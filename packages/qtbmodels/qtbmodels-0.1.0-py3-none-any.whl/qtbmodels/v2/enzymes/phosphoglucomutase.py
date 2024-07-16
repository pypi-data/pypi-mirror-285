"""glucose phosphomutase

EC 5.4.2.2

G6P <=> G1P

Equilibrator
Glucose 6-phosphate(aq) ⇌ D-Glucose-1-phosphate(aq)
Keq = 0.05 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import rapid_equilibrium_1s_1p

from ._utils import add_parameter_if_missing

ENZYME = n.phosphoglucomutase()


def add_phosphoglucomutase(model: Model, *, chl_stroma: str) -> Model:
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)

    model.add_parameter(keq := n.keq(ENZYME), 0.058)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_1s_1p,
        stoichiometry={
            n.g6p(chl_stroma): -1,
            n.g1p(chl_stroma): 1,
        },
        args=[
            n.g6p(chl_stroma),
            n.g1p(chl_stroma),
            "k_rapid_eq",
            keq,
        ],
    )
    return model
