"""Plotter tools."""

import pathlib
import sys

import matplotlib.pyplot as plt
from colorama import Fore, Style

import nvtools
from nvtools.fit.odmr_model import ModelVoigt8
from nvtools.solver import Solver
from nvtools.utils import success


class ODMRPlotter:
    """ODMR plotter."""

    @staticmethod
    def plot_from_spectrum(mw_frequency, odmr, figsize="small", p0_frequency=None):
        """
        Plot ODMR spectrum.

        :param npt.NDArray mw_frequency: MW frequency in MHz
        :param npt.NDArray odmr: ODMR data
        :param str | list figsize: figure size in inches. Use "small" or "large" for default settings.
        :param list | None p0_frequency: estimates for resonance frequencies
        :returns: Fit parameters and B-field
        """
        if figsize == "small":
            figsize = [4, 2.5]
        elif figsize == "large":
            figsize = [8, 5]

        solver = Solver()
        fit_params, b_field = solver.field_from_spectrum(mw_frequency, odmr, p0_frequency=p0_frequency)

        if nvtools.LATEX:
            plt.rc("figure", figsize=figsize)
            plt.rc("text", usetex=True)
            plt.rc("font", family="serif", size=10)
            plt.rcParams["text.latex.preamble"] = "\n".join(
                [
                    r"\usepackage[utf8]{inputenc}",
                    r"\usepackage[T1]{fontenc}",
                    r"\usepackage[detect-all]{siunitx}",
                ]
            )

        if nvtools.VERBOSE:
            print(
                Fore.GREEN
                + Style.BRIGHT
                + "───────────────────────── ODMR Plotter ─────────────────────────"
                + Style.RESET_ALL
            )

        plt.figure()
        plt.plot(mw_frequency, odmr * 100)
        plt.plot(mw_frequency, ModelVoigt8.f(mw_frequency, *fit_params.popt) * 100, color="tab:red")
        if nvtools.LATEX:
            plt.xlabel(r"MW frequency (MHz)")
            plt.ylabel(r"Contrast (\SI{}{\percent})")
        else:
            plt.xlabel("MW frequency (MHz)")
            plt.ylabel("Contrast (%)")
        plt.tight_layout()
        if nvtools.EXPORT:
            folder = pathlib.Path(sys.argv[0]).parent
            file_path = pathlib.Path(folder, "odmr_plot.png")
            success(f"saving ODMR plot in {file_path}")
            print("\n")
            plt.savefig(file_path, dpi=500)
        elif nvtools.SHOW_PLOTS:
            plt.show()

        return fit_params, b_field
