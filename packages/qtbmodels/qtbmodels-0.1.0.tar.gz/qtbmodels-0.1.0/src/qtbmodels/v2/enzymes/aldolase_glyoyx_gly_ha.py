"""EC: 4.1.3.14

Equilibrator
Glyoxylate(aq) + Glycine(aq) ⇌ 3-hydroxyaspartate(aq)
Keq = 4.0 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_1p

from ._utils import build_vmax

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.hydroxyaspartate_aldolase()


def add_hydroxyaspartate_aldolase(
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
    model.add_parameter(kmp := n.km(ENZYME, "p"), 2.3)
    model.add_parameter(keq := n.keq(ENZYME), 4.0)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_1p,
        stoichiometry={
            n.glyoxylate(per): -1,
            n.glycine(per): -1,
            n.hydroxyaspartate(per): 1,
        },
        args=[
            n.glyoxylate(per),
            n.glycine(per),
            n.hydroxyaspartate(per),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
