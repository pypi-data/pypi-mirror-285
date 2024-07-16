"""EC 1.4.1.3

Equilibrator
NADPH(aq) + NH3(aq) + 2-Oxoglutarate(aq) ⇌ H2O(l) + NADP(aq) + L-Glutamate(aq)
Keq = 7.2e5 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_3s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glutamate_dehydrogenase()


def add_glutamate_dehydrogenase(
    model: Model,
    compartment: str,
    enzyme_factor: str | None = None,
    e0: float = 1,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=104,  # Homo sapiens
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 1.54)  # Chlamy, Brenda
    model.add_parameter(kmp := n.km(ENZYME, "p"), 0.64)  # Chlamy, Brenda
    model.add_parameter(keq := n.keq(ENZYME), 7.2e5)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.nadph(compartment): -1.0,
            n.nh4(compartment): -1.0,
            n.oxoglutarate(compartment): -1.0,
            #
            n.glutamate(compartment): 1.0,
            n.nadp(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_3s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.nadph(compartment),
            n.nh4(compartment),
            n.oxoglutarate(compartment),
            #
            n.glutamate(compartment),
            n.nadp(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
