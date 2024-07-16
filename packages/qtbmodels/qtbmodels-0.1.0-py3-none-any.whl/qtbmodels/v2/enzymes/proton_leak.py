"""name

EC FIXME

Equilibrator
"""

from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n
from qtbmodels.shared import protons_stroma

ENZYME = n.proton_leak()


def _neg_one_div_by(x: float) -> float:
    return -1.0 / x


def _rate_leak(
    protons_lumen: float,
    k_leak: float,
    ph_stroma: float,
) -> float:
    return k_leak * (protons_lumen - protons_stroma(ph_stroma))


def add_proton_leak(model: Model, *, chl_stroma: str, chl_lumen: str) -> Model:
    model.add_parameter("kLeak", 10.0)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_leak,
        stoichiometry={},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                function=_neg_one_div_by, args=["bH"]
            )
        },
        args=[
            n.h(chl_lumen),
            "kLeak",
            n.ph(chl_stroma),
        ],
    )
    return model
