from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import reversible_mass_action_keq_2s_2p

from ._utils import filter_stoichiometry

ENZYME = n.oxidative_phosphorylation()


def add_oxidative_phosphorylation(model: Model) -> Model:
    model.add_parameter(kf := n.k(ENZYME), 1)
    model.add_parameter(keq := n.keq(ENZYME), 3 / 2)

    model.add_reaction_from_args(
        ENZYME,
        reversible_mass_action_keq_2s_2p,
        filter_stoichiometry(
            model,
            {
                n.nadph(): -1,
                n.adp(): -1,
                n.nadp(): 1,
                n.atp(): 1,
            },
        ),
        [n.nadph(), n.adp(), n.nadp(), n.atp(), kf, keq],
    )
    return model
