"""EC 2.1.2.1
Metacyc: GLYOHMETRANS-RXN
METHYLENE-THF_m + GLY_m + WATER_m <=> SER_m + THF

Equilibrator
Wildtype
    5,10-Methylenetetrahydrofolate(aq) + Glycine(aq) + H2O(l) ⇌ Serine(aq) + THF(aq)
    Keq = 0.07 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

ATP-hydrolysis variant
    5,10-Methylenetetrahydrofolate(aq) + Glycine(aq) + ATP(aq) + 2 H2O(l)
    ⇌ Serine(aq) + THF(aq) + ADP(aq) + Pi(aq)
    Keq = 1e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Literal

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_2s,
    reversible_michaelis_menten_2s_2p,
    reversible_michaelis_menten_3s_3p,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glycine_hydroxymethyltransferase()


def add_glycine_hydroxymethyltransferase_irrev(
    model: Model,
    per: str,
    mit: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=5,
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.68)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_2s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.methylene_thf(per): -1,
                n.glycine(per): -1,
                n.serine(per): 1,
                n.thf(mit): 1,
            },
        ),
        args=[
            n.methylene_thf(per),
            n.glycine(per),
            vmax,
            kms,
        ],
    )
    return model


def add_glycine_hydroxymethyltransferase(
    model: Model,
    per: str,
    mit: str,
    variant: Literal["wt", "atp-hydrolysis"] = "wt",
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=5,
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.68)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 0.28)

    function: Callable[..., float]
    if variant == "wt":
        function = reversible_michaelis_menten_2s_2p
        model.add_parameter(keq := n.keq(ENZYME), 0.07)
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.methylene_thf(per): -1,
                n.glycine(per): -1,
                n.serine(per): 1,
                n.thf(mit): 1,
            },
        )
        args = [
            n.methylene_thf(per),
            n.glycine(per),
            n.serine(per),
            n.thf(mit),
            vmax,
            kms,
            kmp,
            keq,
        ]
    else:
        function = reversible_michaelis_menten_3s_3p
        model.add_parameter(keq := n.keq(ENZYME), 1e4)
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.methylene_thf(per): -1,
                n.glycine(per): -1,
                n.atp(per): -1,
                #
                n.serine(per): 1,
                n.thf(mit): 1,
                n.adp(per): 1,
            },
        )
        args = [
            n.methylene_thf(per),
            n.glycine(per),
            n.atp(per),
            #
            n.serine(per),
            n.thf(mit),
            n.adp(per),
            vmax,
            kms,
            kmp,
            keq,
        ]

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=function,
        stoichiometry=stoichiometry,
        args=args,
    )
    return model
