r"""
B-field solver tools.

Tools for solving the NV center hamiltonian

.. math::
    \frac{H}{\hbar} = D_{gs}\left(S_z^2 - \frac{1}{3}S(S+1)\right) + E(S_x^2 - S_y^2) + \gamma_{\text{NV}}\vec{B} \cdot \vec{S}
"""

import itertools
import json
import operator
import pathlib
import sys
from dataclasses import dataclass

import numpy as np
import uncertainties.umath as um
from colorama import Fore, Style
from prettytable import SINGLE_BORDER, PrettyTable
from uncertainties import ufloat

import nvtools
from nvtools import unit
from nvtools.fit.odmr import ODMRFitter
from nvtools.utils import success, warning
from nvtools.vector import Vector


@dataclass
class BField:
    """B-field."""

    b_abs: list[float]
    theta: list[float]
    b_vec: Vector

    def to_dict(self):
        """Format to dict."""
        b_abs_json = [val.to("mT").nominal_value for val in self.b_abs]
        b_abs_err_json = [val.to("mT").std_dev for val in self.b_abs]
        theta_json = [val.to("rad").nominal_value for val in self.theta]
        theta_err_json = [val.to("rad").std_dev for val in self.theta]

        return {
            "b_abs (mT)": b_abs_json,
            "b_abs_err (mT)": b_abs_err_json,
            "theta (rad)": theta_json,
            "theta_err (rad)": theta_err_json,
        }


