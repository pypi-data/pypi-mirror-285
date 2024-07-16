"""Phosphoglycerate kinase (PGK)

EC 2.7.2.3

kcat
    - 537 | 1 /s | Pseudomonas sp. | brenda

km
    - 0.18 | PGA | mM | Synechocystis sp. | brenda
    - ? | BPGA | mM | Synechocystis sp. | brenda
    - 0.3 | ATP | mM | Spinacia oleracea | brenda
    - 0.27 | ADP | mM | Spinacia oleracea | brenda


Equilibrator
    ATP(aq) + 3-Phospho-D-glycerate(aq) ⇌ ADP(aq) + 3-Phospho-D-glyceroyl phosphate(aq)
    Keq = 3.7e-4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    rapid_equilibrium_2s_2p,
    reversible_michaelis_menten_2s_2p,
)

from ._utils import add_parameter_if_missing, build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.phosphoglycerate_kinase()


def add_phosphoglycerate_kinase_poolman(
    model: Model,
    *,
    chl_stroma: str,
) -> Model:
    model.add_parameter(keq := n.keq(ENZYME), 0.00031)
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.pga(chl_stroma): -1.0,
            n.atp(chl_stroma): -1.0,
            n.bpga(chl_stroma): 1.0,
            n.adp(chl_stroma): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.pga(chl_stroma),
            n.atp(chl_stroma),
            n.bpga(chl_stroma),
            n.adp(chl_stroma),
            "k_rapid_eq",
            keq,
        ],
    )
    return model


def add_phosphoglycerate_kinase(
    model: Model,
    *,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    model.add_parameter(keq := n.keq(ENZYME), 3.7e-4)
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.18)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 0.27)

    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=537,
        e0=e0,
    ).vmax

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.pga(chl_stroma): -1.0,
            n.atp(chl_stroma): -1.0,
            n.bpga(chl_stroma): 1.0,
            n.adp(chl_stroma): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.pga(chl_stroma),
            n.atp(chl_stroma),
            n.bpga(chl_stroma),
            n.adp(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
