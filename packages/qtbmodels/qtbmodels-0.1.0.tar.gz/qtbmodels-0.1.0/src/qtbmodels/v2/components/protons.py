from modelbase.ode import Model

from qtbmodels import names as n


def add_protons_lumen() -> Model:
    raise NotImplementedError


def add_protons_stroma(model: Model, *, chl_stroma: str) -> Model:
    model.add_parameter(n.h(chl_stroma), 1.2589254117941661e-05)
    return model
