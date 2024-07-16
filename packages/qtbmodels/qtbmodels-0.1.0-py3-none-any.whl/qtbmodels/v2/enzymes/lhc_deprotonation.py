from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import mass_action_1s

from ._utils import filter_stoichiometry

ENZYME = n.lhc_deprotonation()


def add_lhc_deprotonation(model: Model) -> Model:
    model.add_parameter("k_lhc_deprotonation", 0.0096)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=mass_action_1s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.psbs_pr(): -1,
                n.psbs_de(): 1,
            },
        ),
        args=[
            n.psbs_pr(),
            "k_lhc_deprotonation",
        ],
    )
    return model
