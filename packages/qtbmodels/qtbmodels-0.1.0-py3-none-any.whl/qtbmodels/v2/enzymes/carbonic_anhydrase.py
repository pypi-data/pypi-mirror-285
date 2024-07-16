"""name

EC 4.2.1.1

Equilibrator

hco3:co2 is ~50:1 according to Straßburger
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import reversible_mass_action_keq_1s_1p

ENZYME = n.carbonic_anhydrase()


def add_carbonic_anhydrase(model: Model, compartment: str) -> Model:
    model.add_parameter(kf := n.k(ENZYME), 1000)
    model.add_parameter(keq := n.keq(ENZYME), 50)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=reversible_mass_action_keq_1s_1p,
        stoichiometry={
            n.co2(compartment): -1,
            n.hco3(compartment): 1,
        },
        args=[
            n.co2(compartment),
            n.hco3(compartment),
            kf,
            keq,
        ],
    )
    return model
