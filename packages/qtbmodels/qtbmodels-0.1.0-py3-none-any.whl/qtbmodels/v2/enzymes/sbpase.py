"""SBPase

EC 3.1.3.37

Equilibrator
    H2O(l) + Sedoheptulose 1,7-bisphosphate(aq)
    ⇌ Orthophosphate(aq) + Sedoheptulose 7-phosphate(aq)
    Keq = 2e2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import michaelis_menten_1s_1i

from ._utils import build_vmax

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.sbpase()


def add_sbpase(
    model: Model,
    *,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    model.add_parameter(km := n.km(ENZYME), 0.013)
    model.add_parameter(ki := n.ki(ENZYME, n.pi()), 12.0)
    kcat = 0.04 * 8

    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=kcat,
        enzyme_factor=enzyme_factor,
        e0=e0,
    ).vmax

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_1s_1i,
        stoichiometry={
            n.sbp(chl_stroma): -1,
            n.s7p(chl_stroma): 1,
        },
        args=[
            n.sbp(chl_stroma),
            n.pi(chl_stroma),
            vmax,
            km,
            ki,
        ],
    )
    return model
