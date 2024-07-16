"""serine glyoxylate transaminase

Glyoxylate + L-Serine <=> Glycine + Hydroxypyruvate

EC 2.6.1.45

Equilibrator
Glyoxylate(aq) + Serine(aq) ⇌ Glycine(aq) + Hydroxypyruvate(aq)
Keq = 6 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import ping_pong_bi_bi, reversible_michaelis_menten_2s_2p

from ._utils import build_vmax

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.serine_glyoxylate_transaminase()


def add_serine_glyoxylate_transaminase_irreversible(
    model: Model,
    *,
    kcat: float = 159.0,
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
    model.add_parameter(kms1 := "kms_transaminase_glyxoylate", 0.15)
    model.add_parameter(kms2 := "kms_transaminase_serine", 2.72)
    stoichiometry = {
        n.glyoxylate(): -1.0,
        n.serine(): -1.0,
        n.glycine(): 1.0,
        n.hydroxypyruvate(): 1.0,
    }

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=ping_pong_bi_bi,
        stoichiometry=stoichiometry,
        args=[
            n.glyoxylate(),
            n.serine(),
            vmax,
            kms1,
            kms2,
        ],
    )

    return model


def add_serine_glyoxylate_transaminase(
    model: Model,
    *,
    kcat: float = 159.0,
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
    model.add_parameter(kms1 := "kms_transaminase_glyxoylate", 0.15)
    model.add_parameter(kms2 := "kms_transaminase_serine", 2.72)  # noqa: F841
    stoichiometry = {
        n.glyoxylate(): -1.0,
        n.serine(): -1.0,
        n.glycine(): 1.0,
        n.hydroxypyruvate(): 1.0,
    }

    model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
    model.add_parameter(keq := n.keq(ENZYME), 6)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.glyoxylate(),
            n.serine(),
            n.glycine(),
            n.hydroxypyruvate(),
            vmax,
            kms1,  # FIXME: kms2 missing
            kmp,
            keq,
        ],
    )
    return model
