"""ODMR fit models."""

import numpy as np
import scipy
import uncertainties.umath as um

from nvtools import unit


class ModelLorentz1:
    r"""
    Lorentz model with 1 resonance.

    .. math::
        L(x) = 1 - \frac{C\alpha^2}{4(x - f_{\text{res}})^2 + \alpha^2}
    """

    @staticmethod
    def f(x, c, alpha, f_res):
        """
        Lorentz profile.

        :param x: X data
        :param c: contrast
        :param alpha: FWHM linewidth
        :param f_res: resonance frequency
        """
        return 1 - (c * np.power(alpha, 2)) / (4 * np.power(x - f_res, 2) + np.power(alpha, 2))


class ModelGauss1:
    r"""
    Gauss model with 1 resonance.

    .. math::
        G(x) = 1 - C \exp\left(4\ln\left(\frac{1}{2}\right)\frac{(x-f_{\text{res}})^2}{\alpha^2}\right)
    """

    @staticmethod
    def f(x, c, alpha, f_res):
        """
        Gauss profile.

        :param x: X data
        :param c: contrast
        :param alpha: FWHM linewidth
        :param f_res: resonance frequency
        """
        return 1 - c * np.exp(4 * np.log(0.5) * np.power(x - f_res, 2) / np.power(alpha, 2))


class ModelVoigt1:
    r"""
    Voigt model with 1 resonance.

    .. math::
        V(x) = \int G(x-\tau) L(x) \, d\tau
    """

    @staticmethod
    def f(x, a, sigma, nu, f_res, c):
        """
        Voigt profile with 1 resonance.

        :param x: X data
        :param a: area
        :param sigma: Lorentz width
        :param nu: Gauss width
        :param f_res: resonance frequency
        :param c: offset
        """
        z = (x - f_res + 1j * nu) / (sigma * np.sqrt(2))
        return c - a * np.real(scipy.special.wofz(z)) / (sigma * np.sqrt(2 * np.pi))

    @staticmethod
    def voigt_parameters(area, sigma, nu, units=True):
        r"""
        Calculate useful parameters from Voigt fit parameters.

        .. math::
            \alpha_\text{L} &= 2\nu \\
            \alpha_\text{G} &= 2\sigma\sqrt{2\log 2} \\
            \alpha_\text{V} &= 0.5346\alpha_\text{L} + \sqrt{0.2166\alpha_\text{L}^2 + \alpha_\text{G}^2} \\
            d &= \frac{\alpha_\text{L} - \alpha_\text{G}}{\alpha_\text{L} + \alpha_\text{G}} \\
            C &= V(x=f_{\text{res}})

        :param area: area under graph
        :param sigma: Lorentz linewidth
        :param nu: Gauss linewidth
        :returns: alpha_l, alpha_g, alpha_v, d, contrast
        """
        try:
            area = area.to("MHz^2").magnitude
            sigma = sigma.to("MHz").magnitude
            nu = nu.to("MHz").magnitude
        except AttributeError:
            pass

        alpha_l = 2 * nu
        alpha_g = 2 * sigma * um.sqrt(2 * um.log(2))
        alpha_v = 0.5346 * alpha_l + um.sqrt(0.2166 * alpha_l**2 + alpha_g**2)
        d = (alpha_l - alpha_g) / (alpha_g + alpha_l)

        try:
            a_val = area.nominal_value
            nu_val = nu.nominal_value
            sigma_val = sigma.nominal_value
        except AttributeError:
            a_val = area
            nu_val = nu
            sigma_val = sigma

        z0 = (1j * nu_val) / (sigma_val * np.sqrt(2))
        c = a_val * np.real(scipy.special.wofz(z0)) / (sigma_val * np.sqrt(2 * np.pi))

        if units:
            return alpha_l * unit.MHz, alpha_g * unit.MHz, alpha_v * unit.MHz, d, c
        else:
            return alpha_l, alpha_g, alpha_v, d, c


class ModelVoigt8:
    r"""
    Voigt model with 8 resonances.

    .. math::
        V(x) = c - \sum_{i=1}^8 V_i(x)
    """

    @staticmethod
    def f(
        x,
        a1,
        s1,
        n1,
        f1,
        a2,
        s2,
        n2,
        f2,
        a3,
        s3,
        n3,
        f3,
        a4,
        s4,
        n4,
        f4,
        a5,
        s5,
        n5,
        f5,
        a6,
        s6,
        n6,
        f6,
        a7,
        s7,
        n7,
        f7,
        a8,
        s8,
        n8,
        f8,
        c,
    ):
        """Voigt profile for eight resonances."""
        model_voigt_1 = ModelVoigt1()

        return (
            c
            - model_voigt_1.f(x, -a1, s1, n1, f1, 0)
            - model_voigt_1.f(x, -a2, s2, n2, f2, 0)
            - model_voigt_1.f(x, -a3, s3, n3, f3, 0)
            - model_voigt_1.f(x, -a4, s4, n4, f4, 0)
            - model_voigt_1.f(x, -a5, s5, n5, f5, 0)
            - model_voigt_1.f(x, -a6, s6, n6, f6, 0)
            - model_voigt_1.f(x, -a7, s7, n7, f7, 0)
            - model_voigt_1.f(x, -a8, s8, n8, f8, 0)
        )

    @staticmethod
    def voigt_parameters(area, sigma, nu, units=True):
        """Same as ModelVoigt1.voigt_parameters."""
        return ModelVoigt1().voigt_parameters(area, sigma, nu, units)
