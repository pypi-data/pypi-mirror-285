"""GAP + S7P <=> R5P + X5P

EC 2.2.1.1

Equilibrator
D-Glyceraldehyde 3-phosphate(aq) + Sedoheptulose 7-phosphate(aq)
    ⇌ D-Ribose 5-phosphate(aq) + D-Xylulose 5-phosphate(aq)
Keq = 0.2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import rapid_equilibrium_2s_2p

from ._utils import add_parameter_if_missing

ENZYME = n.transketolase_gap_s7p()


def add_transketolase_x5p_r5p_s7p_gap(
    model: Model, *, chl_stroma: str
) -> Model:
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)

    model.add_parameter("keq_transketolase_10", 0.85)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_2s_2p,
        stoichiometry={
            n.gap(chl_stroma): -1,
            n.s7p(chl_stroma): -1,
            n.r5p(chl_stroma): 1,
            n.x5p(chl_stroma): 1,
        },
        args=[
            n.gap(chl_stroma),
            n.s7p(chl_stroma),
            n.r5p(chl_stroma),
            n.x5p(chl_stroma),
            "k_rapid_eq",
            "keq_transketolase_10",
        ],
    )
    return model
