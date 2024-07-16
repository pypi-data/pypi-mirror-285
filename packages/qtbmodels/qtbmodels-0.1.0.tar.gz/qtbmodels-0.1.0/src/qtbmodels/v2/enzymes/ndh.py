"""NAD(P)H dehydrogenase-like complex (NDH)

PQH2 -> PQ

"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import mass_action_1s

ENZYME = n.ndh()


def add_ndh(model: Model) -> Model:
    model.add_parameter("kNDH", 0.002)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=mass_action_1s,
        stoichiometry={
            n.pq_ox(): -1,
        },
        args=[
            n.pq_ox(),
            "kNDH",
        ],
    )
    return model
