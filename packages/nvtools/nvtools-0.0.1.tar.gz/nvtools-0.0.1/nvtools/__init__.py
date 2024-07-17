"""NV tools."""

from pint import UnitRegistry

unit = UnitRegistry()

from .io import H5Loader  # NOQA E402
from .plot import ODMRPlotter  # NOQA E402
from .solver import Solver  # NOQA E402

__all__ = [
    "Solver",
    "ODMRPlotter",
    "H5Loader",
]

VERBOSE = True
EXPORT = False
SHOW_PLOTS = True
LATEX = False
ODMR_MODEL = None

D_SPLITTING = 2870
E_SPLITTING = 5
GAMMA = 28
