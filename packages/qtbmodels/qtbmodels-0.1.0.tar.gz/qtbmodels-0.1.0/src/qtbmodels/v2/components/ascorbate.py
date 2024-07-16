"""name

EC FIXME

Equilibrator
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_2


def add_ascorbate_moiety(model: Model) -> Model:
    model.add_parameter(tot := "Ascorbate_total", 10)
    model.add_derived_compound(
        name=n.ascorbate(),
        function=moiety_2,
        args=[n.mda(), n.dha(), tot],
    )
    return model
