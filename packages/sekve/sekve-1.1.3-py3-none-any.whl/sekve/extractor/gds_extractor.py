import numpy as np
from typing import Union
from scipy.stats import linregress
from scipy.signal import savgol_filter
from matplotlib import pyplot as plt


def extract_Gds(
        i: np.ndarray,
        v: np.ndarray,
        method: str = "auto",
        bins: Union[str, int] = "auto",
        region: Union[None, tuple] = None,  # (0.7, 0.8)
        at_vd: Union[None, float] = None,
        show=False) -> float:
    """ Extract Gds.

    :param i: drain current.
    :param v: drain voltage.
    :param method: ["auto", "region", "deriv"]
    :param region: selected data for calculating Gds, defined by drain voltage.
    :param at_vd: get Gds from given vds point.
    :param bins: number of bin for histogram.
    :param show: show extraction.

    """
    if region is not None:
        method = "manual"
    if (region is None) and (at_vd is not None):
        method = "deriv"

    intercept = None
    if method == "auto":
        did = np.gradient(i, v)
        count, interval = np.histogram(did[~np.isnan(did)], bins=bins)
        max_c = int(np.where(count == max(count))[0][0])
        low_b, up_b = interval[max_c:max_c+2]
        loc = np.where((low_b <= did) & (did <= up_b))
        slope, intercept, _, _, _ = linregress(v[loc], i[loc])
    elif method == "manual":
        if isinstance(region, tuple):
            low_b, up_b = region
            loc = np.where((low_b <= v) & (v <= up_b))
            slope, intercept, _, _, _ = linregress(v[loc], i[loc])
        else:
            raise ValueError("Region is not given or object type is wrong.")
    elif method == "deriv":
        gds = np.gradient(i, v)
        win = len(i) // 4
        if not win % 2:
            win += 1
        filter_gds = savgol_filter(gds, window_length=win, polyorder=2,
                                   mode="mirror")
        if at_vd is None:
            raise ValueError("'at_vd' is not given for 'deriv' method.")
        slope = filter_gds[np.where(abs(v-at_vd) == min(abs(v-at_vd)))][0]
    else:
        raise ValueError("Method '%s' is not supported" % method)

    if show:
        ax = plt.gca()
        ax.set_xlabel("$|V_{DS}|$ (V)")
        ax.set_ylabel("$|I_{DS}|$ (A)")
        ax.plot(v, i, color="k", ls="", marker="o", mfc="none")

        if method in ["manual", "auto"]:
            ax.axvline(low_b, linestyle="--", color="k")
            ax.axvline(up_b, linestyle="--", color="k")
            y = slope * v + intercept
            ax.plot(v, y, "r-")
        elif method == "deriv":
            axt = ax.twinx()
            axt.plot(v, gds*1e3, "b--", label="$G_{DS}$")
            axt.plot(v, filter_gds*1e3, "r--", label="smoothed $G_{DS}$")
            axt.set_ylabel("$G_{ds}$ (mS)")
            y = slope * (v-at_vd) + i[np.where(abs(v-at_vd) == min(abs(v-at_vd)))][0]
            ax.plot(v, y, "r-")
        _s = slope * 1e3
        ax.text(0.5, 0.4,
                f"Method: '{method}'\n" +
                r"$G_{DS}$ = %.2f mS" % _s,
                transform=ax.transAxes, va="bottom", ha="center")
        plt.show()
    return slope
