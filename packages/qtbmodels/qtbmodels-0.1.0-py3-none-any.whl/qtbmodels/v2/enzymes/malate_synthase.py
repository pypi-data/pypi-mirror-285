"""malate synthase

EC 2.3.3.9

Equilibrator
------------
    H2O + Acetyl-CoA + Glyoxylate <=> CoA + (S)-Malate
    Keq = 6.0e6 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.malate_synthase()


def add_malate_synthase(
    model: Model,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=27.8,  # bacillus
        e0=e0,
    ).vmax

    model.add_parameter(kms := n.km(ENZYME, "s"), 0.098)  # Zea mays
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1.0)  # FIXME
    model.add_parameter(keq := n.keq(ENZYME), 6.0e6)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.acetyl_coa(chl_stroma): -1,
            n.glyoxylate(chl_stroma): -1,
            #
            n.coa(chl_stroma): 1,
            n.malate(chl_stroma): 1,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.acetyl_coa(chl_stroma),
            n.glyoxylate(chl_stroma),
            n.coa(chl_stroma),
            n.malate(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
