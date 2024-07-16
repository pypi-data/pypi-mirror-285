"""pyruvate dehydrogenase

EC 1.2.4.1

Equilibrator
------------
    NAD (aq) + CoA(aq) + Pyruvate(aq) + H2O(l) ⇌ NADH(aq) + Acetyl-CoA(aq) + CO2(total)
    Keq = 2.6e7 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_3s_3p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.pyruvate_dehydrogenase()


def add_pyruvate_dehydrogenase(
    model: Model,
    chl_stroma: str,
    *,
    nadph_hack: bool,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.0124)  # Synechocystis
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1.0)  # FIXME
    model.add_parameter(keq := n.keq(ENZYME), 2.6e7)

    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=0.48,  # Geobacillus
        e0=e0,
    ).vmax

    if nadph_hack:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.nadp(chl_stroma): -1,
                n.coa(chl_stroma): -1,
                n.pyruvate(chl_stroma): -1,
                #
                n.nadph(chl_stroma): 1,
                n.acetyl_coa(chl_stroma): 1,
                n.co2(chl_stroma): 1,
            },
        )
    else:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.nad(chl_stroma): -1,
                n.coa(chl_stroma): -1,
                n.pyruvate(chl_stroma): -1,
                #
                n.nadh(chl_stroma): 1,
                n.acetyl_coa(chl_stroma): 1,
                n.co2(chl_stroma): 1,
            },
        )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_3s_3p,
        stoichiometry=stoichiometry,
        args=[
            n.nad(chl_stroma),
            n.coa(chl_stroma),
            n.pyruvate(chl_stroma),
            #
            n.nadh(chl_stroma),
            n.acetyl_coa(chl_stroma),
            n.co2(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
