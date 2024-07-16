from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import diffusion

ENZYME = n.co2_dissolving()


def add_co2_dissolving(model: Model, *, chl_stroma: str) -> Model:
    model.add_parameter(k := n.k(ENZYME), 4.5)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=diffusion,
        stoichiometry={
            n.co2(chl_stroma): 1,
        },
        args=[
            n.co2(chl_stroma),
            n.co2_atmosphere(),
            k,
        ],
    )
    return model
