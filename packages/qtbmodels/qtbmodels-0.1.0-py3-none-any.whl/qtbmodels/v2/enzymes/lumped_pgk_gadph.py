"""Lumped reaction of Glyceraldehyde 3-phosphate dehydrogenase (GADPH) and Phosphoglycerate kinase (PGK)
    3-Phospho-D-glycerate(aq) + ATP(aq) ⇌ 3-Phospho-D-glyceroyl phosphate(aq) + ADP(aq)
    3-Phospho-D-glyceroyl phosphate(aq) + NADPH(aq) ⇌ D-Glyceraldehyde 3-phosphate(aq) + NADP (aq) + Orthophosphate(aq)
Into
    3-Phospho-D-glycerate(aq) + ATP(aq) + NADPH(aq) ⇌ D-Glyceraldehyde 3-phosphate(aq) + ADP(aq) + Orthophosphate(aq) + NADP(aq)

Equilibrator
    Keq = 6.0e-4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_3s_4p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = "pgk_gadph"


def lumped_pgk_gadph(
    model: Model,
    *,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    model.add_parameter(keq := n.keq(ENZYME), 6.0e-4)
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.18)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 0.27)

    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=537,
        e0=e0,
    ).vmax

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.pga(chl_stroma): -1.0,
            n.atp(chl_stroma): -1.0,
            n.nadph(chl_stroma): -1.0,
            #
            n.gap(chl_stroma): 1.0,
            n.adp(chl_stroma): 1.0,
            n.pi(chl_stroma): 1.0,
            n.nadp(chl_stroma): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_3s_4p,
        stoichiometry=stoichiometry,
        args=[
            n.pga(chl_stroma),
            n.atp(chl_stroma),
            n.nadph(chl_stroma),
            #
            n.gap(chl_stroma),
            n.adp(chl_stroma),
            n.pi(chl_stroma),
            n.nadp(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
