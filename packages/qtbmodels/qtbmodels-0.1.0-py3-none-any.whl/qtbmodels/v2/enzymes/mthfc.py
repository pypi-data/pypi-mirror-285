"""Methenyltetrahydrofolate cyclohydrolase

EC 3.5.4.9
Metacyc: MTHFC

10-FORMYL-THF_m + 0.07 PROTON_m <=> 5-10-METHENYL-THF_m + WATER_m

Equilibrator
10-Formyl-THF(aq) ⇌ 5,10-Methenyltetrahydrofolate(aq) + H2O(l)
Keq = 0.1 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_1s,
    reversible_michaelis_menten_1s_1p,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.mthfc()


def add_mthfc(
    model: Model,
    mit: str,
    *,
    reversible: bool,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=40,
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.2)

    if reversible:
        model.add_parameter(kmp := n.km(ENZYME, "p"), 0.04)
        model.add_parameter(keq := n.keq(ENZYME), 0.1)

        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_1s_1p,
            stoichiometry=filter_stoichiometry(
                model,
                {
                    n.formyl_thf(mit): -1,
                    n.methenyl_thf(mit): 1,
                },
            ),
            args=[
                n.formyl_thf(mit),
                n.methenyl_thf(mit),
                vmax,
                kms,
                kmp,
                keq,
            ],
        )
    else:
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=michaelis_menten_1s,
            stoichiometry=filter_stoichiometry(
                model,
                {
                    n.formyl_thf(mit): -1,
                    n.methenyl_thf(mit): 1,
                },
            ),
            args=[
                n.formyl_thf(mit),
                vmax,
                kms,
            ],
        )

    return model
