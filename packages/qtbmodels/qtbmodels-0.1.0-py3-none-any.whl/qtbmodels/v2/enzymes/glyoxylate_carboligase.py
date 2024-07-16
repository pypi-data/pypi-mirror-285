"""glyoxylate carboligase == tartronate-semialdehyde synthase

EC 4.1.1.47

Equilibrator
2 Glyoxylate + H2O <=> Tartronate semialdehyde + CO2(total)
Keq = 1.6e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_1s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glyoxylate_carboligase()


def add_glyoxylate_carboligase(
    model: Model,
    compartment: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=18.9,  # Brenda (E.coli)
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        {
            n.glyoxylate(compartment): -2,
            #
            n.tartronate_semialdehyde(compartment): 1,
            n.co2(compartment): 1,
        },
    )
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.9)  # Brenda (E.coli)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
    model.add_parameter(keq := n.keq(ENZYME), 1.6e4)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_1s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.glyoxylate(compartment),
            n.tartronate_semialdehyde(compartment),
            n.co2(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
