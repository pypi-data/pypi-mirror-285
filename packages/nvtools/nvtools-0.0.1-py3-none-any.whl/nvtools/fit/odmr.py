r"""
ODMR fitting tools.

Tries to automatically guess starting parameters.

Usage
^^^^^

Fit an ODMR spectrum with eight resonances

.. code-block:: python

   from nvtools.fit.odmr import ODMRFitter

   fitter = ODMRFitter()
   fit_results = fitter.fit_odmr_8(mw_frequency, odmr)

   print(fit_results)
"""

import pathlib
import sys
from dataclasses import dataclass
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
import scipy
from colorama import Fore, Style
from prettytable import SINGLE_BORDER, PrettyTable

import nvtools.fit
from nvtools import unit
from nvtools.fit.odmr_model import ModelVoigt1, ModelVoigt8
from nvtools.utils import critical, success


@dataclass
class ODMRFitResult:
    """ODMR fit results."""

    mw_frequency: list
    odmr: list
    popt: list
    pcov: list
    perr: list
    model: Callable
    frequency: float | list[float]
    contrast: float | list[float]
    linewidth: float | list[float]

    @property
    def fit_func(self):
        """Fit function values."""
        return self.model(self.mw_frequency, *self.popt)


class ODMRFitter:
    """ODMR fitter."""

    @staticmethod
    def fit_odmr_single(mw_frequency, odmr):
        """
        Fit ODMR with one resonance.

        :param mw_frequency: MW frequency
        :param odmr: ODMR
        """
        ten_mhz_distance = len(mw_frequency) / (np.max(mw_frequency - np.min(mw_frequency))) * 10
        peaks, __ = scipy.signal.find_peaks(-odmr, distance=ten_mhz_distance)
        fit_model = ModelVoigt1()
        popt, pcov = scipy.optimize.curve_fit(
            f=fit_model.f, xdata=mw_frequency, ydata=odmr, p0=[10, 5, 5, mw_frequency[peaks]]
        )
        perr = np.sqrt(np.diag(pcov))

        area = (popt[0] * unit.MHz * unit.MHz).plus_minus(perr[0])
        sigma = (popt[1] * unit.MHz).plus_minus(perr[1])
        nu = (popt[2] * unit.MHz).plus_minus(perr[2])
        frequency = (popt[3] * unit.MHz).plus_minus(perr[3])

        alpha_l, alpha_g, alpha_v, d, contrast = fit_model.voigt_parameters(area, sigma, nu)

        return ODMRFitResult(popt, pcov, perr, frequency, contrast, alpha_v)

    @staticmethod
    def fit_odmr_full(mw_frequency, odmr, p0_frequency=None, units=True):
        """
        Fit ODMR with eight resonances.

        :param mw_frequency: MW frequency
        :param odmr: ODMR
        :param list | None p0_frequency: estimates for resonance frequencies
        :raises: RuntimeError when peaks can not be found
        """
        if p0_frequency is None:
            ten_mhz_distance = len(mw_frequency) / (np.max(mw_frequency - np.min(mw_frequency))) * 10
            one_percent_prominence = (np.max(odmr) - np.min(odmr)) * 0.1
            peaks, __ = scipy.signal.find_peaks(-odmr, distance=ten_mhz_distance, prominence=one_percent_prominence)
            p0_frequency = mw_frequency[peaks]
        else:
            peaks = None

        if len(p0_frequency) != 8:
            peaks_str = ", ".join([f"{x:.2f}" for x in p0_frequency])
            critical("Could not find eight peaks. Try to set the starting parameters manually with 'p0_frequency'.")
            critical(f"Found {len(p0_frequency)} peaks at {peaks_str} MHz")
            print("\n")
            plt.figure()
            plt.plot(mw_frequency, odmr, label="data")
            if peaks is not None:
                plt.plot(p0_frequency, odmr[peaks], "x", label="peak estimates")
            plt.legend(loc="best")
            plt.show()

            raise RuntimeError(
                "Could not find eight peaks. Try to set the starting parameters manually with 'p0_frequency'."
            )

        # c_est = np.max(odmr) - np.min(odmr)
        # print("contrast", c_est)

        areas = np.full(8, 1)
        sigmas = np.full(8, 2)
        nus = np.full(8, 2)
        start_params = np.column_stack((areas, sigmas, nus, p0_frequency)).flatten()
        start_params = np.append(start_params, np.max(odmr))
        if nvtools.ODMR_MODEL is None:
            fit_model = ModelVoigt8()

        # plt.figure()
        # plt.plot(mw_frequency, odmr)
        # plt.plot(mw_frequency, fit_model.f(mw_frequency, *start_params))
        # plt.show()

        popt, pcov = scipy.optimize.curve_fit(f=fit_model.f, xdata=mw_frequency, ydata=odmr, p0=start_params)
        perr = np.sqrt(np.diag(pcov))
        areas, sigmas, nus, frequencies, alpha_ls, alpha_gs, alpha_vs, contrasts = [], [], [], [], [], [], [], []
        for i in range(8):
            if units:
                area = (popt[4 * i + 0] * unit.MHz * unit.MHz).plus_minus(perr[4 * i + 0])
                sigma = (popt[4 * i + 1] * unit.MHz).plus_minus(perr[4 * i + 1])
                nu = (popt[4 * i + 2] * unit.MHz).plus_minus(perr[4 * i + 2])
                frequency = (popt[4 * i + 3] * unit.MHz).plus_minus(perr[4 * i + 3])
            else:
                area = popt[4 * i + 0]
                sigma = popt[4 * i + 1]
                nu = popt[4 * i + 2]
                frequency = popt[4 * i + 3]

            alpha_l, alpha_g, alpha_v, d, c = fit_model.voigt_parameters(area, sigma, nu, units=units)

            areas.append(area)
            sigmas.append(sigma)
            nus.append(nus)
            frequencies.append(frequency)
            alpha_ls.append(alpha_l)
            alpha_gs.append(alpha_g)
            alpha_vs.append(alpha_v)
            contrasts.append(c)

        if nvtools.VERBOSE or nvtools.EXPORT:
            resonance_names = ["lower 1", "lower 2", "lower 3", "lower 4", "upper 4", "upper 3", "upper 2", "upper 1"]
            table = PrettyTable()
            table.set_style(SINGLE_BORDER)
            table.field_names = ["Resonance", "Frequency", "Contrast", "Linewidth"]
            for i in range(8):
                table.add_row(
                    [resonance_names[i], f"{frequencies[i]:~P}", f"{contrasts[i] * 100:.2f} %", f"{alpha_vs[i]:~P}"]
                )
            if nvtools.VERBOSE:
                print(
                    Fore.GREEN
                    + Style.BRIGHT
                    + "───────────────────────── ODMR Fitter ─────────────────────────"
                    + Style.RESET_ALL
                )
                print(table)
                print("\n")
            if nvtools.EXPORT:
                folder = pathlib.Path(sys.argv[0]).parent
                file_path = pathlib.Path(folder, "odmr_fit.csv")
                success(f"saving fit results in {file_path}")
                print("\n")
                with open(file_path, "w") as file:
                    file.write(table.get_csv_string())

        return ODMRFitResult(
            mw_frequency=mw_frequency,
            odmr=odmr,
            popt=popt,
            pcov=pcov,
            perr=perr,
            model=fit_model.f,
            frequency=frequencies,
            contrast=contrasts,
            linewidth=alpha_vs,
        )
