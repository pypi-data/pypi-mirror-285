"""name

EC 2.7.1.209

Equilibrator
Erythrulose(aq) + ATP(aq) ⇌ Erythrulose 1-phosphate(aq) + ADP(aq)
Keq = 6 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.erythrulose_kinase()


def add_erythrulose_kinase(
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
    model.add_parameter(keq := n.keq(ENZYME), 6)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.erythrulose(compartment): -1.0,
            n.atp(compartment): -1.0,
            #
            n.erythrulose_1p(compartment): 1.0,
            n.adp(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.erythrulose(compartment),
            n.atp(compartment),
            n.erythrulose_1p(compartment),
            n.adp(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
