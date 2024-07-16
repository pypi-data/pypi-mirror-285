"""name

EC 2.7.9.1

Equilibrator
Pyruvate(aq) + ATP(aq) + Orthophosphate(aq) ⇌ PEP(aq) + AMP(aq) + Diphosphate(aq)
Keq = 9.6e-3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_3s_3p

from ._utils import build_vmax

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.pyruvate_phosphate_dikinase()


def add_pyruvate_phosphate_dikinase(
    model: Model,
    chl_stroma: str,
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
    model.add_parameter(keq := n.keq(ENZYME), 0.0096)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_3s_3p,
        stoichiometry={
            n.pyruvate(chl_stroma): -1,
            n.atp(chl_stroma): -1,
            n.pep(chl_stroma): 1,
        },
        args=[
            n.pyruvate(chl_stroma),
            n.atp(chl_stroma),
            n.pi(chl_stroma),
            n.pep(chl_stroma),
            n.amp(chl_stroma),
            n.ppi(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
