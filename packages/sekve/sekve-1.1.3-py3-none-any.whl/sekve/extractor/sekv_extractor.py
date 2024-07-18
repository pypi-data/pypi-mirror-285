import logging
import numpy as np
from numpy import ndarray
from matplotlib import pyplot as plt
from scipy.signal import savgol_filter, find_peaks
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy.stats import linregress
from collections import namedtuple
import time
import pandas as pd
from sekve.model import sEKVModel
from sekve.extractor.ss_extractor import extract_ss, extract_ss_cryo
from sekve.extractor.gds_extractor import extract_Gds
from sekve.utils import get_savgol_win_num

log = logging.getLogger(__name__)


class Base(sEKVModel):
    _progress_figsize = (7, 5)
    _final_figsize = (4, 3)
    _output_figsize = (6, 3)

    def __init__(self, vg: ndarray, i: ndarray, vd: float,
                 width: float = None, length: float = None,
                 temp=300., vs=0.):
        super().__init__(i=i, temp=temp, vs=vs)
        self._VG = vg
        self._W = width
        self._L = length
        self._VD = vd
        self._VG_m = None  # modeled VG

        self._Gm = self.cal_Gm(i=self.ID, vg=self.VG)
        self._Gm_over_ID = self.cal_Gm_over_ID(i=self.ID, vg=self.VG)
        self._n_values = self.cal_n(i=self.ID, vg=self.VG, temp=self.T)
        self._gDS = None

    @property
    def W(self):
        return self._W

    @property
    def L(self):
        return self._L

    @property
    def VG(self):
        return self._VG

    @property
    def VG_m(self):
        return self._VG_m

    @property
    def VD(self):
        return self._VD

    @property
    def VDS(self):
        return self.VD - self.VS

    @property
    def Gm(self):
        return self._Gm

    @property
    def Gm_over_ID(self):
        return self._Gm_over_ID

    @property
    def n_values(self):
        return self._n_values

    @classmethod
    def set_progress_figsize(cls, figsize: tuple):
        cls._progress_figsize = figsize

    @classmethod
    def set_final_figsize(cls, figsize: tuple):
        cls._final_figsize = figsize

    @staticmethod
    def cal_Gm(i: ndarray, vg: ndarray) -> ndarray:
        """Calculate transconductance."""
        return np.gradient(i, vg)

    @staticmethod
    def cal_Gm_over_ID(i: ndarray, vg: ndarray) -> ndarray:
        """Calculate transconductance efficiency."""
        ln_id = np.log(i)
        return np.gradient(ln_id, vg)

    @staticmethod
    def cal_n(i: ndarray, vg: ndarray, temp: float):
        ut = sEKVModel.get_thermal_voltage(temp)
        ln_id = np.log(i)
        one_over_n = np.gradient(ln_id, vg) * ut
        return 1./one_over_n

    def show(self):
        self.progress_fig.tight_layout(pad=0.1)
        self.progress_fig.show()
        self.final_fig.tight_layout(pad=0.1)
        self.final_fig.show()

    def save_data(self, output_path: str):
        """Save result into csv file"""
        d = dict(data_vg=self.VG, data_id=self.ID,
                 model_vg=self.VG_m, ic=self.ID / self.Ispec)
        df = pd.DataFrame(d)
        df_csv = df.to_csv(index=False, line_terminator="\n")
        with open(output_path, "w") as file:
            file.write(self.readable_ekv4params)
            file.write("\r\n")
            file.write(df_csv)


class Params(Base):
    _bbox_style = dict(boxstyle='round', facecolor='white', alpha=0.7)

    def __init__(self, vg: ndarray, i: ndarray, vd: float, *args, **kwargs):
        super().__init__(vg, i, vd, *args, **kwargs)

        # parameters for `_get_Gm_peak`.
        self._savgol_frac_max_Gm = 0.2
        self._savgol_polyorder_max_Gm = 2
        self._find_peak_width = 0.2 * len(self.ID)
        self._offset_vg = 0.05

        # parameters for `_extract_Ispec`.
        self._n_slope_limit = None
        self._savgol_frac_Ispec = 0.2
        self._savgol_polyorder_Ispec = 2
        self._slope_threshold = 0.7

        # parameters for `_extract_Ispec_and_lambdac`.
        self._initial_lambdac = 0.2
        self._ignore_lambdac_threshold = 1e-3

        # parameters for `_extract_Vt0`
        self._initial_vt0 = 0.2

        # parameters for `_refine_Ispec_and_lambdac`
        self._Vt0_offset = 0.

        # parameters for subthreshold slope extraction
        self._ss_kwargs = dict(frac=0.1, take_val="min")

        # parameters for plotting
        self._insert_ax_loc = [0.1, 0.12, 0.5, 0.4]

    # TODO: add setters


