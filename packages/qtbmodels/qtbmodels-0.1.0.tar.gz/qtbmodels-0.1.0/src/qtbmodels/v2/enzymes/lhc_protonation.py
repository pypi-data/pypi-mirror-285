"""name

EC FIXME

Equilibrator
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import protons_stroma

from ._utils import filter_stoichiometry

ENZYME = n.lhc_protonation()


def _protonation_hill(
    Vx: float,
    H: float,
    nH: float,
    k_fwd: float,
    kphSat: float,
) -> float:
    return k_fwd * (H**nH / (H**nH + protons_stroma(kphSat) ** nH)) * Vx  # type: ignore


def add_lhc_protonation(model: Model, *, chl_lumen: str) -> Model:
    model.add_parameter("kH_LHC", 3.0)
    model.add_parameter("k_lhc_protonation", 0.0096)
    model.add_parameter("kph_sat_lhc", 5.8)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_protonation_hill,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.psbs_de(): -1,
                n.psbs_pr(): 1,
            },
        ),
        args=[
            n.psbs_de(),
            n.h(chl_lumen),
            "kH_LHC",
            "k_lhc_protonation",
            "kph_sat_lhc",
        ],
    )
    return model
