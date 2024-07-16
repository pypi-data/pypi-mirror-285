"""name

EC FIXME

Equilibrator
"""

from modelbase.ode import Model

from qtbmodels.shared import proportional


def add_rt(model: Model) -> Model:
    model.add_parameters(
        {
            "R": 0.0083,
            "T": 298.0,
        }
    )
    model.add_derived_parameter(
        "RT",
        proportional,
        ["R", "T"],
    )
    return model
