from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_nadp_nadph(
    model: Model,
    *,
    compartment: str,
    static: bool,
    nadph: float = 0.21,  # only if static
    total: float = 0.5,
) -> Model:
    model.add_parameter("NADP*_total", total)

    if static:
        model.add_parameter(n.nadph(compartment), nadph)
        model.add_derived_parameter(
            n.nadp(compartment),
            moiety_1,
            [
                n.nadph(compartment),
                "NADP*_total",
            ],
        )
    else:
        model.add_compound(n.nadph(compartment))
        model.add_derived_compound(
            n.nadp(compartment),
            moiety_1,
            args=[
                n.nadph(compartment),
                "NADP*_total",
            ],
        )
    return model
