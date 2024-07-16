"""GCC: glyccoa + atp + hco3 -> tarcoa + adp + pi

dG' = -20.86
Keq = 4515.62
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from qtbmodels import names as n
from qtbmodels.shared import reversible_michaelis_menten_3s_3p

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glycolyl_coa_carboxylase()


def add_glycolyl_coa_carboxylase(
    model: Model,
    variant: Literal["M5", "L100N", "optimal"],
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    stoichiometry = {
        n.glycolyl_coa(chl_stroma): -1.0,
        # n.atp(chl_stroma): -1.0,
        n.hco3(chl_stroma): -1.0,
        n.tartronyl_coa(chl_stroma): 1.0,
        # n.adp(chl_stroma): 1.0,
        n.pi(chl_stroma): 1.0,
    }

    if variant == "M5":
        stoichiometry |= {
            n.atp(chl_stroma): -3.9,
            n.adp(chl_stroma): 3.9,
        }

        kcat = 5.6
        keq_val = 1830000000000.0
    elif variant == "L100N":
        stoichiometry |= {
            n.atp(chl_stroma): -1.7,
            n.adp(chl_stroma): 1.7,
        }
        # ATP/CO2 is 1.71
        kcat = 4.0
        keq_val = 892
    elif variant == "optimal":
        stoichiometry |= {
            n.atp(chl_stroma): -1,
            n.adp(chl_stroma): 1,
        }
        kcat = 5.6
        keq_val = 892

    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        enzyme_factor=enzyme_factor,
        kcat=kcat,
        e0=e0,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.15)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
    model.add_parameter(keq := n.keq(ENZYME), keq_val)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_3s_3p,
        stoichiometry=filter_stoichiometry(model, stoichiometry),
        args=[
            # substrates
            n.glycolyl_coa(chl_stroma),
            n.hco3(chl_stroma),
            n.atp(chl_stroma),
            # products
            n.tartronyl_coa(chl_stroma),
            n.adp(chl_stroma),
            n.pi(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
