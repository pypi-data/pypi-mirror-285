"""Glycolyl-CoA + NADPH <=> Glycolaldehyde + NADP + CoA

EC 1.2.1.12

Equilibrator

Keq = ? (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_3p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glycolaldehyde_dehydrogenase()


def add_glycolaldehyde_dehydrogenase(
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
    model.add_parameter(keq := n.keq(ENZYME), 1.0)  # FIXME

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.glycolyl_coa(compartment): -1.0,
            n.nadph(compartment): -1.0,
            #
            n.glycolaldehyde(compartment): 1.0,
            n.nadp(compartment): 1.0,
            n.coa(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_3p,
        stoichiometry=stoichiometry,
        args=[
            n.glycolyl_coa(compartment),
            n.nadph(compartment),
            n.glycolaldehyde(compartment),
            n.nadp(compartment),
            n.coa(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
