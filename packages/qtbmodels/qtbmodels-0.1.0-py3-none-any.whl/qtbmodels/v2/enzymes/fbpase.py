"""fructose-1,6-bisphosphatase

EC 3.1.3.11

Equilibrator

Equilibrator
    H2O(l) + D-Fructose 1,6-bisphosphate(aq) ⇌ Orthophosphate(aq) + D-Fructose 6-phosphate(aq)
    Keq = 1.2e3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import michaelis_menten_1s_2i

from ._utils import build_vmax

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.fbpase()


def add_fbpase(
    model: Model,
    *,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    model.add_parameter(km := n.km(ENZYME), 0.03)
    model.add_parameter(ki1 := n.ki(ENZYME, n.f6p()), 0.7)
    model.add_parameter(ki2 := n.ki(ENZYME, n.pi()), 12.0)
    kcat = 0.2 * 8

    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=kcat,
        enzyme_factor=enzyme_factor,
        e0=e0,
    ).vmax

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_1s_2i,
        stoichiometry={
            n.fbp(chl_stroma): -1,
            n.f6p(chl_stroma): 1,
        },
        args=[
            n.fbp(chl_stroma),
            n.f6p(chl_stroma),
            n.pi(chl_stroma),
            vmax,
            km,
            ki1,
            ki2,
        ],
    )
    return model
