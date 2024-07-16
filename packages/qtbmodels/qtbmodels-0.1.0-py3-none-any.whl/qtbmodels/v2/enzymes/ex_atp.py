from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import mass_action_1s

ENZYME = n.ex_atp()


def add_atp_consumption(
    model: Model, *, compartment: str, k_val: float
) -> Model:
    model.add_parameter(k := n.k(ENZYME), k_val)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=mass_action_1s,
        stoichiometry={
            n.atp(compartment): -1,
        },
        args=[
            n.atp(compartment),
            k,
        ],
    )
    return model
