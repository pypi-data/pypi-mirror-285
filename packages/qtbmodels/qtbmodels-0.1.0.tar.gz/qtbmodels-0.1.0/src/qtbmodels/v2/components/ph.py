"""name

EC FIXME

Equilibrator
"""

import math
from typing import cast

import numpy as np
from modelbase.ode import Model

from qtbmodels import names as n


def _ph_lumen(protons: float) -> float:
    return cast(float, -np.log10(protons * 0.00025))


def _dG_pH(r: float, t: float) -> float:
    return math.log(10) * r * t


def add_ph_lumen(model: Model, *, chl_lumen: str) -> Model:
    model.add_derived_parameter("dG_pH", _dG_pH, ["R", "T"])

    model.add_derived_compound(
        name=n.ph(chl_lumen),
        function=_ph_lumen,
        args=[
            n.h(chl_lumen),
        ],
    )
    return model
