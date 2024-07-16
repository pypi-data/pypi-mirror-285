"""GCS: atp + coa + glyclt -> Diphosphate + amp + glyccoa

dG' = 9.25
Keq = 0.024
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_3s,
    reversible_michaelis_menten_3s_3p,
)

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glycolyl_coa_synthetase()


def add_glycolyl_coa_synthetase_irrev(
    model: Model,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model, enzyme_name=ENZYME, enzyme_factor=enzyme_factor, kcat=4.0, e0=e0
    ).vmax
    model.add_parameter(kms := n.km(ENZYME), 13)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_3s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.atp(chl_stroma): -1,
                n.coa(chl_stroma): -1,
                n.glycolate(chl_stroma): -1,
                n.glycolyl_coa(chl_stroma): 1,
                n.ppi(chl_stroma): 1,
                n.amp(chl_stroma): 1,
            },
        ),
        args=[
            n.atp(chl_stroma),
            n.coa(chl_stroma),
            n.glycolate(chl_stroma),
            vmax,
            kms,
        ],
    )
    return model


def add_glycolyl_coa_synthetase(
    model: Model,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    vmax = build_vmax(
        model, enzyme_name=ENZYME, enzyme_factor=enzyme_factor, kcat=4.0, e0=e0
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 13)
    model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
    model.add_parameter(keq := n.keq(ENZYME), 0.024)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_michaelis_menten_3s_3p,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.atp(chl_stroma): -1,
                n.coa(chl_stroma): -1,
                n.glycolate(chl_stroma): -1,
                n.glycolyl_coa(chl_stroma): 1,
                n.ppi(chl_stroma): 1,
                n.amp(chl_stroma): 1,
            },
        ),
        args=[
            n.atp(chl_stroma),
            n.coa(chl_stroma),
            n.glycolate(chl_stroma),
            #
            n.glycolyl_coa(chl_stroma),
            n.ppi(chl_stroma),
            n.amp(chl_stroma),
            vmax,
            kms,
            kmp,
            keq,
        ],
    )
    return model
