"""name

EC 6.2.1.5

Metacyc: SUCCCOASYN-RXN
SUC_m + CO-A_m + ATP_m <=> SUC-COA_m + ADP_m + Pi_m

Equilibrator
Succinate(aq) + CoA(aq) + ATP(aq) ⇌ Succinyl-CoA(aq) + ADP(aq) + Pi(aq)
Keq = 2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_2s,
    reversible_michaelis_menten_2s_3p,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.succinyl_coa_synthetase()


def add_succinyl_coa_synthetase(
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
        kcat=44.73,
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        {
            n.succinate(mit): -1,
            n.coa(mit): -1,
            #
            n.succinyl_coa(mit): 1,
            n.adp(mit): 1,
            n.pi(mit): 1,
        },
    )
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.25)
    if reversible:
        model.add_parameter(keq := n.keq(ENZYME), 2)
        model.add_parameter(kmp := n.km(ENZYME, "p"), 0.041)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_2s_3p,
            stoichiometry=stoichiometry,
            args=[
                n.succinate(mit),
                n.coa(mit),
                n.succinyl_coa(mit),
                n.adp(mit),
                n.pi(mit),
                vmax,
                kms,
                kmp,
                keq,
            ],
        )
    else:
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=michaelis_menten_2s,
            stoichiometry=stoichiometry,
            args=[
                n.succinate(mit),
                n.coa(mit),
                vmax,
                kms,
            ],
        )
    return model
