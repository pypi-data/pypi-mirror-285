"""EC 1.5.1.5

Metacyc: METHYLENETHFDEHYDROG-NADP-RXN
METHENYL-THF_m + NADPH_m + 0.93 PROTON_m <=> METHYLENE-THF_m + NADP_m

Equilibrator
5,10-Methenyltetrahydrofolate(aq) + NADPH(aq) ⇌ 5,10-Methylenetetrahydrofolate(aq) + NADP(aq)
Keq = 1e1 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_2s,
    reversible_michaelis_menten_2s_2p,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.methylene_thf_dehydrogenase()


def add_methylene_thf_dehydrogenase(
    model: Model,
    mit: str,
    *,
    reversible: bool = True,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=14,
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        {
            n.methenyl_thf(mit): -1,
            n.nadph(mit): -1,
            #
            n.methylene_thf(mit): 1,
            n.nadp(mit): 1,
        },
    )

    model.add_parameter(kms := n.km(ENZYME, "s"), 0.12)
    if reversible:
        model.add_parameter(keq := n.keq(ENZYME), 10.0)
        model.add_parameter(kmp := n.km(ENZYME, "p"), 0.302)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_2s_2p,
            stoichiometry=stoichiometry,
            args=[
                n.methenyl_thf(mit),
                n.nadph(mit),
                n.methylene_thf(mit),
                n.nadp(mit),
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
                n.methenyl_thf(mit),
                n.nadph(mit),
                vmax,
                kms,
            ],
        )
    return model
