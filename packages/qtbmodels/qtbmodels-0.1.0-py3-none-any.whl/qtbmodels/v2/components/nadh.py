"""Concentrations
-------------
Stroma        | NAD  | 190 µM   | Heineke 1990
Mitochondrium | NAD  | 640 µM   | Kasimova 2006
Mitochondrium | NADH | 220 µM   | Kasimova 2006


NADH / NAD ratio
----------------
Cytosol       | 1e-2    | Heineke 1990
Chloroplast   | 0.04    | Höhner 2021
Mitochondrium | 0.34375 | Kasimova 2006
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_nadh_static(
    model: Model,
    *,
    compartment: str,
    nadh: float = 0.22,
    total: float = 0.86,
) -> Model:
    model.add_parameter(n.nadh(compartment), nadh)
    model.add_parameter(f"NAD*{compartment}_total", total)

    model.add_derived_parameter(
        n.nad(compartment),
        moiety_1,
        [
            n.nadh(compartment),
            "NAD*_total",
        ],
    )
    return model


def add_nadh_dynamic(model: Model, *, compartment: str, total: float) -> Model:
    model.add_compound(n.nadh(compartment))
    model.add_parameter(f"NAD*{compartment}_total", total)

    model.add_derived_compound(
        n.nad(compartment),
        moiety_1,
        args=[
            n.nadh(compartment),
            "NAD*_total",
        ],
    )
    return model
