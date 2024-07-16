from modelbase.ode import Model

from qtbmodels import names as n


def add_diphosphate(
    model: Model, *, compartment: str, conc: float = 0.3
) -> Model:
    model.add_parameter(n.ppi(compartment), conc)
    return model
