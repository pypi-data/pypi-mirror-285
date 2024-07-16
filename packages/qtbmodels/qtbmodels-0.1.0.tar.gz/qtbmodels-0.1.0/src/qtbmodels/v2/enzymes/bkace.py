"""name

EC FIXME

Equilibrator
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

ENZYME = n.bkace()


def add_bkace(
    model: Model,
    mit: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
    *,
    reversible: bool = True,
) -> Model:
    """Metacyc:
    ACETYL-COA + MALONATE-S-ALD <=> 3-KETOBUTYRATE + FORMYL_COA

    Equilibrator
    Acetyl-CoA(aq) + Malonate semialdehyde(aq) ⇌ Acetoacetate(aq) + Formyl-CoA(aq)
    Keq = 1.2e3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=0.21,
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        {
            n.acetyl_coa(mit): -1,
            n.malonate_s_aldehyde(mit): -1,
            #
            n.acetoacetate(mit): 1,
            n.formyl_coa(mit): 1,
        },
    )
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.84)
    if reversible:
        model.add_parameter(keq := n.keq(ENZYME), 1200.0)
        model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_2s_2p,
            stoichiometry=stoichiometry,
            args=[
                n.acetyl_coa(mit),
                n.malonate_s_aldehyde(mit),
                n.acetoacetate(mit),
                n.formyl_coa(mit),
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
                n.acetyl_coa(mit),
                n.malonate_s_aldehyde(mit),
                vmax,
                kms,
            ],
        )
    return model
