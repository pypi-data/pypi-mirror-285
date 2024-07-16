"""glycine transaminase

EC 2.6.1.4

Equilibrator
L-Glutamate(aq) + Glyoxylate(aq) ⇌ 2-Oxoglutarate(aq) + Glycine(aq)
Keq = 30 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_1s,
    michaelis_menten_2s,
    reversible_michaelis_menten_2s_2p,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glycine_transaminase()


def add_glycine_transaminase_yokota(
    model: Model,
    *,
    kcat: float = 143.0,
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
    model.add_parameter(kms := n.km(ENZYME, "s"), 3.0)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.glyoxylate(): -1.0,
            n.glycine(): 1.0,
        },
    )
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_1s,
        stoichiometry=stoichiometry,
        args=[
            n.glyoxylate(),
            vmax,
            kms,
        ],
    )
    return model


def add_glycine_transaminase_irreversible(
    model: Model,
    *,
    kcat: float = 143.0,
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
    model.add_parameter(kms := n.km(ENZYME, "s"), 3.0)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.glutamate(): -1.0,
            n.glyoxylate(): -1.0,
            n.oxoglutarate(): 1.0,
            n.glycine(): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_2s,
        stoichiometry=stoichiometry,
        args=[
            n.glyoxylate(),
            n.glutamate(),
            vmax,
            kms,
        ],
    )

    return model


def add_glycine_transaminase(
    model: Model,
    *,
    kcat: float = 143.0,
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
    model.add_parameter(kms := n.km(ENZYME, "s"), 3.0)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.glutamate(): -1.0,
            n.glyoxylate(): -1.0,
            n.oxoglutarate(): 1.0,
            n.glycine(): 1.0,
        },
    )

    model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
    model.add_parameter(keq := n.keq(ENZYME), 30)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.glyoxylate(),
            n.glutamate(),
            n.glycine(),
            n.oxoglutarate(),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )

    return model
