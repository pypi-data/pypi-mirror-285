"""GAP + F6P <=> E4P + X5P

EC 2.2.1.1

Equilibrator
D-Glyceraldehyde 3-phosphate(aq) + D-Fructose 6-phosphate(aq)
    ⇌ D-Xylulose 5-phosphate(aq) + D-Erythrose 4-phosphate(aq)
Keq = 0.02 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import rapid_equilibrium_2s_2p

from ._utils import add_parameter_if_missing

ENZYME = n.transketolase_gap_f6p()


def add_transketolase_x5p_e4p_f6p_gap(
    model: Model, *, chl_stroma: str
) -> Model:
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)

    model.add_parameter("keq_transketolase_7", 0.084)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_2s_2p,
        stoichiometry={
            n.gap(chl_stroma): -1,
            n.f6p(chl_stroma): -1,
            n.e4p(chl_stroma): 1,
            n.x5p(chl_stroma): 1,
        },
        args=[
            n.gap(chl_stroma),
            n.f6p(chl_stroma),
            n.e4p(chl_stroma),
            n.x5p(chl_stroma),
            "k_rapid_eq",
            "keq_transketolase_7",
        ],
    )

    return model
