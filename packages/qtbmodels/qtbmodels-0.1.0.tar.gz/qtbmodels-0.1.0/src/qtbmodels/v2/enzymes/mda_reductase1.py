"""name

EC FIXME

Equilibrator
Monodehydroascorbate(aq) + 0.5 NAD (aq) ⇌ Dehydroascorbate(aq) + 0.5 NADH(aq)
"""

from modelbase.ode import Model

from qtbmodels import names as n

ENZYME = n.mda_reductase1()


def _rate_mda_reductase(
    MDA: float,
    k3: float,
) -> float:
    return k3 * MDA**2


def add_mda_reductase1(model: Model) -> Model:
    model.add_parameter(k3 := "k3", 0.5 / 1e-3)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_mda_reductase,
        stoichiometry={
            n.mda(): -2,
            n.dha(): 1,
        },
        args=[n.mda(), k3],
    )
    return model
