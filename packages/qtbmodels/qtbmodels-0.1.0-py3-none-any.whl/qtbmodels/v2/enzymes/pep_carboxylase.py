"""name

EC 4.1.1.31

Equilibrator
Phosphoenolpyruvate(aq) + CO2(total) ⇌ Orthophosphate(aq) + Oxaloacetate(aq)
Keq = 4.4e5 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.pep_carboxylase()


def add_pep_carboxylase(
    model: Model,
    chl_stroma: str,
    per: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    model.add_parameter(kms := n.km(ENZYME, "s"), 1.0)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1.0)
    model.add_parameter(keq := n.keq(ENZYME), 440000.0)

    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=1.0,
        e0=e0,
    ).vmax

    stoichiometry = filter_stoichiometry(
        model,
        stoichiometry={
            n.pep(chl_stroma): -1,
            n.oxaloacetate(per): 1,
        },
        optional={
            n.hco3(chl_stroma): -1,
        },
    )
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.pep(chl_stroma),
            n.hco3(chl_stroma),
            n.oxaloacetate(per),
            n.pi(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
