"""acetoacetate_coa_ligase

EC 6.2.1.16

Metacyc (ACETOACETATE--COA-LIGASE-RXN):
    3-KETOBUTYRATE_m + ATP_m + CO-A_m
    --> ACETOACETYL-COA_m + AMP_m + Diphosphate_m + 0.92 PROTON_m

Equilibrator
    Acetoacetate(aq) + ATP(aq) + CoA(aq) ⇌ Acetoacetyl-CoA(aq) + AMP(aq) + Diphosphate(aq)
    Keq = 2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
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

ENZYME = n.acetoacetate_coa_ligase()


def add_acetoacetate_coa_ligase(
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
        kcat=5.89,
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        {
            n.acetoacetate(mit): -1,
            n.atp(mit): -1,
            n.coa(mit): -1,
            #
            n.acetoacetyl_coa(mit): 1,
            n.amp(mit): 1,
            n.ppi(mit): 1,
        },
    )
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.07)
    if reversible:
        model.add_parameter(keq := n.keq(ENZYME), 2)
        model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_3s_3p,
            stoichiometry=stoichiometry,
            args=[
                n.acetoacetate(mit),
                n.atp(mit),
                n.coa(mit),
                n.acetoacetyl_coa(mit),
                n.amp(mit),
                n.ppi(mit),
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
                n.acetoacetate(mit),
                n.atp(mit),
                n.coa(mit),
                vmax,
                kms,
            ],
        )
    return model
