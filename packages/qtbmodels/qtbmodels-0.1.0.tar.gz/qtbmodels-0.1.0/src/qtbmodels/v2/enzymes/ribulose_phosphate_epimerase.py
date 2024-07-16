"""ribulose-phosphate 3-epimerase

EC 5.1.3.1

Equilibrator
    D-Xylulose 5-phosphate(aq) ⇌ D-Ribulose 5-phosphate(aq)
    Keq = 0.3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import rapid_equilibrium_1s_1p

from ._utils import add_parameter_if_missing

ENZYME = n.ribulose_phosphate_epimerase()


def add_ribulose_5_phosphate_3_epimerase(
    model: Model, *, chl_stroma: str
) -> Model:
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)
    model.add_parameter(keq := n.keq(ENZYME), 0.67)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_1s_1p,
        stoichiometry={
            n.x5p(chl_stroma): -1,
            n.ru5p(chl_stroma): 1,
        },
        args=[
            n.x5p(chl_stroma),
            n.ru5p(chl_stroma),
            "k_rapid_eq",
            keq,
        ],
    )
    return model
