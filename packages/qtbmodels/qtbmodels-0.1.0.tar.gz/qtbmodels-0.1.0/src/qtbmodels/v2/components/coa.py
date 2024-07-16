from modelbase.ode import Model

from qtbmodels import names as n


def add_coa(model: Model, *, compartment: str, conc: float = 0.5) -> Model:
    """Ranges from 0.1 - 1 mM"""
    model.add_parameter(n.coa(compartment), conc)
    return model
