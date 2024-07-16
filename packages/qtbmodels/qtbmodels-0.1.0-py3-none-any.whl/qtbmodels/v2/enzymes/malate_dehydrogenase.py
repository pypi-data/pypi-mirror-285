"""name

EC 1.1.1.37

Equilibrator
Oxaloacetate(aq) + NADH(aq) ⇌ Malate(aq) + NAD(aq)
Keq = 4.4e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.malate_dehydrogenase()


def add_malate_dehydrogenase(
    model: Model,
    chl_stroma: str,
    per: str,
    *,
    nadph_hack: bool,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=1.0,
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 1.0)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1.0)
    model.add_parameter(keq := n.keq(ENZYME), 44000.0)

    if nadph_hack:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.oxaloacetate(per): -1,
                n.nadph(per): -1,
                n.malate(chl_stroma): 1,
                n.nadp(per): 1,
            },
        )
    else:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.oxaloacetate(per): -1,
                n.nadh(per): -1,
                n.malate(chl_stroma): 1,
                n.nad(per): 1,
            },
        )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.oxaloacetate(per),
            n.nadh(per),
            n.malate(chl_stroma),
            n.nad(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
