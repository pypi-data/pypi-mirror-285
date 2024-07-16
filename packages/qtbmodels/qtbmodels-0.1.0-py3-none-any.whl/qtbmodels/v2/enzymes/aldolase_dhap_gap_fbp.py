"""DHAP + GAP <=> FBP

EC 4.1.2.13

Equilibrator
Glycerone phosphate(aq) + D-Glyceraldehyde 3-phosphate(aq) ⇌ D-Fructose 1,6-bisphosphate(aq)
Keq = 1.1e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import rapid_equilibrium_2s_1p

from ._utils import add_parameter_if_missing

ENZYME = n.aldolase_dhap_gap()


def add_aldolase_dhap_gap(model: Model, *, chl_stroma: str) -> Model:
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)

    model.add_parameter(keq := n.keq(ENZYME), 7.1)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_2s_1p,
        stoichiometry={
            n.gap(chl_stroma): -1,
            n.dhap(chl_stroma): -1,
            n.fbp(chl_stroma): 1,
        },
        args=[
            n.gap(chl_stroma),
            n.dhap(chl_stroma),
            n.fbp(chl_stroma),
            "k_rapid_eq",
            keq,
        ],
    )
    return model
