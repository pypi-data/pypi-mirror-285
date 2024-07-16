"""Glycolaldehyde + S7P <=> RIBOSE_5P  + ERYTHRULOSE

EC 2.2.1.1

Equilibrator
Glycolaldehyde(aq) + Sedoheptulose-7-phosphate(aq)
    ⇌ Ribose-5-phosphate(aq) + Erythrulose(aq)
Keq = 0.5 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.transketolase_gad_s7p_r5p_eru()


def add_transketolase_gad_s7p_eru_r5p(
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
    model.add_parameter(keq := n.keq(ENZYME), 0.5)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.glycolaldehyde(compartment): -1.0,
            n.s7p(compartment): -1.0,
            #
            n.r5p(compartment): 1.0,
            n.erythrulose(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.glycolaldehyde(compartment),
            n.s7p(compartment),
            n.r5p(compartment),
            n.erythrulose(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
