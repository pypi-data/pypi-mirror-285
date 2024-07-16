from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_lhc_moiety(model: Model) -> Model:
    model.add_parameter("LHC_total", 1)
    model.add_derived_compound(
        name=n.lhcp(),
        function=moiety_1,
        args=[n.lhc(), "LHC_total"],
    )
    return model
