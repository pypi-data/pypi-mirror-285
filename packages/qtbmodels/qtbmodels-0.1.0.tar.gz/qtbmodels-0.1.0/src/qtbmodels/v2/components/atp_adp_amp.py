"""Total A*P pool
- Poolman 2000: 0.5 mM
- Matuszyńska 2016: 2.55 mmol / mol Chl

"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_atp_adp(
    model: Model,
    *,
    compartment: str,
    static: bool,
    atp: float = 0.436,  # only if static
    total: float = 0.5,
) -> Model:
    model.add_parameter("A*P_total", total)

    if static:
        model.add_parameter(n.atp(compartment), atp)
        model.add_derived_parameter(
            parameter_name=n.adp(compartment),
            function=moiety_1,
            parameters=[
                n.atp(compartment),
                "A*P_total",
            ],
        )
    else:
        model.add_compound(n.atp(compartment))
        model.add_derived_compound(
            name=n.adp(compartment),
            function=moiety_1,
            args=[
                n.atp(compartment),
                "A*P_total",
            ],
        )
    return model


def add_amp(model: Model, *, compartment: str, conc: float = 1.0) -> Model:
    """Estimates are between 1 and 10 mM"""
    model.add_parameter(n.amp(compartment), conc)
    return model
