"""malic enzyme == malate dehydrogenase decarboxylating

EC 1.1.1.39

Equilibrator
    NAD (aq) + (S)-Malate(aq) + H2O(l) ⇌ NADH(aq) + Pyruvate(aq) + CO2(total)
    Keq = 0.2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_3p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.malic_enzyme()


def add_malic_enzyme(
    model: Model,
    chl_stroma: str,
    *,
    nadph_hack: bool,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.003)  # Zea mays
    model.add_parameter(kmp := n.km(ENZYME, "p"), 0.00125)  # Zea mays
    model.add_parameter(keq := n.keq(ENZYME), 0.2)

    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=39,  # Arabidopsis
        e0=e0,
    ).vmax

    if nadph_hack:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.nadp(chl_stroma): -1,
                n.malate(chl_stroma): -1,
                #
                n.nadph(chl_stroma): 1,
                n.pyruvate(chl_stroma): 1,
                n.co2(chl_stroma): 1,
            },
        )
    else:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.nad(chl_stroma): -1,
                n.malate(chl_stroma): -1,
                #
                n.nadh(chl_stroma): 1,
                n.pyruvate(chl_stroma): 1,
                n.co2(chl_stroma): 1,
            },
        )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_3p,
        stoichiometry=stoichiometry,
        args=[
            n.nad(chl_stroma),
            n.malate(chl_stroma),
            #
            n.nadh(chl_stroma),
            n.pyruvate(chl_stroma),
            n.co2(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
