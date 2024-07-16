from modelbase.ode import Model

from qtbmodels import names as n


def add_energy(
    model: Model,
    *,
    static: bool = True,
    static_val: float = 1.0,
) -> Model:
    if static:
        model.add_parameter(n.energy(), static_val)
    else:
        model.add_compound(n.energy())
    return model
