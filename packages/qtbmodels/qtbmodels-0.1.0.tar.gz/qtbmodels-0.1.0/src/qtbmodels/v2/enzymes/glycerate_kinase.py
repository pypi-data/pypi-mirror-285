"""glycerate kinase

ATP + D-Glycerate <=> ADP + 3-Phospho-D-glycerate

Equilibrator
ATP(aq) + D-Glycerate(aq) ⇌ ADP(aq) + 3-Phospho-D-glycerate(aq)
Keq = 4.9e2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_2s,
    reversible_michaelis_menten_2s_2p,
)

from ._utils import build_vmax

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glycerate_kinase()


# def _rate_glycerate_kinase(
#     s1: float,
#     s2: float,
#     i1: float,
#     vmax: float,
#     km_s1: float,
#     km_s2: float,
#     ki1: float,
# ) -> float:
#     return vmax * s1 * s2 / (s1 * s2 + s1 * km_s1 + s2 * km_s2 * (1 + i1 / ki1))


def add_glycerate_kinase(
    model: Model,
    *,
    irreversible: bool,
    kcat: float = 5.71579,
    e0: float = 1.0,
    enzyme_factor: str | None = None,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=kcat,
        e0=e0,
        enzyme_factor=enzyme_factor,
    ).vmax

    model.add_parameter(km_gly := n.km(ENZYME, n.glycerate()), 0.25)
    # model.add_parameter(km_atp := n.km(ENZYME, n.atp()), 0.21)
    # model.add_parameter(ki := n.ki(ENZYME, n.pga()), 0.36)

    stoichiometry = {
        n.glycerate(): -1.0,
        n.atp(): -1.0,
        n.pga(): 1.0,
    }

    if irreversible:
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=michaelis_menten_2s,
            stoichiometry=stoichiometry,
            args=[
                n.glycerate(),
                n.atp(),
                vmax,
                km_gly,
            ],
        )
        # model.add_reaction_from_args(
        #     rate_name=enzyme,
        #     function=_rate_glycerate_kinase,
        #     stoichiometry=stoichiometry,
        #     args=[
        #         n.glycerate(),
        #         n.atp(),
        #         n.pga(),
        #         vmax,
        #         km_gly,
        #         km_atp,
        #         ki,
        #     ],
        # )
    else:
        model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
        model.add_parameter(keq := n.keq(ENZYME), 490.0)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_2s_2p,
            stoichiometry=stoichiometry,
            args=[
                n.glycerate(),
                n.atp(),
                n.pga(),
                n.adp(),
                vmax,
                km_gly,  # FIXME: km_atp missing
                kmp,  # FIXME: ki missing
                keq,
            ],
        )
    return model
