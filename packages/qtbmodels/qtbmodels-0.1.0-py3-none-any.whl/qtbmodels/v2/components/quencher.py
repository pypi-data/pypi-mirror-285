"""name

EC FIXME

Equilibrator
"""

from modelbase.ode import Model

from qtbmodels import names as n


def _rate_quencher(
    Psbs: float,
    Vx: float,
    Psbsp: float,
    Zx: float,
    y0: float,
    y1: float,
    y2: float,
    y3: float,
    kZSat: float,
) -> float:
    """co-operative 4-state quenching mechanism
    gamma0: slow quenching of (Vx - protonation)
    gamma1: fast quenching (Vx + protonation)
    gamma2: fastest possible quenching (Zx + protonation)
    gamma3: slow quenching of Zx present (Zx - protonation)
    """
    ZAnt = Zx / (Zx + kZSat)
    return (
        y0 * Vx * Psbs + y1 * Vx * Psbsp + y2 * ZAnt * Psbsp + y3 * ZAnt * Psbs
    )


def add_quencher(model: Model) -> Model:
    model.add_parameter("gamma0", 0.1)
    model.add_parameter("gamma1", 0.25)
    model.add_parameter("gamma2", 0.6)
    model.add_parameter("gamma3", 0.15)
    model.add_parameter("kZSat", 0.12)
    model.add_derived_compound(
        name=n.quencher(),
        function=_rate_quencher,
        args=[
            n.psbs_de(),
            n.vx(),
            n.psbs_pr(),
            n.zx(),
            "gamma0",
            "gamma1",
            "gamma2",
            "gamma3",
            "kZSat",
        ],
    )
    return model
