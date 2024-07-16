"""glycine decarboxylase

2 Glycine + NAD + 2 H2O ⇌ Serine + NH3 + NADH + CO2

Equilibrator
2 Glycine(aq) + NAD(aq) + 2 H2O(l) ⇌ Serine(aq) + NH3(aq) + NADH(aq) + CO2(total)
Keq = 2.4e-4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_1s,
    michaelis_menten_2s,
    reversible_michaelis_menten_2s_4p,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glycine_decarboxylase()


def add_glycine_decarboxylase_yokota(
    model: Model,
    kcat: float = 100.0,
    e0: float = 1.0,
    enzyme_factor: str | None = None,
) -> Model:
    model.add_parameter(kms := n.km(ENZYME, "s"), 6.0)
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=kcat,
        enzyme_factor=enzyme_factor,
        e0=e0,
    ).vmax

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.glycine(): -2.0,
            #
            n.serine(): 1.0,
        },
    )
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_1s,
        stoichiometry=stoichiometry,
        args=[
            n.glycine(),
            vmax,
            kms,
        ],
    )
    return model


def add_glycine_decarboxylase_irreversible(
    model: Model,
    *,
    nadph_hack: bool = False,
    kcat: float = 100.0,
    e0: float = 1.0,
    enzyme_factor: str | None = None,
) -> Model:
    model.add_parameter(kms := n.km(ENZYME, "s"), 6.0)
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=kcat,
        enzyme_factor=enzyme_factor,
        e0=e0,
    ).vmax

    if nadph_hack:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.glycine(): -2.0,
                n.nadp(): -1.0,
                n.serine(): 1.0,
                n.nh4(): 1.0,
                n.nadph(): 1.0,
                n.co2(): 1.0,
            },
        )
    else:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.glycine(): -2.0,
                n.nad(): -1.0,
                n.serine(): 1.0,
                n.nh4(): 1.0,
                n.nadh(): 1.0,
                n.co2(): 1.0,
            },
        )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_2s,
        stoichiometry=stoichiometry,
        args=[
            n.glycine(),
            n.nad(),
            vmax,
            kms,
        ],
    )

    return model


def add_glycine_decarboxylase(
    model: Model,
    *,
    nadph_hack: bool = False,
    kcat: float = 100.0,
    e0: float = 1.0,
    enzyme_factor: str | None = None,
) -> Model:
    model.add_parameter(kms := n.km(ENZYME, "s"), 6.0)
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=kcat,
        enzyme_factor=enzyme_factor,
        e0=e0,
    ).vmax

    if nadph_hack:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.glycine(): -2.0,
                n.nadp(): -1.0,
                n.serine(): 1.0,
                n.nh4(): 1.0,
                n.nadph(): 1.0,
                n.co2(): 1.0,
            },
        )
    else:
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.glycine(): -2.0,
                n.nad(): -1.0,
                n.serine(): 1.0,
                n.nh4(): 1.0,
                n.nadh(): 1.0,
                n.co2(): 1.0,
            },
        )

    model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
    model.add_parameter(keq := n.keq(ENZYME), 0.00024)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_2s_4p,
        stoichiometry=stoichiometry,
        args=[
            n.glycine(),
            n.nad(),
            n.serine(),
            n.nh4(),
            n.nadh(),
            n.co2(),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
