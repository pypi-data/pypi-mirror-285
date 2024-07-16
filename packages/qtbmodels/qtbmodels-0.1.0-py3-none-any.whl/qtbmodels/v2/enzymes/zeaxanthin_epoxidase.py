"""Zeaxanthin Epoxidase (stroma):
Zeaxanthin + NADPH + O2 -> Anteraxanthin + NADP + H2O
Antheraxanthin + NADPH + O2 -> Violaxanthin + NADP + H2O
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import mass_action_1s

ENZYME = n.zeaxanthin_epoxidase()


def add_zeaxanthin_epoxidase(model: Model) -> Model:
    model.add_parameter(k := "kEpoxZ", 0.00024)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=mass_action_1s,
        stoichiometry={
            n.vx(): 1,
        },
        args=[
            n.zx(),
            k,
        ],
    )
    return model
