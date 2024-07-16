"""Glycolaldehyde + GAP <=> A5P

EC 4.1.2.?

Equilibrator
Glycolaldehyde(aq) + Glyceraldehyde 3-phosphate(aq) ⇌ Arabinose-5-phosphate(aq)
Keq = 6.1e2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_1p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.a5p_aldolase()


def add_a5p_aldolase(
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
    model.add_parameter(keq := n.keq(ENZYME), 6.1e2)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.glycolaldehyde(compartment): -1.0,
            n.gap(compartment): -1.0,
            #
            n.arabinose_5_phosphate(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_1p,
        stoichiometry=stoichiometry,
        args=[
            n.glycolaldehyde(compartment),
            n.gap(compartment),
            n.arabinose_5_phosphate(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