class Extractor(Params):
    """Extracting simplified EKV parameters from transfer and output characteristics."""
    def __init__(self, vg: ndarray, i: ndarray, vd: float, vs: float = 0.,
                 width: float = None, length: float = None, temp: float = 300.,
                 remove_mobility_reduction=True, vth_tol=0.02, n_ext_method='ss',
                 force_lambdac_0=False, opt_method="trf", no_refine=False,
                 transconductance_cleanning=False
                 ):
        """ An automated extractor for sEKV MOSFET model.

        Parameters
        ----------
        vg: numpy.ndarray
            A sequence of gate voltage. Please note that it is the gate-to-source voltage for nMOS and
            source-to-gate voltage for pMOS.
        i: numpy.ndarray
            A sequence of drain current. Please note that it is the drain-to-source current for nMOS and
            source-to-drain current for pMOS.
        vd: float
            Drain-to-bulk voltage for nMOS and source-to-bulk voltage for pMOS.
        vs: float
            Source-to-bulk voltage for nMOS and bulk-to-source voltage for pMOS.
        width: float, optional
            Device width in meter.
        length: float, optional
            Device length in meter.
        temp: float, optional
            Ambient temperature in Kelvin.
        remove_mobility_reduction: bool, optional
            If True, the data point suffering the mobility reduction is filter out.
        vth_tol: float, optional
            A tolerance in Volt when extractor re-tunes the `Ispec` from the subthreshold regime. If
            data points in subthreshold regime are sufficient, clean, and reasonably linear, you could set `vth_tol=0`.
        n_ext_method: {"ss", "ss_general"}, optional
            Method extracting subthreshold swing:

                * 'ss' (default): the old method validated only at room temperature.
                * 'ss_general': the new method validated at various temperature.
                This method requires `width` and `length`.

        force_lambdac_0: bool, optional
            If True, force `lambdac=0`.
        opt_method: {'trf', 'dogbox}, optional
            See `scipy.optimize.least_squares` for more information.
        no_refine: bool, optional
            If True, extractor won't re-tune Ispec from subthreshold regime.
        transconductance_cleanning: bool, optional
            If True, the data region having negative transconductance would be filter out.

        Raises
        ------
        ValueError
        IndexError
        """
        vg, i = self._user_cleanup(vg, i, transconductance_cleanning)
        super().__init__(vg, i, vd, width, length, temp, vs)

        self._remove_mobility_reduction = remove_mobility_reduction
        self._vth_tol = vth_tol
        self._n_ext_method = n_ext_method
        self._force_lambdac_0 = force_lambdac_0
        self._opt_method = opt_method
        self._no_refine = no_refine
        self._params_during_process = {}

        self._output_fig = None
        self._final_fig = None
        self._progress_fig = None

        # check
        if self._n_ext_method == "ss_general":
            if self.W is None or self.L is None:
                raise ValueError('Device `width` and `length` should be given, if `n_ext_method="ss_general"`.')

    @staticmethod
    def _user_cleanup(vg: ndarray, i: ndarray, transconductance_cleanning: bool):
        """Cleaning the input values from the user."""
        loc = np.zeros(i.size, dtype=bool)
        for j, _i in enumerate(i[::-1]):
            if _i < 0:
                break
            loc[loc.size-j-1] = True

        vg = vg[loc]
        i = i[loc]

        if transconductance_cleanning:
            grad = np.gradient(i, vg)
            loc = np.zeros(grad.size, dtype=bool)
            for j, grad_v in enumerate(grad[::-1]):
                if grad_v <= 0:
                    break
                loc[loc.size-j-1] = True

            vg = vg[loc]
            i = i[loc]
    
        return vg, i

    def run_extraction(self):
        """Execute the extraction."""
        start = time.time()
        log.info("Start extracting ...")

        self._cleanup()
        self._define_region()
        self._extract_n()
        self._extract_Ispec()
        self._extract_Ispec_and_lambdac()
        self._extract_Vt0()
        if not self._no_refine:
            self._refine_Ispec_and_lambdac()
        self._refine_Vt0()
        end = time.time()
        spent_time = end - start
        log.info(f"Extraction is finished, spent {spent_time} s")

    @property
    def progress_fig(self):
        """Return process result figure."""
        if self._progress_fig is None:
            self._plot_process_figure()
        return self._progress_fig

    @property
    def final_fig(self):
        """Return final result figure."""
        if self._final_fig is None:
            self._plot_final_figure()
        return self._final_fig

    @property
    def output_fig(self):
        """Return output conductance figure."""
        if self._output_fig is None:
            self._plot_output_figure()
        return self._output_fig

    def extract_sigmad_lambdad(self, df: pd.DataFrame,
                               gds_ext_dict: dict = None):

        if self.VDS is None:
            raise ValueError("Drain-to-source voltage 'vds' is not given from class.")
        gds_ext = {
            "method": "deriv",
            "at_vd": self.VDS
        }
        if gds_ext_dict is not None:
            for k, v in gds_ext_dict.items():
                gds_ext[k] = v

        gdss = []
        ics = []
        gms_model = []
        gms_data = []

        for vg, idvd in df.items():
            Gds = extract_Gds(idvd.values, idvd.index.values, **gds_ext)
            gds = Gds / self.Gspec

            x = self.VG
            y = self.ID
            f = interp1d(x, y, fill_value="extrapolate")
            id = f(float(vg))
            ic = id / self.Ispec

            y = self.Gm
            f = interp1d(x, y, fill_value="extrapolate")
            gm = f(float(vg))
            gms_data.append(gm * self.n / self.Gspec)

            gdss.append(gds)
            ics.append(ic)

            # model
            gms_ = self.model_gms(id, self.lambdac, self.Ispec)
            gms_model.append(gms_)

        gdss = np.array(gdss)
        self._gDS = gdss
        ics = np.array(ics)
        gms_model = np.array(gms_model)
        gms_data = np.array(gms_data)

        mk = np.where(ics <= 0.05)
        slope, _, _, _, _ = linregress(gms_data[mk], gdss[mk])
        sigma_d = slope * self._n
        exp_line = ics * sigma_d / self._n
        f = lambda _id, _lambda: self.model_gms(i=_id, lambdac=_lambda, ispec=self.Ispec) * slope
        res = curve_fit(f,
                        xdata=ics * self.Ispec,
                        ydata=gdss,
                        p0=[0.6],
                        loss="linear",
                        bounds=([0], [1]),
                        method='trf')
        lambdad = res[0][0]
        gds_use_lambdac = slope * gms_model
        gds_use_lambdad = slope * self.model_gms(
            i=ics * self.Ispec, lambdac=lambdad, ispec=self.Ispec)
        factor = self._n / (sigma_d * ics)

        # store the parameters
        self._params_during_process['output'] = {
            'ics': ics,
            'gdss': gdss,
            'exp_line': exp_line,
            'factor': factor,
            'gds_use_lambdac': gds_use_lambdac,
            'gds_use_lambdad': gds_use_lambdad,
        }

        self.lambdad = lambdad
        self.sigmad = sigma_d

    def _get_Gm_peak(self, show=False):
        """Get peak Gm."""
        log_gm = np.log(self.Gm)
        non_nan = ~np.isnan(log_gm)
        non_nan_gm = log_gm[non_nan]
        vg = self.VG[non_nan]
        id = self.ID[non_nan]

        win = get_savgol_win_num(data_len=len(self.ID), frac=self._savgol_frac_max_Gm)
        gm_smooth = savgol_filter(non_nan_gm, win, self._savgol_polyorder_max_Gm)
        peaks_loc, _ = find_peaks(gm_smooth, width=self._find_peak_width)

        if len(peaks_loc) == 1:
            peak_loc = peaks_loc[0]
        elif len(peaks_loc) > 1:
            peak_loc = peaks_loc[-1]
        else:
            peak_loc = np.where(gm_smooth == max(gm_smooth))

        peak = np.exp(gm_smooth[peak_loc])
        gm_smooth = np.exp(gm_smooth)
        Out = namedtuple("Out", "peak smoothed_gm vg id crit_vg")
        out = Out(peak=float(peak), smoothed_gm=gm_smooth, vg=vg, id=id, crit_vg=vg[peak_loc])

        if show:
            plt.plot(vg, gm_smooth, "--", label="smooth $G_m$")
            plt.plot(self.VG, self.ID, "-", label="$I_D$")
            plt.plot(self.VG, self.Gm, "+", label="$G_m$")
            plt.axvline(x=out.crit_vg)
            plt.axhline(y=out.peak)
            plt.show()

        return out

    def _cleanup(self):
        """Remove the noisy data and redefine the data range, starting from Ioff."""
        log_id = np.log10(self.ID)
        diff_log_id = np.gradient(log_id, self.VG)
        loc = np.where((~np.isnan(diff_log_id))
                       & (diff_log_id > 0))
        origin_num = len(self.ID)
        self._ID = self._ID[loc]
        self._VG = self._VG[loc]
        self._n_values = self._n_values[loc]
        self._Gm = self._Gm[loc]
        self._Gm_over_ID = self._Gm_over_ID[loc]

        argmin = np.argmin(self.ID)
        loc = slice(argmin, None)
        self._ID = self._ID[loc]
        self._VG = self._VG[loc]
        self._n_values = self._n_values[loc]
        self._Gm = self._Gm[loc]
        self._Gm_over_ID = self._Gm_over_ID[loc]
        new_num = len(self.ID)
        log.info(f"The Id-Vg data is redefined by removing the noise data "
                 f"and accumulation region. Data points is reduced from "
                 f"{origin_num} to {new_num}.")

    def _define_region(self):
        """define the data region for extraction."""
        if self._remove_mobility_reduction:
            peak_gm_inf = self._get_Gm_peak()
            crti_vg = peak_gm_inf.crit_vg
            crti_vg_loc = np.where(self.VG > (crti_vg + self._offset_vg))
            try:
                stop = crti_vg_loc[0][0]
            except IndexError:
                loc = slice(0, None)
            else:
                loc = slice(0, stop)
        else:
            loc = slice(0, None)

        if loc != slice(0, None):
            origin_num = len(self.ID)
            self._ID = self._ID[loc]
            self._VG = self._VG[loc]
            self._n_values = self._n_values[loc]
            self._Gm = self._Gm[loc]
            self._Gm_over_ID = self._Gm_over_ID[loc]
            new_num = len(self.ID)
            log.info(f"The Id-Vg data is redefined by removing the "
                     f"region having mobility reduction due to vertical field. "
                     f"Data points is reduced from {origin_num} to {new_num}.")

        return loc

    def _extract_n(self):
        if self._n_ext_method in ["ss", "ss_general"]:
            if self._n_ext_method == "ss":
                ss, vc = extract_ss(
                    v=self.VG, i=self.ID, t=self.T,
                    return_crit_v=True, **self._ss_kwargs)
            else:
                ss = extract_ss_cryo(
                    v=self.VG, i=self.ID, t=self.T, w=self.W, l=self.L,
                    **self._ss_kwargs)
    
            ss /= 1e3  # mV/dec -> V/dec
            n = ss / (self.Ut * np.log(10))
            self.n = n
            log.info(f"The `n` is extracted with the value of {n}")
        else:
            raise ValueError("The n extracting method {} is not recognized.".format(self._n_ext_method))

    def _extract_Ispec(self):
        """Extract specific current."""
        slp = np.gradient(np.log(self._n_values), np.log(self.ID))
        loc = ~np.isnan(slp)
        win = get_savgol_win_num(data_len=len(self.ID[loc]), frac=self._savgol_frac_Ispec)
        _y = savgol_filter(slp[loc], win, self._savgol_polyorder_Ispec)
        _x = self.ID[loc]

        if self._n_slope_limit is None:
            self._n_slope_limit = 0.5 if max(_y) < self._slope_threshold else 1.

        diff = (_y - self._n_slope_limit) ** 2
        diff = savgol_filter(diff, window_length=win,
                             polyorder=self._savgol_polyorder_Ispec)
        diff = abs(diff)
        func = lambda ids, ids_c, n_c: self._n_slope_limit * (np.log10(ids) - np.log10(ids_c)) + np.log10(n_c)
        _id = _x[np.where(diff == np.nanmin(diff))]
        loc_exp = np.where(self.ID == _id)
        new_y = 10 ** (func(self.ID, self.ID[loc_exp], self._n_values[loc_exp]))
        f = interp1d(new_y, self.ID)
        ispec = f(self._n)
        self.Ispec = float(ispec)

        # storing parameters for plotting
        self._params_during_process['a'] = {
            'ispec_asymptote': new_y,
            'ispec': ispec,
            'n': float(self.n)
        }
        log.info("The `Ispec` is extracted with the value of %.3e A" % ispec)

    def _extract_Ispec_and_lambdac(self):
        """Get lambdac and specific current via optimizer."""

        GmnUt_id = self.Gm_over_ID * self.Ut * self.n
        if self._force_lambdac_0:
            fit_func = lambda _id, _ispec: sEKVModel.model_gms_over_IC_vs_IC(
                i=_id, lambdac=0., ispec=self.Ispec
            )
            res = curve_fit(fit_func,
                            xdata=self.ID,
                            ydata=GmnUt_id,
                            p0=[self.Ispec],
                            loss='cauchy',
                            f_scale=0.01,
                            bounds=([0], [np.inf]),
                            method=self._opt_method
                            )
            ispec = res[0][0]
            self.Ispec = ispec
            lambdac = 0.
        else:
            fit_func = sEKVModel.model_gms_over_IC_vs_IC
            res = curve_fit(fit_func,
                            xdata=self.ID,
                            ydata=GmnUt_id,
                            p0=[self._initial_lambdac, self.Ispec],
                            loss='cauchy',
                            f_scale=0.01,
                            bounds=([0.0, 0], [1, np.inf]),
                            method=self._opt_method
                            )
            lambdac, ispec = res[0]
        self.lambdac = lambdac
        self.Ispec = ispec
        log.info("The `Ispec` is extracted with the value of %.3e A." % ispec)

        if lambdac < self._ignore_lambdac_threshold:
            self._force_lambdac_0 = True
            self.lambdac = 0.
            log.info("The `lambdac` is extracted with the value of %.3f." % lambdac)

        # storing parameters for plotting
        self._params_during_process['b'] = {
            'ispec': ispec,
            'meas': GmnUt_id,
            'model': sEKVModel.model_gms_over_IC_vs_IC(self.ID, self.lambdac, self.Ispec),
            'lambdac': lambdac
        }

    def _extract_Vt0(self):
        if self._force_lambdac_0:
            f = lambda _id, _ispec, _vt0:\
                sEKVModel.model_ID_vs_VG(_id, n=self._n, ispec=_ispec,
                                         lambdac=0.0, vt0=_vt0, temperature=self.T)
            res = curve_fit(f,
                            xdata=self.ID,
                            ydata=self.VG,
                            p0=[self.Ispec, self._initial_vt0],
                            bounds=([0.0, -np.inf], [np.inf, np.inf]),
                            method=self._opt_method
                            )
            lambdac = 0.0
            ispec, vt0 = res[0]
        else:
            f = lambda _id, _ispec, _lc, _vt0:\
                sEKVModel.model_ID_vs_VG(_id, n=self._n, ispec=_ispec,
                                         lambdac=_lc, vt0=_vt0, temperature=self.T)
            res = curve_fit(f,
                            xdata=self.ID,
                            ydata=self.VG,
                            p0=[self.Ispec, self.lambdac, self._initial_vt0],
                            bounds=([0.0, 0.0, -np.inf], [np.inf, 1.0, np.inf]),
                            method=self._opt_method
                            )
            ispec, lambdac, vt0 = res[0]
        self.Ispec = ispec
        self.lambdac = lambdac
        self.Vt0 = vt0
        log.info("The `Ispec`, `lambdac`, and `Vt0` have been optimized "
                 "with the value of %.3e A, %.3f, %.3f V." % (self.Ispec, self.lambdac, self.Vt0))
        self._VG_m = self.get_sim_VG()

        # storing parameters for plotting
        self._params_during_process['c'] = {
            'VG_m': self.VG_m.copy(),
            'text': self.readable_ekv4params
        }

    def _get_bound_of_Ispec_range(self, vth_tol: float, intercept: float):

        vth_dev = vth_tol / (self.n * self.Ut)
        up_it = intercept + abs(vth_dev)
        down_it = intercept - abs(vth_dev)

        up_ispec = np.exp(up_it) * self.n * self.Ut
        down_ispec = np.exp(down_it) * self.n * self.Ut

        return up_ispec, down_ispec

    def _refine_Ispec_and_lambdac(self):
        region = np.where(self.VG < (self._Vt0 - self._Vt0_offset))
        vg_minus_vt0 = self.VG[region] - self.Vt0
        Gm = self.Gm[region]
        c = 1.0 / (self._n * self.Ut)
        y = np.log(Gm)

        intercept = np.nanmean(y - c * vg_minus_vt0)
        ispec = np.exp(intercept) / c
        self.Ispec = ispec
        ispec1 = ispec
        log.info('The `Ispec` is re-extracted from the subthreshold region with '
                 'the value of %.3e A' % self.Ispec)
        fit_y = c * vg_minus_vt0 + intercept

        GmnUt_id = self.Gm_over_ID * self.Ut * self._n

        # re-optimize lambdac
        if self._force_lambdac_0:
            self.lambdac = 0.
            if self._vth_tol > 0.0:
                up_ispec, down_ispec = self._get_bound_of_Ispec_range(
                    vth_tol=self._vth_tol, intercept=float(intercept))
                fit_func = lambda _id, _ispec: sEKVModel.model_gms_over_IC_vs_IC(
                    _id, lambdac=0.0, ispec=_ispec)
                res = curve_fit(fit_func,
                                xdata=self.ID,
                                ydata=GmnUt_id,
                                p0=[self.Ispec],
                                loss='cauchy',
                                f_scale=0.01,
                                bounds=([down_ispec], [up_ispec]),
                                method=self._opt_method)
                ispec = res[0][0]
                self.Ispec = ispec
                log.info("The `Ispec` is re-optimized, resulting in %.3e A" % self.Ispec)
        else:
            x, y = self.ID, GmnUt_id
            x = x[~np.isnan(y)]
            y = y[~np.isnan(y)]
            if self._vth_tol > 0.0:
                up_ispec, down_ispec = self._get_bound_of_Ispec_range(
                    vth_tol=self._vth_tol, intercept=float(intercept))
                fit_func = lambda _id, _lc, _ispec: sEKVModel.model_gms_over_IC_vs_IC(
                    _id, _lc, _ispec)
                res = curve_fit(fit_func,
                                xdata=x,
                                ydata=y,
                                p0=[self.lambdac, self.Ispec],
                                loss='cauchy',
                                f_scale=0.02,
                                bounds=([0.0, down_ispec], [1.0, up_ispec]),
                                method=self._opt_method)
                lambdac, ispec = res[0]
                self.Ispec = ispec
                self.lambdac = lambdac
                log.info("The `Ispec` is re-optimized, resulting in %.3e A" % self.Ispec)
                log.info("The `lambdac` is re-optimized, resulting in %.3f " % self.lambdac)

            elif self._vth_tol == 0.0:
                fit_func = lambda _id, _lc: sEKVModel.model_gms_over_IC_vs_IC(_id, _lc, ispec=ispec)
                res = curve_fit(fit_func,
                                xdata=x,
                                ydata=y,
                                p0=[self._lambdac],
                                loss='cauchy',
                                f_scale=0.02,
                                bounds=([0.0], [1.0]),
                                method=self._opt_method)
                lambdac = res[0][0]
                self.lambdac = lambdac
                log.info("The `lambdac` is re-optimized, resulting in %.3f " % self.lambdac)
            else:
                raise ValueError("Tolerance of threshold voltage must be larger than or equal to 0, instead of {}".format(
                    self._vth_tol))

        # storing parameters for plotting
        self._params_during_process['d'] = {
            'vg_minus_vt0': vg_minus_vt0,
            'fit_y': fit_y,
            'y': np.log(Gm),
            'ispec1': ispec1,
            'lambdac': float(self.lambdac),
            'ispec2': float(self.Ispec),
            'GmnUt_id': GmnUt_id,
            'model': sEKVModel.model_gms_over_IC_vs_IC(self.ID, self.lambdac, self.Ispec)
        }

    def _refine_Vt0(self):

        f = lambda _id, _vt0: sEKVModel.model_ID_vs_VG(
            _id, n=self._n, ispec=self.Ispec, lambdac=self.lambdac, vt0=_vt0, temperature=self.T)
        res = curve_fit(f,
                        xdata=self.ID,
                        ydata=self.VG,
                        p0=[self.Vt0],
                        bounds=([-np.inf], [np.inf]),
                        method=self._opt_method
                        )
        vt0 = res[0]
        self.Vt0 = float(vt0)
        self._VG_m = self.get_sim_VG()
        log.info('The `Vt0` is re-optimized in the final step with the value of %.3f V' % self.Vt0)

    def _plot_final_figure(self):
        """Plot figure showing the final result."""
        self._final_fig = plt.figure(figsize=self.__class__._final_figsize)
        ax = self.final_fig.add_subplot(111)
        ln1 = ax.semilogy(self.VG, self.ID, 'ro', mfc="none", label='Data (log)')
        ln2 = ax.semilogy(self.VG_m, self.ID, 'k--', label='sEKV')
        ax.set_xlabel('$V_{G}$ [V]')
        ax.set_ylabel('$I_D$ [A]')

        if self.VDS is not None:
            vds_txt = '\n|$V_{DS}$| = %.2f V' % self.VDS
        else:
            vds_txt = ''
        txt = self.readable_ekv4params + vds_txt
        ax.text(0.03, 0.97, txt,
                transform=ax.transAxes,
                ha='left', va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        ax2 = ax.twinx()
        ln3 = ax2.plot(self.VG, self.ID, 'r>', mfc="none", label="Data (linear)")
        ax2.plot(self.VG_m, self.ID, 'k--')

        lns = ln1 + ln3 + ln2
        labs = [l.get_label() for l in lns]
        ax.legend(lns, labs, loc=4)
        ax2.set_ylabel('$I_D$ [A]')

        self._final_fig.tight_layout()

    def _plot_process_figure(self):
        """Plot figure showing the extraction process"""
        # Ispec and n
        self._progress_fig = plt.figure(figsize=self.__class__._progress_figsize)
        params = self._params_during_process['a']
        ax = self.progress_fig.add_subplot(221)
        ax.set_title("(a)", x=-0.1, y=-0.2)
        ax.loglog(self.ID, self._n_values, 'ro', label='Data')
        ax.axhline(y=params['n'], color='k', linestyle='--', marker="None")
        ax.loglog(self.ID, params['ispec_asymptote'], color="k")
        ax.axvline(x=params['ispec'], color='k', linestyle='--', marker='None')
        ax.text(0.03, 0.05, 'n = %.3f' % self._n, transform=ax.transAxes,
                ha="left", va="bottom",
                bbox=self.__class__._bbox_style)
        ax.text(0.97, 0.95, '$I_{spec}$=%.2e [A]' % params['ispec'], transform=ax.transAxes,
                ha="right", va="top",
                bbox=self.__class__._bbox_style)
        ax.set_ylabel('n = $I_D$ / ($G_mU_T$) [-]')
        ax.set_xlabel('$I_D$ [A]')
        ax.set_ylim(0.1, None)
        ax.legend(loc=2)

        # lambdac and Ispec
        params = self._params_during_process['b']
        ax = self.progress_fig.add_subplot(222)
        ax.set_title("(b)", x=-0.1, y=-0.2)
        ax.loglog(self.ID / params['ispec'], params['meas'], 'ro', label='Data')
        ax.loglog(self.ID / params['ispec'], params['model'], 'k--', label='sEKV')
        ax.text(0.03, 0.03,
                '$\lambda_c$ = %.3f \n$I_{spec}$ = %.3e [A]' % (params['lambdac'], params['ispec']),
                transform=ax.transAxes, ha='left', va='bottom',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
        ax.set_xlabel('IC [-]')
        ax.set_ylabel('$G_mnU_T$ / $I_D$ [-]')
        ax.set_ylim(1e-2, 10)
        ax.legend(loc=1)

        # Vth0
        params = self._params_during_process['c']
        ax = self.progress_fig.add_subplot(223)
        ax.set_title("(c)", x=-0.1, y=-0.2)
        ax2 = ax.twinx()
        ln1 = ax.semilogy(self.VG, self.ID, 'ro', label='Data (log)')
        ln2 = ax2.plot(self.VG, self.ID, 'r>', label='Data (linear)')
        ln3 = ax.semilogy(params['VG_m'], self.ID, 'k--', label='EKV')
        ax.set_xlabel('$V_{G}$ [V]')
        ax.set_ylabel('$I_D$ [A]')

        ax.text(0.95, 0.05, params['text'],
                transform=ax.transAxes, ha='right', va='bottom',
                bbox=self.__class__._bbox_style)
        ax2.plot(params['VG_m'], self.ID, 'k--')
        lns = ln1 + ln2 + ln3
        labs = [l.get_label() for l in lns]
        ax.legend(lns, labs, loc=2)
        ax2.set_ylabel('$I_D$ [A]')

        # Gmnut
        params = self._params_during_process['d']
        ax = self.progress_fig.add_subplot(224)
        ax.set_title("(d)", x=-0.1, y=-0.2)
        axs_loc = self._insert_ax_loc
        axs = ax.inset_axes(axs_loc)
        axs.plot(params['vg_minus_vt0'], params['y'], 'ro')
        axs.plot(params['vg_minus_vt0'], params['fit_y'], 'k--', label='Fit with fixed slope')
        axs.text(0.95, 0.05, '$I_{spec}$ = %.3e [A]' % params['ispec1'],
                 ha="right", va="bottom",
                 transform=axs.transAxes,
                 # bbox=self.__class__._bbox_style,
                 fontsize=6)
        axs.set_xlabel('$V_{G}$-$V_{T0}$ [V]', fontsize=6)
        axs.set_ylabel('$ln$ $G_m$', fontsize=6)
        axs.set_xticks([])
        axs.set_yticks([])

        ax.loglog(self.IC, params['GmnUt_id'], 'ro', label='Data')
        ax.loglog(self.IC, params['model'],
                  'k--', label='sEKV')
        ax.text(0.03, 0.97,
                '$\lambda_c$ = %.3f \n$I_{spec}$ = %.3e' % (params['lambdac'], params['ispec2']),
                transform=ax.transAxes, bbox=self._bbox_style,
                ha='left', va='top'
                )
        ax.set_xlabel('$IC$ [-]')
        ax.set_ylabel('$G_m$n$U_T$ / $I_D$')
        ax.set_ylim(1e-2, 1e1)
        ax.legend(loc=1)
        self._progress_fig.tight_layout()

    def _plot_output_figure(self):
        """PLot figure showing the output conductance modeling result"""
        self._output_fig = plt.figure(figsize=self.__class__._output_figsize)
        ax1 = self._output_fig.add_subplot(121)
        ax2 = self._output_fig.add_subplot(122)

        params = self._params_during_process['output']
        ax1.loglog(params['ics'], params['gdss'], marker="o", ls="", mfc="none", color="k", label="data")
        ax1.loglog(params['ics'], params['exp_line'], "r-", label="Ext. of $\sigma_d$")
        ax1.grid(axis="both", which="major", ls="-", alpha=0.5)
        ax1.grid(axis="both", which="minor", ls="--", alpha=0.5)
        ax1.set_xlabel("$IC$")
        ax1.set_ylabel("$g_{DS}$")
        ax1.legend(loc=0)

        ax2.loglog(params['ics'], params['gdss'] * params['factor'],
                   marker="o", ls="", color="k", label="data", mfc="none")
        ax2.loglog(params['ics'], params['gds_use_lambdac'] * params['factor'],
                   ls="-", color="r", label="$\lambda_d$ = $\lambda_c$")
        ax2.loglog(params['ics'], params['gds_use_lambdad'] * params['factor'],
                   ls="-", color="b", label="optimzed $\lambda_d$")
        ax2.grid(axis="both", which="major", ls="-", alpha=0.5)
        ax2.grid(axis="both", which="minor", ls="--", alpha=0.5)
        s = [
            "n = %.2f" % self.n,
            "$\sigma_d$ = %.3f" % self.sigmad,
            "$\lambda_c$ = %.3f" % self.lambdac,
            "$\lambda_d$ = %.3f" % self.lambdad,
        ]
        ax2.text(x=0.03, y=0.03, s="\n".join(s), va="bottom", ha="left",
                 transform=ax2.transAxes)
        ax2.set_xlabel("IC")
        ax2.set_ylabel("$ng_{DS}$/$\sigma_dIC$")
        ax2.legend(loc=4)

        self._output_fig.tight_layout()
