"""Aspartate aminotransferase

EC 2.6.1.1

Equilibrator
Aspartate(aq) + alpha-Ketoglutarate(aq) ⇌ Oxaloacetate(aq) + Glutamate(aq)
Keq = 0.3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.aspartate_aminotransferase()


def add_aspartate_aminotransferase(
    model: Model,
    compartment: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=84,  # Chlamy, BRENDA
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 2.53)  # Chlamy, BRENDA
    model.add_parameter(kmp := n.km(ENZYME, "p"), 3.88)  # Chlamy, BRENDA
    model.add_parameter(keq := n.keq(ENZYME), 0.3)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.aspartate(compartment): -1.0,
            n.oxoglutarate(compartment): -1.0,
            #
            n.oxaloacetate(compartment): 1.0,
            n.glutamate(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.aspartate(compartment),
            n.oxoglutarate(compartment),
            #
            n.oxaloacetate(compartment),
            n.glutamate(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
