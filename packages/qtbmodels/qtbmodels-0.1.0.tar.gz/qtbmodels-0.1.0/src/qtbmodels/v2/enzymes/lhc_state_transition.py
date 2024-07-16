"""name

EC FIXME

Equilibrator
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import mass_action_1s


def _rate_state_transition_ps1_ps2(
    Ant: float,
    Pox: float,
    kStt7: float,
    PQtot: float,
    KM_ST: float,
    n_ST: float,
) -> float:
    kKin = kStt7 * (1 / (1 + (Pox / PQtot / KM_ST) ** n_ST))
    return kKin * Ant  # type: ignore


def add_state_transitions(model: Model) -> Model:
    model.add_parameter("kStt7", 0.0035)
    model.add_parameter("KM_ST", 0.2)
    model.add_parameter("n_ST", 2.0)
    model.add_parameter("kPph1", 0.0013)

    enzyme_name = n.lhc_state_transition_12()
    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=_rate_state_transition_ps1_ps2,
        stoichiometry={
            n.lhc(): -1,
        },
        args=[
            n.lhc(),
            n.pq_ox(),
            "kStt7",
            "PQ_total",
            "KM_ST",
            "n_ST",
        ],
    )

    enzyme_name = n.lhc_state_transition_21()
    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=mass_action_1s,
        stoichiometry={
            n.lhc(): 1,
        },
        args=[
            n.lhcp(),
            "kPph1",
        ],
    )
    return model
