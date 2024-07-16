"""ERYTHRULOSE_4P <=> ERYTHROSE_4P

EC 5.3.1.34

Equilibrator
Erythrulose-4-phosphate(aq) ⇌ Erythrose-4-phosphate(aq)
Keq = 0.07 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_1s_1p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.e4p_isomerase()


def add_e4p_isomerase(
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
    model.add_parameter(keq := n.keq(ENZYME), 0.07)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.erythrulose_4p(compartment): -1.0,
            #
            n.e4p(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_1s_1p,
        stoichiometry=stoichiometry,
        args=[
            n.erythrulose_4p(compartment),
            n.e4p(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
