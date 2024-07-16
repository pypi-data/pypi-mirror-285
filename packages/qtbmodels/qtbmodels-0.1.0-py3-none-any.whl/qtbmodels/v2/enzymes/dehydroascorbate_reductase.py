"""dehydroascorbate_reductase, DHAR

EC FIXME

Equilibrator
"""

from modelbase.ode import Model

from qtbmodels import names as n

ENZYME = n.dehydroascorbate_reductase()


def _rate_dhar(
    DHA: float,
    GSH: float,
    kcat_DHAR: float,
    DHAR0: float,
    KmDHA: float,
    K: float,
    KmGSH: float,
) -> float:
    nom = kcat_DHAR * DHAR0 * DHA * GSH
    denom = K + KmDHA * GSH + KmGSH * DHA + DHA * GSH
    return nom / denom


def add_dehydroascorbate_reductase(model: Model) -> Model:
    model.add_parameter(kcat := n.kcat(ENZYME), 142)
    model.add_parameter(e0 := n.e0(ENZYME), 1.7e-3)
    model.add_parameter("K", 5e5 * (1e-3) ** 2)
    model.add_parameter(km_dha := n.km(ENZYME, n.dha()), 70e-3)
    model.add_parameter(
        km_gsh := n.km(ENZYME, n.glutathion_red()), 2.5e3 * 1e-3
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_dhar,
        stoichiometry={
            n.dha(): -1,
            n.glutathion_ox(): 1,
        },
        args=[
            n.dha(),
            n.glutathion_red(),
            kcat,
            e0,
            km_dha,
            "K",
            km_gsh,
        ],
    )
    return model
