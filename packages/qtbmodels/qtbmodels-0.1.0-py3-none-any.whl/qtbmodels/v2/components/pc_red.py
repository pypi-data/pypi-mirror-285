from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_plastocyanin_moiety(model: Model, *, total: float = 4.0) -> Model:
    model.add_parameter("PC_total", total)

    model.add_derived_compound(
        name=n.pc_red(),
        function=moiety_1,
        args=[
            n.pc_ox(),
            "PC_total",
        ],
    )
    return model
