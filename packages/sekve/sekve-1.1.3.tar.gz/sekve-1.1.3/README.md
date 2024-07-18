# SEKV-E

SEKV-E is a Python-based parameters extractor for the simplified EKV model,
which is developed by ICLAB, EPFL.
While it has been developed to serve the needs of low-power analog circuit designs.
The source file is controlled on our GitLab repo at [SEKV-E](https://gitlab.com/moscm/sekv-e).

You can find the tutorial at [15_minutes_to_sekve](https://gitlab.com/moscm/sekv-e/-/blob/main/docs/examples/15_minutes_to_sekve.ipynb).
Please find our recent [published paper](https://doi.org/10.1109/OJCAS.2022.3179046) for more information about 
the extraction methodology and applications.

## Install

The project is present on `pip` and `conda-forge`.

### Conda

To get the package in your `conda` environment:

```console
conda install -c conda-forge sekve
```

### PyPI

To install the project via `pip`:

```console
pip install sekve
```

### Git

To clone directly the project in your local directory:

```console
git clone https://gitlab.com/moscm/sekv-e.git
```

## Authors and acknowledgment

Hung-Chi Han, doctoral assistant in ICLAB, EPFL, Lausanne, Switzerland
(email:[hung.han@epfl.ch](mailto:hung.han@epfl.ch)).<br/>
Vicente Carbon, master student in ICLAB, EPFL, Lausanne, Switzerland.<br/>
Christian Enz, director of ICLAB, EPFL, Lausanne, Switzerland.

## Paper

If you use SEKV-E in your research, please cite the paper

H. -C. Han, A. D’Amico and C. Enz, "SEKV-E: Parameter Extractor of Simplified EKV I-V Model for Low-Power Analog Circuits," in IEEE Open Journal of Circuits and Systems, vol. 3, pp. 162-167, 2022, doi: [10.1109/OJCAS.2022.3179046](https://doi.org/10.1109/OJCAS.2022.3179046).

## License

see [LICENSE](LICENSE).


## Tutorials

* [15_minutes_to_sekve](https://gitlab.com/moscm/sekv-e/-/blob/main/docs/examples/15_minutes_to_sekve.ipynb),<br/>
which gives you a general introduction to SEKV-E. You will learn how to manage your input
data, how to run the extraction, and how to get the extracted parameters.