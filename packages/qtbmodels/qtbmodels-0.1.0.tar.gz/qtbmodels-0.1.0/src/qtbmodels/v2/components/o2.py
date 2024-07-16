"""Atmospheric concentration around 21 %

0.25 mM in chloroplast stroma (FIXME: source)
8.0 mmol / (mol Chl) in chloroplast lumen (FIXME: source)

"""

from modelbase.ode import Model

from qtbmodels import names as n


def _add_o2_static(
    model: Model, *, compartment: str, par_value: float
) -> Model:
    model.add_parameter(n.o2(compartment), par_value)
    return model


def add_o2(
    model: Model,
    *,
    compartment: str,
    static: bool,
    par_value: float,
) -> Model:
    if static:
        _add_o2_static(model, compartment=compartment, par_value=par_value)
    else:
        raise NotImplementedError
    return model
