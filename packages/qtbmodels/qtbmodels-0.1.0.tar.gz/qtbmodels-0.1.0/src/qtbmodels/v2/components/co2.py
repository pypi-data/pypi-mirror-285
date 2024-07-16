"""atmospheric CO2: ~400 ppm
dissolved CO2:
    - freshwater: 5-20 ppm
    - seawater: 20-90 ppm
    - plant cell: 10-100 ppm

Use 50 ppm as internal (0.012 mM)
With atmospheric / internal = 400 / 50 = 8
we get 8*0.012 = 0.096 mM atmospheric CO2
"""

from modelbase.ode import Model

from qtbmodels import names as n

ENZYME = n.co2_dissolving()


def _add_co2_static(
    model: Model, *, chl_stroma: str, par_value: float
) -> Model:
    model.add_parameter(n.co2(chl_stroma), par_value)
    return model


def _add_co2_dynamic(model: Model, *, chl_stroma: str) -> Model:
    model.add_compound(n.co2(chl_stroma))
    model.add_parameters(
        {
            n.co2_atmosphere(): 0.096,  # mM
        }
    )
    return model


def add_co2(
    model: Model, *, chl_stroma: str, static: bool, par_value: float
) -> Model:
    if static:
        _add_co2_static(model, chl_stroma=chl_stroma, par_value=par_value)
    else:
        _add_co2_dynamic(model, chl_stroma=chl_stroma)
    return model
