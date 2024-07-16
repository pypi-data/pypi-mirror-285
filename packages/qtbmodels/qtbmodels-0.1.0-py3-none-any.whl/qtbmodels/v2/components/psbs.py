from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def add_psbs_moietry(model: Model) -> Model:
    """Derive protonated form from deprotonated form"""
    model.add_parameter("PSBS_total", 1.0)
    model.add_derived_compound(
        name=n.psbs_pr(),
        function=moiety_1,
        args=[
            n.psbs_de(),
            "PSBS_total",
        ],
    )
    return model
