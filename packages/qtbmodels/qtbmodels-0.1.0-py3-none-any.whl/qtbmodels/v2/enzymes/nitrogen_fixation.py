"""name

EC FIXME

Equilibrator
"""

from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n

from ._utils import filter_stoichiometry

ENZYME = n.nitrogen_fixation()


def _two_times_convf(convf: float) -> float:
    return 2.0 * convf


def _rate_nitrogen_fixation(
    oxo: float,
    atp: float,
    fd_red: float,
    nh4: float,
    k_fwd: float,
    convf: float,
) -> float:
    return k_fwd * oxo * atp * nh4 * (2 * fd_red * convf)


def add_nitrogen_metabolism(
    model: Model,
) -> Model:
    """Equilibrator
        2-Oxoglutarate(aq) + ATP(aq) + 2 ferredoxin(red)(aq) + NH4 (aq)
        ⇌ Glutamate(aq) + ADP(aq) + 2 ferredoxin(ox)(aq) + Orthophosphate(aq)
    K'eq = 2.4e13

    Units
     - 2-oxoglutarate: mM
     - ATP: mM
     - Fd_red: ?
     - NH4: mM
     - Glutamate: mM
     - ADP: mM
     - Fd_ox: ?
     - Orthophosphate: mM
    """
    model.add_parameter(k := n.k(ENZYME), 1.0)

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.atp(): -1.0,  # mM
            n.nh4(): -1.0,  # mM
            n.glutamate(): 1.0,  # mM
        },
    )

    model.add_reaction_from_args(
        ENZYME,
        _rate_nitrogen_fixation,
        stoichiometry=stoichiometry,
        derived_stoichiometry={
            n.fd_ox(): DerivedStoichiometry(_two_times_convf, ["convf"]),
        },
        args=[
            n.oxoglutarate(),
            n.atp(),
            n.fd_red(),
            n.nh4(),
            k,
            "convf",
        ],
    )

    return model
