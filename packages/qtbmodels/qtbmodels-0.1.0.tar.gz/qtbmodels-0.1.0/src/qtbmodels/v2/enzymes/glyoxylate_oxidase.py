"""name

EC 1.2.3.5

Equilibrator
Glyoxylate(aq) + H2O(l) + O2(aq) ⇌ Oxalate(aq) + H2O2(aq)
Keq = 2.5e28 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import michaelis_menten_2s

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glyoxylate_oxidase()


def add_glyoxylate_oxidase(
    model: Model,
    compartment: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=1.0,  # FIXME
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME), 1.0)  # FIXME

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.glyoxylate(compartment): -1.0,
            # n.h2o(compartment): -1.0,
            n.o2(compartment): -1.0,
            n.oxalate(compartment): 1.0,
            n.h2o2(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_2s,
        stoichiometry=stoichiometry,
        args=[
            n.glyoxylate(compartment),
            n.o2(compartment),
            vmax,
            kms,
        ],
    )
    return model
