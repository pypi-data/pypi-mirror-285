"""phosphoglycolate phosphatase, EC 3.1.3.18

H2O(chl) + PGO(chl) <=> Orthophosphate(chl) + Glycolate(chl)

Equilibrator
H2O(l) + PGO(aq) ⇌ Orthophosphate(aq) + Glycolate(aq)
Keq = 3.1e5 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.shared import (
    michaelis_menten_1s_1i,
    reversible_michaelis_menten_1s_1p_1i,
    value,
)

from ._utils import build_vmax

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.phosphoglycolate_phosphatase()


def add_phosphoglycolate_influx(
    model: Model, *, chl_stroma: str = ""
) -> Model:
    model.add_parameter("pgo_influx", 60.0)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=value,
        stoichiometry={
            n.glycolate(chl_stroma): 1,
        },
        args=["pgo_influx"],
    )
    return model


def add_phosphoglycolate_phosphatase(
    model: Model,
    *,
    irreversible: bool,
    e0: float = 1.0,
    kcat: float = 292.0,
    enzyme_factor: str | None = None,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=kcat,
        e0=e0,
        enzyme_factor=enzyme_factor,
    ).vmax
    model.add_parameter(kms := n.km(ENZYME, "s"), 0.029)
    model.add_parameter(ki := n.ki(ENZYME, n.pi()), 12.0)

    stoichiometry = {
        n.pgo(): -1.0,
        n.glycolate(): 1.0,
    }

    if irreversible:
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=michaelis_menten_1s_1i,
            stoichiometry=stoichiometry,
            args=[
                n.pgo(),
                n.pi(),
                vmax,
                kms,
                ki,
            ],
        )
    else:
        model.add_parameter(kmp := n.km(ENZYME, "p"), 1)
        model.add_parameter(keq := n.keq(ENZYME), 310000.0)

        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=reversible_michaelis_menten_1s_1p_1i,
            stoichiometry=stoichiometry,
            args=[
                n.pgo(),
                n.glycolate(),
                n.pi(),
                vmax,
                kms,
                kmp,
                ki,
                keq,
            ],
        )
    return model
