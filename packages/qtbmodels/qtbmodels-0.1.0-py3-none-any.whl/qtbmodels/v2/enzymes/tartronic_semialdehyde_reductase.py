"""Tartronate semialdehyde(aq) + NADH(aq) ⇌ Glycerate(aq) + NAD (aq)
Keq = 1.6e5 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.tartronate_semialdehyde_reductase()


def add_tartronate_semialdehyde_reductase(
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
        kcat=243,
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.05)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 0.28)
    model.add_parameter(keq := n.keq(ENZYME), 1.6e5)

    if nadph_hack:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.tartronate_semialdehyde(chl_stroma): -1,
                n.nadph(chl_stroma): -1,
                n.glycerate(chl_stroma): 1,
                n.nadp(chl_stroma): 1,
            },
        )
    else:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.tartronate_semialdehyde(chl_stroma): -1,
                n.nadh(chl_stroma): -1,
                n.glycerate(chl_stroma): 1,
                n.nad(chl_stroma): 1,
            },
        )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.tartronate_semialdehyde(chl_stroma),
            n.nadh(chl_stroma),
            n.glycerate(chl_stroma),
            n.nad(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
