"""EC 5.4.2.1

Equilibrator
2-Phospho-D-glycerate(aq) ⇌ 3-Phospho-D-glycerate(aq)
Keq = 6 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_1s_1p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.phosphoglycerate_mutase()


def add_phosphoglycerate_mutase(
    model: Model,
    compartment: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=1.0,  # FIXME
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 1.0)  # FIXME
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1.0)  # FIXME
    model.add_parameter(keq := n.keq(ENZYME), 6)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.pga2(compartment): -1.0,
            #
            n.pga(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_1s_1p,
        stoichiometry=stoichiometry,
        args=[
            n.pga2(compartment),
            n.pga(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
