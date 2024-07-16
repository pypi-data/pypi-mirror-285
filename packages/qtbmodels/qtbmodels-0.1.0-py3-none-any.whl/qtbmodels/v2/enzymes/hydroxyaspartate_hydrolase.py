"""(2R,3S)-beta-Hydroxyasparate hydro-lyase (Iminosuccinate forming)

EC FIXME

Equilibrator
3-hydroxyaspartate(aq) ⇌ Iminoaspartate(aq) + H2O(l)
Keq = 4.0 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_1s_1p

from ._utils import build_vmax

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.hydroxyaspartate_hydrolase()


def add_hydroxyaspartate_hydrolase(
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
    model.add_parameter(keq := n.keq(ENZYME), 4.0)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_1s_1p,
        stoichiometry={
            n.hydroxyaspartate(per): -1,
            n.iminoaspartate(per): 1,
        },
        args=[
            n.hydroxyaspartate(per),
            n.iminoaspartate(per),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
