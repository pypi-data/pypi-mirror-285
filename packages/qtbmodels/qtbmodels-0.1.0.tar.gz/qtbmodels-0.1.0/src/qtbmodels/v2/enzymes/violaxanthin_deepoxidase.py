"""Violaxanthin Deepoxidase (lumen)
Violaxanthin + Ascorbate -> Antheraxanthin + Dehydroascorbate + H2O
Antheraxanthin + Ascorbate -> Zeaxanthin + Dehydroascorbate + H2O
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import protons_stroma

ENZYME = n.violaxanthin_deepoxidase()


def _rate_protonation_hill(
    Vx: float,
    H: float,
    nH: float,
    k_fwd: float,
    kphSat: float,
) -> float:
    return k_fwd * (H**nH / (H**nH + protons_stroma(kphSat) ** nH)) * Vx  # type: ignore


def add_violaxanthin_epoxidase(model: Model, *, chl_lumen: str) -> Model:
    model.add_parameter("kHillX", 5.0)
    model.add_parameter(k := "kDeepoxV", 0.0024)
    model.add_parameter("kphSat", 5.8)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_protonation_hill,
        stoichiometry={
            n.vx(): -1,
        },
        args=[
            n.vx(),
            n.h(chl_lumen),
            "kHillX",
            k,
            "kphSat",
        ],
    )
    return model
