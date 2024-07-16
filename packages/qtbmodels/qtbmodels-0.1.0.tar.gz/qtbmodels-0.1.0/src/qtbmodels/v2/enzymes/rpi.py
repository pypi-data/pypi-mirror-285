"""ribose-5-phosphate isomerase

EC 5.3.1.6

Equilibrator
    D-Ribose 5-phosphate(aq) ⇌ D-Ribulose 5-phosphate(aq)
    Keq = 0.4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import rapid_equilibrium_1s_1p

from ._utils import add_parameter_if_missing

ENZYME = n.ribose_phosphate_isomerase()


def add_ribose_5_phosphate_isomerase(
    model: Model, *, chl_stroma: str
) -> Model:
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)

    model.add_parameter(keq := n.keq(ENZYME), 0.4)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_1s_1p,
        stoichiometry={
            n.r5p(chl_stroma): -1,
            n.ru5p(chl_stroma): 1,
        },
        args=[
            n.r5p(chl_stroma),
            n.ru5p(chl_stroma),
            "k_rapid_eq",
            keq,
        ],
    )
    return model
