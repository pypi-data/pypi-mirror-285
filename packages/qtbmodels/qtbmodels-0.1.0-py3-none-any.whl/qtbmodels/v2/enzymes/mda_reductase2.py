"""EC 1.6.5.4
NADH + Proton + 2 Monodehydroascorbate <=> NAD + 2 ascorbate


Equilibrator
"""

from modelbase.ode import Model

from qtbmodels import names as n

ENZYME = n.mda_reductase2()


def _rate_mda_reductase(
    NADPH: float,
    MDA: float,
    kcatMDAR: float,
    KmMDAR_NADPH: float,
    KmMDAR_MDA: float,
    MDAR0: float,
) -> float:
    """Compare Valero et al. 2016"""
    nom = kcatMDAR * MDAR0 * NADPH * MDA
    denom = (
        KmMDAR_NADPH * MDA
        + KmMDAR_MDA * NADPH
        + NADPH * MDA
        + KmMDAR_NADPH * KmMDAR_MDA
    )
    return nom / denom


def add_mda_reductase2(model: Model) -> Model:
    model.add_parameters(
        {
            "kcatMDAR": 1080000 / (60 * 60),
            "KmMDAR_MDA": 1.4e-3,
            "KmMDAR_NADPH": 23e-3,
            "MDAR0": 2e-3,
        }
    )
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_mda_reductase,
        stoichiometry={
            n.nadph(): -1,
            n.mda(): -2,
        },
        args=[
            n.nadph(),
            n.mda(),
            "kcatMDAR",
            "KmMDAR_NADPH",
            "KmMDAR_MDA",
            "MDAR0",
        ],
    )
    return model
