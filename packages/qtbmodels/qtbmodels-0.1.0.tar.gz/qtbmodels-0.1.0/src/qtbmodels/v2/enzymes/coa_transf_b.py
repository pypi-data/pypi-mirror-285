"""EC 2.8.3.5
Metacyc: COA-TRANSF-B
3-KETOBUTYRATE_m + SUC-COA_m --> ACETOACETYL-COA_m + SUC_m

Equilibrator
Acetoacetate(aq) + Succinyl-CoA(aq) ⇌ Acetoacetyl-CoA(aq) + Succinate(aq)
Keq = 6.1e-3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

ATP-hydrolysis variant
Acetoacetate(aq) + Succinyl-CoA(aq) + ATP(aq) + H2O(l) ⇌ Acetoacetyl-CoA(aq) + Succinate(aq) + ADP(aq) + Pi(aq)
Keq = 9.6e2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
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

ENZYME = n.coa_transf_b()


def add_coa_transf_b_irrev(
    model: Model,
    mit: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=98.3,
        e0=e0,
    ).vmax

    model.add_parameter(kms := n.km(ENZYME, "s"), 0.1)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_2s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.acetoacetate(mit): -1,
                n.succinyl_coa(mit): -1,
                n.acetoacetyl_coa(mit): 1,
                n.succinate(mit): 1,
            },
        ),
        args=[
            n.acetoacetate(mit),
            n.succinyl_coa(mit),
            vmax,
            kms,
        ],
    )
    return model


def add_coa_transf_b(
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
        kcat=98.3,
        e0=e0,
    ).vmax

    model.add_parameter(kms := n.km(ENZYME, "s"), 0.1)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 0.2)

    function: Callable[..., float]
    if variant == "wt":
        model.add_parameter(keq := n.keq(ENZYME), 0.0061)
        function = reversible_michaelis_menten_2s_2p
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.acetoacetate(mit): -1,
                n.succinyl_coa(mit): -1,
                n.acetoacetyl_coa(mit): 1,
                n.succinate(mit): 1,
            },
        )
        args = [
            n.acetoacetate(mit),
            n.succinyl_coa(mit),
            n.acetoacetyl_coa(mit),
            n.succinate(mit),
            vmax,
            kms,
            kmp,
            keq,
        ]
    else:
        model.add_parameter(keq := n.keq(ENZYME), 9.6e2)
        function = reversible_michaelis_menten_3s_3p
        stoichiometry = filter_stoichiometry(
            model,
            {
                n.acetoacetate(mit): -1,
                n.succinyl_coa(mit): -1,
                n.atp(mit): -1,
                n.acetoacetyl_coa(mit): 1,
                n.succinate(mit): 1,
                n.adp(mit): 1,
            },
        )
        args = [
            n.acetoacetate(mit),
            n.succinyl_coa(mit),
            n.atp(mit),
            #
            n.acetoacetyl_coa(mit),
            n.succinate(mit),
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
