from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_ferredoxin_moiety(model: Model, *, total: float = 5.0) -> Model:
    model.add_parameter("Fd_total", total)

    model.add_derived_compound(
        name=n.fd_red(),
        function=moiety_1,
        args=[
            n.fd_ox(),
            "Fd_total",
        ],
    )
    return model
