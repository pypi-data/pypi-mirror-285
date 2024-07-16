from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_carotenoid_moiety(
    model: Model, *, compartment: str = "", total: float = 1.0
) -> Model:
    model.add_parameter("Carotenoids_total", total)

    model.add_derived_compound(
        name=n.zx(compartment),
        function=moiety_1,
        args=[
            n.vx(compartment),
            "Carotenoids_total",
        ],
    )
    return model
