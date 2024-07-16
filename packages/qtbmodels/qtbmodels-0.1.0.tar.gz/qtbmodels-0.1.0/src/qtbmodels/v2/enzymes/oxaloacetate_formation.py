"""Spontaneous reaction

EC FIXME

Equilibrator
Iminoaspartate(aq) + H2O(l) ⇌ Oxaloacetate(aq) + NH3(aq)
Keq = 7.1e3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_1s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.oxaloacetate_formation()


def add_oxaloacetate_formation(
    model: Model,
    per: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=1.0,
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 1.0)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1.0)
    model.add_parameter(keq := n.keq(ENZYME), 7100.0)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_1s_2p,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.iminoaspartate(per): -1,
                #
                n.oxaloacetate(per): 1,
                n.nh4(per): 1,
            },
        ),
        args=[
            n.iminoaspartate(per),
            n.oxaloacetate(per),
            n.nh4(per),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
