"""Plastid terminal oxidase

2 QH2 + O2 -> 2 Q + 2 H2O
"""

from modelbase.ode import Model

from qtbmodels import names as n

ENZYME = n.ptox()


def _rate_ptox(
    pq_red: float,
    kPTOX: float,
    O2: float,
) -> float:
    """calculates reaction rate of PTOX"""
    return pq_red * kPTOX * O2


def add_ptox(model: Model, chl_lumen: str) -> Model:
    model.add_parameter("kPTOX", 0.01)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_ptox,
        stoichiometry={n.pq_ox(): 1},
        args=[n.pq_red(), "kPTOX", n.o2(chl_lumen)],
    )
    return model
