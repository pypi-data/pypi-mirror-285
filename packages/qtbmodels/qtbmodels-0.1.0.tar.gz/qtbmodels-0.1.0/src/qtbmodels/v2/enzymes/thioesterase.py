"""EC 3.1.2.10

Metacyc:
FORMYL_COA_m + WATER_m <=> CO-A_m + FORMATE_m + PROTON_m

Equilibrator
Formyl-CoA(aq) + Water(l) ⇌ CoA(aq) + Formate(aq)
Keq = 4e1 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_1s,
    reversible_michaelis_menten_1s_2p,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.thioesterase()


def add_thioesterase(
    model: Model,
    mit: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
    *,
    reversible: bool = True,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=1.0,
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        {
            n.formyl_coa(mit): -1,
            #
            n.coa(mit): 1,
            n.formate(mit): 1,
        },
    )
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.045)
    if reversible:
        model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
        model.add_parameter(keq := n.keq(ENZYME), 40.0)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_1s_2p,
            stoichiometry=stoichiometry,
            args=[
                n.formyl_coa(mit),
                n.coa(mit),
                n.formate(mit),
                vmax,
                kms,
                kmp,
                keq,
            ],
        )
    else:
        model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
        model.add_parameter(keq := n.keq(ENZYME), 40.0)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=michaelis_menten_1s,
            stoichiometry=stoichiometry,
            args=[
                n.formyl_coa(mit),
                vmax,
                kms,
            ],
        )
    return model
