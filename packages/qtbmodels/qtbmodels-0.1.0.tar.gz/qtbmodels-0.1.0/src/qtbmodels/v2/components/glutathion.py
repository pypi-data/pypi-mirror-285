"""name

EC FIXME

Equilibrator
"""

from modelbase.ode import Model

from qtbmodels import names as n


def _glutathion_moiety(
    GSSG: float,
    GStotal: float,
) -> float:
    return GStotal - 2 * GSSG


def add_glutathion_moiety(model: Model) -> Model:
    model.add_parameter("Glutathion_total", 10)
    model.add_derived_compound(
        name=n.glutathion_red(),
        function=_glutathion_moiety,
        args=[n.glutathion_ox(), "Glutathion_total"],
    )
    return model
