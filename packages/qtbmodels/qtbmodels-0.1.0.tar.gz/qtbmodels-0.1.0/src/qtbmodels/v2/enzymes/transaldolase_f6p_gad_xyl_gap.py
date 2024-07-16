"""F6P + Glycolaldehyde <=> GAP + XYLULOSE

EC 2.2.1.2

Equilibrator
Fructose-6-phosphate(aq) + Glycolaldehyde(aq)
    ⇌ Glyceraldehyde 3-phosphate(aq) + Xylulose(aq)
Keq = 4.8e-4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.transaldolase_f6p_gad_gap_xyl()


def add_transaldolase_f6p_gad_xyl_gap(
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
    model.add_parameter(keq := n.keq(ENZYME), 4.8e-4)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.f6p(compartment): -1.0,
            n.glycolaldehyde(compartment): -1.0,
            #
            n.gap(compartment): 1.0,
            n.xylulose(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.f6p(compartment),
            n.glycolaldehyde(compartment),
            n.gap(compartment),
            n.xylulose(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
