"""DHAP + EAP <=> SBP

EC 4.1.2.13

Equilibrator
Glycerone phosphate(aq) + D-Erythrose 4-phosphate(aq) ⇌ Sedoheptulose 1,7-bisphosphate(aq)
Keq = 4.8e3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import rapid_equilibrium_2s_1p

from ._utils import add_parameter_if_missing

ENZYME = n.aldolase_dhap_e4p()


def add_aldolase_dhap_e4p(model: Model, *, chl_stroma: str) -> Model:
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)

    model.add_parameter(keq := n.keq(ENZYME), 13.0)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_2s_1p,
        stoichiometry={
            n.dhap(chl_stroma): -1,
            n.e4p(chl_stroma): -1,
            n.sbp(chl_stroma): 1,
        },
        args=[
            n.dhap(chl_stroma),
            n.e4p(chl_stroma),
            n.sbp(chl_stroma),
            "k_rapid_eq",
            keq,
        ],
    )
    return model
