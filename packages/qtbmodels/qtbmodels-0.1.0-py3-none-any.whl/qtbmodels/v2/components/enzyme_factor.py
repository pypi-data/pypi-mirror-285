from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_enzyme_factor(model: Model) -> Model:
    model.add_compound(n.e_inactive())
    model.add_parameter(tot := "e_cbb_tot", 6)
    model.add_derived_compound(
        name=n.e_active(),
        function=moiety_1,
        args=[n.e_inactive(), tot],
    )
    return model
