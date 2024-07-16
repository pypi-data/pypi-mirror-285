"""EC 1.1.99.14

Equilibrator
------------
Glycolate(aq) + NAD (aq) ⇌ Glyoxylate(aq) + NADH(aq)
Keq = 6.2 x 10-8 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glycolate_dehydrogenase()


def add_glycolate_dehydrogenase(
    model: Model,
    chl_stroma: str,
    *,
    nadph_hack: bool,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=1.93,  # chlamy
        e0=e0,
    ).vmax

    if nadph_hack:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.glycolate(chl_stroma): -1,
                n.nadp(): -1,
                n.glyoxylate(chl_stroma): 1,
                n.nadph(): 1,
            },
        )
    else:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.glycolate(chl_stroma): -1,
                n.nad(): -1,
                n.glyoxylate(chl_stroma): 1,
                n.nadh(): 1,
            },
        )

    model.add_parameter(kms := n.km(ENZYME, "s"), 0.21)  # chlamy
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
    model.add_parameter(keq := n.keq(ENZYME), 6.2e-8)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.glycolate(chl_stroma),
            n.nad(),
            n.glyoxylate(chl_stroma),
            n.nadh(),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
