"""Glyceraldehyde 3-phosphate dehydrogenase (GADPH)

EC 1.2.1.13

Equilibrator
    NADPH(aq) + 3-Phospho-D-glyceroyl phosphate(aq)
    ⇌ NADP (aq) + Orthophosphate(aq) + D-Glyceraldehyde 3-phosphate(aq)
    Keq = 2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

FIXME: Poolman uses H+ in the description. Why?
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import rapid_equilibrium_3s_3p

from ._utils import add_parameter_if_missing, filter_stoichiometry

ENZYME = n.gadph()


def add_gadph(model: Model, *, chl_stroma: str) -> Model:
    add_parameter_if_missing(model, "k_rapid_eq", 800000000.0)

    model.add_parameter(keq := n.keq(ENZYME), 16000000.0)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.nadph(): -1.0,
            n.bpga(chl_stroma): -1.0,
            #
            n.nadp(): 1.0,
            n.pi(): 1.0,
            n.gap(chl_stroma): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=rapid_equilibrium_3s_3p,
        stoichiometry=stoichiometry,
        args=[
            n.bpga(chl_stroma),
            n.nadph(chl_stroma),
            n.h(chl_stroma),
            n.gap(chl_stroma),
            n.nadp(chl_stroma),
            n.pi(chl_stroma),
            "k_rapid_eq",
            keq,
        ],
    )
    return model
