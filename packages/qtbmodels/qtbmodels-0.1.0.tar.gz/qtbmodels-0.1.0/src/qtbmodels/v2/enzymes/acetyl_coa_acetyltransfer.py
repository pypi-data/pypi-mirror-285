"""name

EC 2.3.1.9

Metacyc:
ACETOACETYL-COA_m + CO-A_m  <=>  2.0 ACETYL-COA_m

Equilibrator
Acetoacetyl-CoA(aq) + CoA(aq) ⇌ 2 Acetyl-CoA(aq)
Keq = 2.4e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_2s,
    reversible_michaelis_menten_2s_1p,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.acetyl_coa_acetyltransfer()


def add_acetyl_coa_acetyltransfer(
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
        kcat=220.5,
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        stoichiometry={
            n.acetoacetyl_coa(mit): -1,
            n.coa(mit): -1,
            n.acetyl_coa(mit): 2,
        },
    )
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.0176)
    if reversible:
        model.add_parameter(keq := n.keq(ENZYME), 24000.0)
        model.add_parameter(kmp := n.km(ENZYME, "p"), 0.1386)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_2s_1p,
            stoichiometry=stoichiometry,
            args=[
                n.acetoacetyl_coa(mit),
                n.coa(mit),
                n.acetyl_coa(mit),
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
                n.acetoacetyl_coa(mit),
                n.coa(mit),
                vmax,
                kms,
            ],
        )
    return model
