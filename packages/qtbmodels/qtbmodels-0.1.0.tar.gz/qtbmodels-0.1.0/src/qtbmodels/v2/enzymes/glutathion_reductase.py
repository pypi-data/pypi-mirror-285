"""name

EC 1.8.1.7

glutathione + NADP <=> glutathion-disulfide + NADPH + H+

Equilibrator
"""

from modelbase.ode import Model

from qtbmodels import names as n

ENZYME = n.glutathion_reductase()


def _rate_glutathion_reductase(
    NADPH: float,
    GSSG: float,
    kcat_GR: float,
    GR0: float,
    KmNADPH: float,
    KmGSSG: float,
) -> float:
    nom = kcat_GR * GR0 * NADPH * GSSG
    denom = KmNADPH * GSSG + KmGSSG * NADPH + NADPH * GSSG + KmNADPH * KmGSSG
    return nom / denom


def add_glutathion_reductase(model: Model) -> Model:
    model.add_parameter(kcat := n.kcat(ENZYME), 595)
    model.add_parameter(e0 := n.e0(ENZYME), 1.4e-3)
    model.add_parameter(km_gssg := n.km(ENZYME, n.glutathion_ox()), 2e2 * 1e-3)
    model.add_parameter(km_nadph := n.km(ENZYME, n.nadph()), 3e-3)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_glutathion_reductase,
        stoichiometry={n.nadph(): -1, n.glutathion_ox(): -1},
        args=[
            n.nadph(),
            n.glutathion_ox(),
            kcat,
            e0,
            km_nadph,
            km_gssg,
        ],
    )
    return model
