import numpy as np
from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import moiety_1


def _keq_pq_red(
    E0_QA: float,
    F: float,
    E0_PQ: float,
    pHstroma: float,
    dG_pH: float,
    RT: float,
) -> float:
    DG1 = -E0_QA * F
    DG2 = -2 * E0_PQ * F
    DG = -2 * DG1 + DG2 + 2 * pHstroma * dG_pH
    K: float = np.exp(-DG / RT)
    return K


def add_plastoquinone_keq(model: Model, *, chl_stroma: str) -> Model:
    model.add_parameter("E^0_QA", -0.14)
    model.add_parameter("E^0_PQ", 0.354)

    model.add_derived_parameter(
        n.keq(n.pq_red()),
        _keq_pq_red,
        [
            "E^0_QA",
            "F",
            "E^0_PQ",
            n.ph(chl_stroma),
            "dG_pH",
            "RT",
        ],
    )
    return model


def add_plastoquinone_moiety(model: Model, *, total: float = 17.5) -> Model:
    model.add_parameter("PQ_total", total)

    model.add_derived_compound(
        name=n.pq_red(),
        function=moiety_1,
        args=[
            n.pq_ox(),
            "PQ_total",
        ],
    )
    return model
