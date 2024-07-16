"""name

EC 6.3.4.3

Equilibrator
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_3s,
    reversible_michaelis_menten_3s_3p,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.formate_thf_ligase()


def add_formate_thf_ligase(
    model: Model,
    mit: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
    *,
    reversible: bool = True,
) -> Model:
    """EC 6.3.4.3
    Metacyc: FORMATETHFLIG-RXN
    FORMATE_m + ATP_m + THF_m <=> 10-FORMYL-THF_m + ADP_m + Pi_m

    Equilibrator
    Formate(aq) + THF(aq) + ATP(aq) ⇌ 10-Formyltetrahydrofolate(aq) + ADP(aq) + Pi(aq)
    Keq = 2.0 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=6.08,
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        {
            n.formate(mit): -1,
            n.atp(mit): -1,
            n.thf(mit): -1,
            #
            n.formyl_thf(mit): 1,
            n.adp(mit): 1,
            n.pi(mit): 1,
        },
    )
    model.add_parameter(kms := n.km(ENZYME, "s"), 7.6)
    if reversible:
        model.add_parameter(keq := n.keq(ENZYME), 2.0)
        model.add_parameter(kmp := n.km(ENZYME, "p"), 10)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_3s_3p,
            stoichiometry=stoichiometry,
            args=[
                n.formate(mit),
                n.atp(mit),
                n.thf(mit),
                n.formyl_thf(mit),
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
            function=michaelis_menten_3s,
            stoichiometry=stoichiometry,
            args=[
                n.formate(mit),
                n.atp(mit),
                n.thf(mit),
                vmax,
                kms,
            ],
        )
    return model
