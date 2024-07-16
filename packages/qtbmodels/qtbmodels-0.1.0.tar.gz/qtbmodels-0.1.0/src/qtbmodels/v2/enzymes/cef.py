from modelbase.ode import Model

from qtbmodels import names as n

ENZYME = n.cyclic_electron_flow()


def _rate_cyclic_electron_flow(
    Pox: float,
    Fdred: float,
    kcyc: float,
) -> float:
    return kcyc * Fdred**2 * Pox


def add_cyclic_electron_flow(model: Model) -> Model:
    model.add_parameter("kcyc", 1.0)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_cyclic_electron_flow,
        stoichiometry={
            n.pq_ox(): -1,
            n.fd_ox(): 2,
        },
        args=[
            n.pq_ox(),
            n.fd_red(),
            "kcyc",
        ],
    )
    return model
