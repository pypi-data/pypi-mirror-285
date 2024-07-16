"""name

EC 1.1.3.15

Equilibrator
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from qtbmodels import names as n
from qtbmodels.shared import michaelis_menten_1s, michaelis_menten_2s

from ._utils import build_vmax

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.glycolate_oxidase()


def add_glycolate_oxidase(
    model: Model,
    *,
    chl_stroma: str = "",
    include_o2: bool = False,
    kcat: float = 100.0,
    e0: float = 1.0,
    enzyme_factor: str | None = None,
) -> Model:
    """glycolate oxidase

    O2(per) + Glycolate(chl) <=> H2O2(per) + Glyoxylate(per)

    Equilibrator
    O2(aq) + Glycolate(aq) ⇌ H2O2(aq) + Glyoxylate(aq)
    Keq = 3e15 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=kcat,
        e0=e0,
        enzyme_factor=enzyme_factor,
    ).vmax
    model.add_parameter(km := n.km(ENZYME, "s"), 0.06)

    function: Callable[..., float]
    if not include_o2:
        args = [
            n.glycolate(),
            vmax,
            km,
        ]
        function = michaelis_menten_1s
    else:
        args = [
            n.glycolate(),
            n.o2(chl_stroma),
            vmax,
            km,
        ]
        function = michaelis_menten_2s

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=function,
        stoichiometry={
            n.glycolate(): -1,
            n.glyoxylate(): 1,
            n.h2o2(): 1,
        },
        args=args,
    )
    return model
