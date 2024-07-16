from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_thioredoxin(model: Model) -> Model:
    model.add_compound(n.tr_ox())
    model.add_parameter(tot := "thioredoxin_tot", 1)
    model.add_derived_compound(
        name=n.tr_red(),
        function=moiety_1,
        args=[n.tr_ox(), tot],
    )
    return model
