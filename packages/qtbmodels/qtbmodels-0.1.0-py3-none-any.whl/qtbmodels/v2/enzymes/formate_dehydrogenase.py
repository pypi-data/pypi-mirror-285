"""name

EC 1.17.1.9

Equilibrator
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_2s_2p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.formate_dehydrogenase()


def add_formate_dehydrogenase(
    model: Model,
    per: str,
    mit: str,
    *,
    nadph_hack: bool,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    """EC 1.17.1.9
    Metacyc: 1.2.1.2-RXN
    FORMATE + NAD ⇌ CARBON-DIOXIDE + NADH

    Equilibrator
    NAD (aq) + Formate(aq) + H2O(l) ⇌ NADH(aq) + CO2(total)
    Keq = 8.7e3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=2.9,
        e0=e0,
    ).vmax
    if nadph_hack:
        stoichiometry = filter_stoichiometry(
            model,
            stoichiometry={
                n.formate(mit): -1.0,
                n.nadp(mit): -1.0,
                #
                n.nadph(mit): 1.0,
                n.co2(mit): 1.0,
            },
        )
    else:
        stoichiometry = filter_stoichiometry(
            model,
            stoichiometry={
                n.formate(mit): -1.0,
                n.nad(mit): -1.0,
                #
                n.nadh(mit): 1.0,
                n.co2(mit): 1.0,
            },
        )
    model.add_parameter(keq := n.keq(ENZYME), 8700.0)
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.011)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 0.18)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_2p,
        stoichiometry=stoichiometry,
        args=[
            n.nad(per),
            n.formate(per),
            n.nadh(per),
            n.co2(mit),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    model.scale_parameter(n.e0(ENZYME), 0.5)
    return model
