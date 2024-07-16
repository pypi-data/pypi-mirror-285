"""EC 1.2.1.75

Metacyc:
MALONYL-COA_m + NADPH_m + PROTON_m <=> CO-A_m + MALONATE-S-ALD_m + NADP_m

Equilibrator
Malonyl-CoA(aq) + NADPH(aq) ⇌ Malonate semialdehyde(aq) + NADP(aq) + CoA(aq)
Keq = 5.6e-3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
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

ENZYME = n.malonyl_coa_reductase()


def add_malonyl_coa_reductase(
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
        kcat=50.0,
        enzyme_factor=enzyme_factor,
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.03)
    stoichiometry = filter_stoichiometry(
        model,
        {
            n.malonyl_coa(mit): -1,
            n.nadph(mit): -1,
            #
            n.malonate_s_aldehyde(mit): 1,
            n.coa(mit): 1,
        },
    )

    if reversible:
        model.add_parameter(keq := n.keq(ENZYME), 0.0056)
        model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_2s_3p,
            stoichiometry=stoichiometry,
            args=[
                n.malonyl_coa(mit),
                n.nadph(mit),
                n.malonate_s_aldehyde(mit),
                n.nadp(mit),
                n.coa(mit),
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
                n.malonyl_coa(mit),
                n.nadph(mit),
                vmax,
                kms,
            ],
        )
    return model
