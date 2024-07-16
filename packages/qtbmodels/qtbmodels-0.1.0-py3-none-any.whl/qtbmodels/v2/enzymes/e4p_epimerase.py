"""name

EC 5.3.1.33

Equilibrator
Erythrulose 1-phosphate(aq) ⇌ Erythrulose-4-phosphate(aq)
Keq = 5e1 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_1s_1p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.e4p_epimerase()


def add_e4p_epimerase(
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
    model.add_parameter(keq := n.keq(ENZYME), 5e1)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.erythrulose_1p(compartment): -1.0,
            #
            n.erythrulose_4p(compartment): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_1s_1p,
        stoichiometry=stoichiometry,
        args=[
            n.erythrulose_1p(compartment),
            n.erythrulose_4p(compartment),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
