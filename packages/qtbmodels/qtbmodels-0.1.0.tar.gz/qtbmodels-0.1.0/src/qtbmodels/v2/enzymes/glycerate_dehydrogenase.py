"""glycerate dehydrogenase

NADH + Hydroxypyruvate <=> NAD  + D-Glycerate

Equilibrator
NADH(aq) + Hydroxypyruvate(aq) ⇌ NAD(aq) + D-Glycerate(aq)
Keq = 8.7e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
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

ENZYME = n.glycerate_dehydrogenase()


def add_hpa_outflux(
    model: Model,
    *,
    per: str = "",
    kcat: float = 398.0,
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
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.12)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_1s,
        stoichiometry={n.hydroxypyruvate(per): -1.0},
        args=[
            n.hydroxypyruvate(per),
            vmax,
            kms,
        ],
    )

    return model


def add_glycerate_dehydrogenase(
    model: Model,
    *,
    irreversible: bool,
    nadph_hack: bool,
    kcat: float = 398.0,
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
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.12)

    if nadph_hack:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.nadph(): -1.0,
                n.hydroxypyruvate(): -1.0,
                n.nadp(): 1.0,
                n.glycerate(): 1.0,
            },
        )
    else:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.nadh(): -1.0,
                n.hydroxypyruvate(): -1.0,
                n.nad(): 1.0,
                n.glycerate(): 1.0,
            },
        )

    if irreversible:
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=michaelis_menten_2s,
            stoichiometry=stoichiometry,
            args=[
                n.hydroxypyruvate(),
                n.nadh(),
                vmax,
                kms,
            ],
        )
    else:
        model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
        model.add_parameter(keq := n.keq(ENZYME), 87000.0)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_2s_2p,
            stoichiometry=stoichiometry,
            args=[
                n.hydroxypyruvate(),
                n.nadh(),
                n.glycerate(),
                n.nad(),
                vmax,
                kms,
                kmp,
                keq,
            ],
        )

    return model
