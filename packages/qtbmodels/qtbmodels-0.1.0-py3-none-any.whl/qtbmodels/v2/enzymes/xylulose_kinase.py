"""XYLULOSE + ATP  <=> XYLULOSE_5_PHOSPHATE + ADP

EC FIXME

Equilibrator
Xylulose(aq) + ATP(aq) ⇌ Xylulose-5-phosphate(aq) + ADP(aq)
Keq = 2.2e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.xylulose_kinase()


def add_xylulose_kinase(
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
    model.add_parameter(kms := n.km(ENZYME, "s"), 1.0)  # FIXME
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1.0)  # FIXME
    model.add_parameter(keq := n.keq(ENZYME), 2.2e4)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.xylulose(compartment): -1.0,
            n.atp(compartment): -1.0,
            #
            n.x5p(compartment): 1.0,
            n.adp(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.xylulose(compartment),
            n.atp(compartment),
            n.x5p(compartment),
            n.adp(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
