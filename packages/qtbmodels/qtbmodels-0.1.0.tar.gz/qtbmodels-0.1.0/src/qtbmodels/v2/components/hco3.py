from modelbase.ode import Model

from qtbmodels import names as n


def add_hco3(model: Model, *, compartment: str) -> Model:
    if n.co2() in model.compounds:
        model.add_compound(n.hco3())
    else:
        model.add_parameter(
            n.hco3(compartment), 50 * model.parameters[n.co2()]
        )
    return model
