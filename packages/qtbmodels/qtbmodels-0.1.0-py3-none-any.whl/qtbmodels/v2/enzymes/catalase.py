"""catalase

2 H2O2 <=> 2 H2O + O2

Equilibrator
2 H2O2(aq) ⇌ 2 H2O(l) + O2(aq)
Keq = 4.3e33 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import michaelis_menten_1s

from ._utils import build_vmax

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.catalase()


def add_catalase(
    model: Model,
    *,
    kcat: float = 760500.0,
    e0: float = 1.0,
    enzyme_factor: str | None = None,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=kcat,
        enzyme_factor=enzyme_factor,
        e0=e0,
    ).vmax
    model.add_parameter(km := n.km(ENZYME), 137.9)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_1s,
        stoichiometry={
            n.h2o2(): -1,
        },
        args=[
            n.h2o2(),
            vmax,
            km,
        ],
    )
    return model
