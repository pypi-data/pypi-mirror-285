from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_glutamate_and_oxoglutarate(
    model: Model, *, chl_stroma: str, static: bool, total: float = 3.0
) -> Model:
    model.add_parameter("Glu_Oxo_total", total)

    if static:
        model.add_parameter(n.glutamate(), 2.0)
        model.add_derived_parameter(
            parameter_name=n.oxoglutarate(),
            function=moiety_1,
            parameters=[
                n.glutamate(),
                "Glu_Oxo_total",
            ],
        )
    else:
        model.add_compound(n.glutamate())

        model.add_derived_compound(
            name=n.oxoglutarate(chl_stroma),
            function=moiety_1,
            args=[
                n.glutamate(),
                "Glu_Oxo_total",
            ],
        )
    return model