class Solver:
    """B-field Solver."""

    @staticmethod
    def field_from_resonances(fl, fu):
        r"""
        Calculate absolute field value and angle to NV-axis.

        .. math::
            \mathcal{B}^2 = \frac{1}{3} \left(f_{\text{u}}^2 + f_{\text{l}}^2 - f_{\text{u}}f_{\text{l}} - D^2 - 3E^2\right)

        .. math::
            \cos^2\theta = \frac{2f_{\text{l}}^3-3f_{\text{l}}^2f_{\text{u}}-3f_{\text{l}}f_{\text{u}}^2+2f_{\text{u}}^3}{27(D-E/2)\mathcal{B}^2} + \frac{2D^3 - 18DE^2}{27(D-E/2)\mathcal{B}^2} + \frac{2D-3E}{6(D-E/2)}

        :param fl: lower resonance frequency
        :param fu: upper resonance frequency
        """
        try:
            fl = fl.to("MHz").magnitude
            fu = fu.to("MHz").magnitude
        except AttributeError:
            warning("Input values to 'field_from_resonances(fl, fu)' have no unit. Assuming fl in MHz and fu in MHz.")

        b_squared = (fu**2 + fl**2 - fu * fl - nvtools.D_SPLITTING**2 - 3 * nvtools.E_SPLITTING**2) / 3
        cos_theta_squared = (
            2 * fl**3
            - 3 * fl**2 * fu
            - 3 * fl * fu**2
            + 2 * fu**3
            + 2 * nvtools.D_SPLITTING**3
            - 18 * nvtools.D_SPLITTING * nvtools.E_SPLITTING**2
        ) / (27 * (nvtools.D_SPLITTING - nvtools.E_SPLITTING / 2) * b_squared) + (
            2 * nvtools.D_SPLITTING - 3 * nvtools.E_SPLITTING
        ) / (
            6 * (nvtools.D_SPLITTING - nvtools.E_SPLITTING / 2)
        )
        if cos_theta_squared < 0:
            cos_theta_squared = ufloat(0.0, cos_theta_squared.std_dev)
        cos_theta = um.sqrt(cos_theta_squared)

        b_abs = (um.sqrt(b_squared) / nvtools.GAMMA) * unit.millitesla
        theta = um.acos(cos_theta) * unit.radians

        return b_abs, theta

    def field_from_spectrum(self, mw_frequency, odmr, p0_frequency=None):
        """
        Calculate field from odmr spectrum.

        :param mw_frequency: MW frequency
        :param odmr: ODMR
        :param list | None p0_frequency: estimates for resonance frequencies
        """
        fitter = ODMRFitter()
        fit_results = fitter.fit_odmr_full(mw_frequency, odmr, p0_frequency=p0_frequency)

        fl1, fl2, fl3, fl4, fu4, fu3, fu2, fu1 = fit_results.frequency
        b_abs_1, theta_1 = self.field_from_resonances(fl1, fu1)
        b_abs_2, theta_2 = self.field_from_resonances(fl2, fu2)
        b_abs_3, theta_3 = self.field_from_resonances(fl3, fu3)
        b_abs_4, theta_4 = self.field_from_resonances(fl4, fu4)

        b_abs = [b_abs_1, b_abs_2, b_abs_3, b_abs_4]
        theta = [theta_1, theta_2, theta_3, theta_4]
        b_vec = self.vector_from_field(b_abs, theta)
        b_field = BField(b_abs=b_abs, theta=theta, b_vec=b_vec)
        if nvtools.EXPORT:
            with open("test.json", "w") as file:
                json.dump(b_field.to_dict(), file)

        table_angle = PrettyTable()
        table_angle.set_style(SINGLE_BORDER)
        table_angle.field_names = ["NV axis", "|B|", "theta"]
        for i in range(4):
            table_angle.add_row([f"NV {i + 1}", f"{b_field.b_abs[i]::~P}", f"{b_field.theta[i].to('deg')::~P}"])
        table_vector = PrettyTable()
        table_vector.set_style(SINGLE_BORDER)
        table_vector.field_names = ["|B|", "b_x", "b_y", "b_z"]
        table_vector.add_row([f"{b_vec.length:.2f}mT", f"{b_vec.x:.2f}", f"{b_vec.y:.2f}", f"{b_vec.z:.2f}"])
        if nvtools.VERBOSE:
            print(
                Fore.GREEN
                + Style.BRIGHT
                + "───────────────────────── B-field Solver ─────────────────────────"
                + Style.RESET_ALL
            )
            print(table_angle)
            print(table_vector)
            print("\n")
        if nvtools.EXPORT:
            folder = pathlib.Path(sys.argv[0]).parent
            file_path = pathlib.Path(folder, "b_field.csv")
            success(f"saving B-field results in {file_path}")
            print("\n")
            with open(file_path, "w") as file:
                file.write("# B-field angles\n")
                file.write(table_angle.get_csv_string())
                file.write("\n# B-field vector\n")
                file.write(table_vector.get_csv_string())

        return fit_results, b_field

    @staticmethod
    def resonances_from_field(b_abs, theta, units=True):
        """
        Calculate resonance frequencies.

        :param b_abs: absolute B-field value
        :param theta: angle between B-field and NV-axis
        """
        if units:
            try:
                b_abs = nvtools.GAMMA * b_abs.to("mT").magnitude
                theta = theta.to("rad").magnitude
            except AttributeError:
                b_abs = nvtools.GAMMA * b_abs
                warning(
                    "Input values to 'resonances_from_field(b_abs, theta)' have no unit. Assuming b_abs in mT and "
                    "theta in rad."
                )

        p = nvtools.D_SPLITTING**2 / 3 + nvtools.E_SPLITTING**2 + b_abs**2
        q = (
            -1 / 2 * nvtools.D_SPLITTING * b_abs**2 * um.cos(2 * theta)
            - nvtools.E_SPLITTING * b_abs**2 * um.sin(theta) ** 2
            - 1 / 6 * nvtools.D_SPLITTING * b_abs**2
            + 2 / 27 * nvtools.D_SPLITTING**3
            - 2 / 3 * nvtools.D_SPLITTING * nvtools.E_SPLITTING**2
        )

        t1 = 2 / um.sqrt(3) * um.sqrt(p)
        t2 = um.acos(3 * um.sqrt(3) / 2 * q / um.sqrt(p**3)) / 3
        lambda_0 = t1 * um.cos(t2)
        lambda_1 = t1 * um.cos(t2 - 2 * np.pi / 3)
        lambda_2 = t1 * um.cos(t2 - 4 * np.pi / 3)

        if units:
            fu = (lambda_0 - lambda_2) * unit.MHz
            fl = (lambda_0 - lambda_1) * unit.MHz
        else:
            fu = lambda_0 - lambda_2
            fl = lambda_0 - lambda_1

        return fu, fl

    @staticmethod
    def vector_from_field(b_abs: list[float], theta: list[float]) -> Vector:
        """
        Calculate B-field vector.

        :param b_abs: absolute B-field value
        :param theta: angle between B-field and NV-axis
        """
        if len(b_abs) != 4 or len(theta) != 4:
            raise ValueError("b_abs and theta need to have 4 elements")

        try:
            b_abs = [b.to("mT").magnitude.nominal_value for b in b_abs]
        except AttributeError:
            pass
        try:
            theta = [t.to("rad").magnitude.nominal_value for t in theta]
        except AttributeError:
            pass

        n = 1 / np.sqrt(3) * np.array([[1, 1, 1], [-1, -1, 1], [-1, 1, -1], [1, -1, -1]])
        design = (
            np.sqrt(3)
            / 4
            * np.array(
                [
                    [1, -1, -1, 1],
                    [1, -1, 1, -1],
                    [1, 1, -1, -1],
                ]
            )
        )

        b_abs_total = np.mean(b_abs)
        res = []
        for e in itertools.product([1, -1], repeat=4):
            c = np.array(e) * np.cos(np.array(theta))
            b_vec = design @ c
            temp = c - n @ b_vec
            ssr = temp.T @ temp
            b_vec = Vector(b_vec).normalize() * b_abs_total
            res.append((b_vec, ssr))
        res = list(sorted(res, key=operator.itemgetter(1)))

        return -res[0][0]
