from modelbase.ode import Model

from qtbmodels import names as n

from ._utils import filter_stoichiometry

ENZYME = n.ferredoxin_reductase()


def _rate_ferredoxin_reductase(
    Fd: float,
    Fdred: float,
    A1: float,
    A2: float,
    kFdred: float,
    Keq_FAFd: float,
) -> float:
    """rate of the redcution of Fd by the activity of PSI
    used to be equall to the rate of PSI but now
    alternative electron pathway from Fd allows for the production of ROS
    hence this rate has to be separate
    """
    return kFdred * Fd * A1 - kFdred / Keq_FAFd * Fdred * A2


def add_ferredoxin_reductase(model: Model) -> Model:
    model.add_parameter(n.k(ENZYME), 2.5e5)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_ferredoxin_reductase,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.fd_ox(): -1,
                n.fd_red(): 1,
            },
        ),
        args=[
            n.fd_ox(),
            n.fd_red(),
            n.a1(),
            n.a2(),
            n.k(ENZYME),
            n.keq(ENZYME),
        ],
    )
    return model
