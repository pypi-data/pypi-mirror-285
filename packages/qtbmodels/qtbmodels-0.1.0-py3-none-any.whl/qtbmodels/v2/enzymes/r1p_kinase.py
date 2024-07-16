"""R1P + ATP  <=> RUBP + ADP

EC FIXME

Equilibrator
Ribose-1-phosphate(aq) + ATP(aq) ⇌ Ribulose-1,5-bisphosphate(aq) + ADP(aq)
Keq = 4.4e6 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import michaelis_menten_2s

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.r1p_kinase()


def add_r1p_kinase(
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

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.r1p(compartment): -1.0,
            n.atp(compartment): -1.0,
            #
            n.rubp(compartment): 1.0,
            n.adp(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_2s,
        stoichiometry=stoichiometry,
        args=[
            n.r1p(compartment),
            n.atp(compartment),
            vmax,
            kms,
        ],
    )
    return model
