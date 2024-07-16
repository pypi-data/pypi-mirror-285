"""TCR1: nadph + tarcoa -> nadp + coa + 2h3oppan

Tartronyl-Coa + NADPH -> Tartronate-semialdehyde + NADP + CoA
dG' = 29.78
Keq = 6.06e-6
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_3p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.tartronyl_coa_reductase()


def add_tartronyl_coa_reductase(
    model: Model,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model, enzyme_name=ENZYME, kcat=1.4, enzyme_factor=enzyme_factor, e0=e0
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.03)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
    model.add_parameter(keq := n.keq(ENZYME), 6.06e-06)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_3p,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.nadph(chl_stroma): -1,
                n.tartronyl_coa(chl_stroma): -1,
                n.nadp(chl_stroma): 1,
                n.tartronate_semialdehyde(chl_stroma): 1,
            },
        ),
        args=[
            # substrates
            n.tartronyl_coa(chl_stroma),
            n.nadph(chl_stroma),
            # products
            n.tartronate_semialdehyde(chl_stroma),
            n.nadp(chl_stroma),
            n.coa(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
