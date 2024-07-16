"""name

EC 6.4.1.2

Metacyc:
ACETYL-COA_m + ATP_m + HCO3_m <=> ADP_m + MALONYL-COA_m + PROTON_m + Pi_m

Equilibrator
Acetyl-CoA(aq) + ATP(aq) + HCO3-(aq) ⇌ ADP(aq) + Malonyl-CoA(aq) + Orthophosphate(aq)
Too much uncertainty for HCO3

As a proxy
Acetyl-CoA(aq) + ATP(aq) + CO2(total) ⇌ ADP(aq) + Malonyl-CoA(aq) + Orthophosphate(aq)
Keq = 4e1 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_3s,
    reversible_michaelis_menten_3s_3p,
    reversible_michaelis_menten_3s_3p_1i,
    reversible_michaelis_menten_3s_3p_2i,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.acetyl_coa_carboxyltransfer()


def add_acetyl_coa_carboxyltransfer(
    model: Model,
    mit: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
    *,
    reversible: bool = True,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=30.1,
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        stoichiometry={
            n.acetyl_coa(mit): -1.0,
            n.atp(mit): -1.0,
            n.hco3(mit): -1.0,
            #
            n.adp(mit): 1.0,
            n.malonyl_coa(mit): 1.0,
            n.pi(mit): 1.0,
        },
    )
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.0487)
    if reversible:
        model.add_parameter(keq := n.keq(ENZYME), 40.0)
        model.add_parameter(kmp := n.km(ENZYME, "p"), 0.1)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_3s_3p,
            stoichiometry=stoichiometry,
            args=[
                n.acetyl_coa(mit),
                n.atp(mit),
                n.hco3(mit),
                #
                n.adp(mit),
                n.malonyl_coa(mit),
                n.pi(mit),
                vmax,
                kms,
                kmp,
                keq,
            ],
        )
    else:
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=michaelis_menten_3s,
            stoichiometry=stoichiometry,
            args=[
                n.acetyl_coa(mit),
                n.atp(mit),
                n.hco3(mit),
                vmax,
                kms,
            ],
        )
    return model


def add_acetyl_coa_carboxyltransfer_1i(
    model: Model,
    mit: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=30.1,
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        stoichiometry={
            n.acetyl_coa(mit): -1.0,
            n.atp(mit): -1.0,
            n.hco3(mit): -1.0,
            #
            n.adp(mit): 1.0,
            n.malonyl_coa(mit): 1.0,
            n.pi(mit): 1.0,
        },
    )
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.0487)
    model.add_parameter(keq := n.keq(ENZYME), 40.0)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 0.1)
    model.add_parameter(ki := n.ki(ENZYME), 0.002)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_3s_3p_1i,
        stoichiometry=stoichiometry,
        args=[
            n.acetyl_coa(mit),
            n.atp(mit),
            n.hco3(mit),
            #
            n.adp(mit),
            n.malonyl_coa(mit),
            n.pi(mit),
            vmax,
            kms,
            kmp,
            keq,
            n.formate(),
            ki,
        ],
    )
    return model


def add_acetyl_coa_carboxyltransfer_2i(
    model: Model,
    mit: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=30.1,
        e0=e0,
    ).vmax
    stoichiometry = filter_stoichiometry(
        model,
        stoichiometry={
            n.acetyl_coa(mit): -1.0,
            n.atp(mit): -1.0,
            n.hco3(mit): -1.0,
            #
            n.adp(mit): 1.0,
            n.malonyl_coa(mit): 1.0,
            n.pi(mit): 1.0,
        },
    )
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.0487)
    model.add_parameter(ki1 := n.ki(ENZYME, n.formate()), 0.002)
    model.add_parameter(ki2 := n.ki(ENZYME, n.malonyl_coa()), 0.002)
    model.add_parameter(keq := n.keq(ENZYME), 40.0)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 0.1)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_3s_3p_2i,
        stoichiometry=stoichiometry,
        args=[
            n.acetyl_coa(mit),
            n.atp(mit),
            n.hco3(mit),
            n.adp(mit),
            n.malonyl_coa(mit),
            n.pi(mit),
            vmax,
            kms,
            kmp,
            keq,
            n.formate(),
            ki1,
            n.malonyl_coa(),
            ki2,
        ],
    )
    return model
