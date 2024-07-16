"""triose-phosphate isomerase

EC 5.3.1.1

Equilibrator
    D-Glyceraldehyde 3-phosphate(aq) ⇌ Glycerone phosphate(aq)
    Keq = 10 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import rapid_equilibrium_1s_1p

from ._utils import add_parameter_if_missing

ENZYME = n.triose_phosphate_isomerase()


def add_triose_phosphate_isomerase(model: Model, *, chl_stroma: str) -> Model:
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)
    model.add_parameter(keq := n.keq(ENZYME), 22.0)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_1s_1p,
        stoichiometry={
            n.gap(chl_stroma): -1,
            n.dhap(chl_stroma): 1,
        },
        args=[
            n.gap(chl_stroma),
            n.dhap(chl_stroma),
            "k_rapid_eq",
            keq,
        ],
    )
    return model
