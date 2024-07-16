from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import mass_action_1s

from ._utils import filter_stoichiometry

ENZYME = n.quencher()


def add_quenching_reaction(
    model: Model,
    compartment: str,
) -> Model:
    model.add_parameter(k := n.k(ENZYME), 1.0)

    stoichiometry = filter_stoichiometry(
        model,
        {
            # Substrates
            n.energy(compartment): -1.0,
            # Products
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=mass_action_1s,
        stoichiometry=stoichiometry,
        args=[
            n.energy(compartment),
            k,
        ],
    )
    return model
