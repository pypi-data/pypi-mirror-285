"""name

EC FIXME

Equilibrator
"""

from modelbase.ode import Model

from qtbmodels import names as n


def add_nh4(
    model: Model, *, static_nh4: bool, par_value: float = 1.0
) -> Model:
    if static_nh4:
        model.add_parameter(n.nh4(), par_value)
    else:
        model.add_compound(n.nh4())
    return model
