"""EC 2.8.3.16?
Metacyc: COA-TRANSF-A
FORMYL_COA_m + SUC_m --> FORMATE_m + SUC-COA_m

Equilibrator
------------
Wildtype
    Formyl-CoA(aq) + Succinate(aq) ⇌ Formate(aq) + Succinyl-CoA(aq)
    Keq = 4.6e-4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

ATP-hydrolysis variant
    Formyl-CoA + Succinate + ATP + H2O <=> Formate + Succinyl-CoA + ADP + Pi
    Keq = 7e+01 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

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

ENZYME = n.coa_transf_a()


def add_coa_transf_a_irrev(
    model: Model,
    mit: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=1.0,
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 1)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_2s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.formyl_coa(mit): -1,
                n.succinate(mit): -1,
                n.formate(mit): 1,
                n.succinyl_coa(mit): 1,
            },
        ),
        args=[
            n.formyl_coa(mit),
            n.succinate(mit),
            vmax,
            kms,
        ],
    )
    return model


def add_coa_transf_a(
    model: Model,
    mit: str,
    variant: Literal["wt", "atp-hydrolysis"] = "wt",
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=1.0,
        e0=e0,
    ).vmax

    model.add_parameter(kms := n.km(ENZYME, "s"), 1)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1)

    function: Callable[..., float]
    if variant == "wt":
        model.add_parameter(keq := n.keq(ENZYME), 0.00046)
        function = reversible_michaelis_menten_2s_2p
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.formyl_coa(mit): -1,
                n.succinate(mit): -1,
                n.formate(mit): 1,
                n.succinyl_coa(mit): 1,
            },
        )
        args = [
            n.formyl_coa(mit),
            n.succinate(mit),
            n.formate(mit),
            n.succinyl_coa(mit),
            vmax,
            kms,
            kmp,
            keq,
        ]
    else:
        model.add_parameter(keq := n.keq(ENZYME), 7e1)
        function = reversible_michaelis_menten_3s_3p
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.formyl_coa(mit): -1,
                n.succinate(mit): -1,
                n.atp(mit): -1,
                n.formate(mit): 1,
                n.succinyl_coa(mit): 1,
                n.adp(mit): 1,
            },
        )
        args = [
            n.formyl_coa(mit),
            n.succinate(mit),
            n.atp(mit),
            #
            n.formate(mit),
            n.succinyl_coa(mit),
            n.adp(mit),
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
