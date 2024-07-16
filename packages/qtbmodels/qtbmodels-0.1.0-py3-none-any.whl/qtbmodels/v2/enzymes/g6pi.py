"""phosphohexomutase

EC 5.3.1.9

Equilibrator
D-Fructose 6-phosphate(aq) ⇌ D-Glucose 6-phosphate(aq)
Keq = 3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import rapid_equilibrium_1s_1p

from ._utils import add_parameter_if_missing

ENZYME = n.g6pi()


def add_glucose_6_phosphate_isomerase(
    model: Model, *, chl_stroma: str
) -> Model:
    model.add_parameter("keq_g6p_isomerase", 2.3)
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_1s_1p,
        stoichiometry={
            n.f6p(chl_stroma): -1,
            n.g6p(chl_stroma): 1,
        },
        args=[
            n.f6p(chl_stroma),
            n.g6p(chl_stroma),
            "k_rapid_eq",
            "keq_g6p_isomerase",
        ],
    )
    return model
