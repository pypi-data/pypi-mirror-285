from __future__ import annotations

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.v1.shared import (
    add_vmax,
    michaelis_menten_1s,
    ping_pong_bi_bi,
    value,
)


def _add_phosphoglycolate_phosphatase(model: Model, chl: str) -> Model:
    """phosphoglycolate phosphatase, EC 3.1.3.18

    H2O(chl) + PGO(chl) <=> Orthophosphate(chl) + Glycolate(chl)

    Equilibrator
    H2O(l) + PGO(aq) ⇌ Orthophosphate(aq) + Glycolate(aq)
    Keq = 3.1e5 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.add_parameter("pgo_influx", 60.0)
    model.add_reaction_from_args(
        rate_name="phosphoglycolate_phosphatase",
        function=value,
        stoichiometry={n.glycolate(): 1},
        args=["pgo_influx"],
    )
    return model


def _add_glycolate_oxidase(model: Model, chl: str, per: str) -> Model:
    """glycolate oxidase

    O2(per) + Glycolate(chl) <=> H2O2(per) + Glyoxylate(per)

    Equilibrator
    O2(aq) + Glycolate(aq) ⇌ H2O2(aq) + Glyoxylate(aq)
    Keq = 3e15 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    rate_name = "glycolate_oxidase"
    vmax = add_vmax(model, rate_name, kcat=100.0)
    model.add_parameter(f"kms_{rate_name}", 0.06)
    model.add_reaction_from_args(
        rate_name=rate_name,
        function=michaelis_menten_1s,
        stoichiometry={
            # "O2_stroma": -1,
            n.glycolate(): -1,
            n.glyoxylate(): 1,
            n.h2o2(): 1,
        },
        args=[
            n.glycolate(),
            vmax,
            f"kms_{rate_name}",
        ],
    )
    return model


def _add_glycine_transaminase(model: Model, per: str) -> Model:
    """glycine transaminase

    L-Glutamate(per) + Glyoxylate(per) <=> 2-Oxoglutarate(per) + Glycine(per)

    Equilibrator
    L-Glutamate(aq) + Glyoxylate(aq) ⇌ 2-Oxoglutarate(aq) + Glycine(aq)
    Keq = 30 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    name = "glycine_transaminase"
    vmax = add_vmax(model, name, kcat=143.0)
    model.add_parameter(f"kms_{name}", 3.0)
    model.add_reaction_from_args(
        rate_name=f"{name}",
        function=michaelis_menten_1s,
        stoichiometry={
            n.glyoxylate(): -1,
            n.gly(): 1,
        },
        args=[
            n.glyoxylate(),
            vmax,
            f"kms_{name}",
        ],
    )
    return model


def _add_glycine_decarboxylase(
    model: Model,
    per: str,
    mit: str,
    static_co2: bool,
) -> Model:
    """glycine decarboxylase

    2 Glycine + NAD + 2 H2O ⇌ Serine + NH3 + NADH + CO2

    Equilibrator
    2 Glycine(aq) + NAD(aq) + 2 H2O(l) ⇌ Serine(aq) + NH3(aq) + NADH(aq) + CO2(total)
    Keq = 2.4e-4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    name = "glycine_decarboxylase"
    vmax = add_vmax(model, name, kcat=100.0)
    model.add_parameter(f"kms_{name}", 6.0)
    stoichiometry = {
        # n.nad(): -0.5,
        n.gly(): -1,
        # n.nadh(): 0.5,
        # n.nh4(): 0.5,
        n.ser(): 0.5,
        # n.co2(): 0.5,
    }
    if not static_co2:
        stoichiometry.update({n.co2(): 0.5})

    model.add_reaction_from_args(
        rate_name=f"{name}",
        function=michaelis_menten_1s,
        stoichiometry=stoichiometry,
        args=[
            n.gly(),
            vmax,
            f"kms_{name}",
        ],
    )
    return model


def _add_serine_glyoxylate_transaminase(model: Model, per: str) -> Model:
    """serine glyoxylate transaminase

    Glyoxylate + L-Serine <=> Glycine + Hydroxypyruvate

    Equilibrator
    Glyoxylate(aq) + Serine(aq) ⇌ Glycine(aq) + Hydroxypyruvate(aq)
    Keq = 6 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    name = "serine_glyoxylate_transaminase"
    vmax = add_vmax(model, name, kcat=159.0)
    model.add_parameter("kms_transaminase_serine", 2.72)
    model.add_parameter("kms_transaminase_glyxoylate", 0.15)
    model.add_reaction_from_args(
        rate_name=f"{name}",
        function=ping_pong_bi_bi,
        stoichiometry={
            n.glyoxylate(): -1,
            n.ser(): -1,
            n.gly(): 1,
            n.hydroxypyruvate(): 1,
        },
        args=[
            n.glyoxylate(),
            n.ser(),
            vmax,
            "kms_transaminase_glyxoylate",
            "kms_transaminase_serine",
        ],
    )
    return model


def _add_glycerate_dehydrogenase(model: Model, per: str) -> Model:
    """glycerate dehydrogenase

    NADH + Hydroxypyruvate <=> NAD  + D-Glycerate

    Equilibrator
    NADH(aq) + Hydroxypyruvate(aq) ⇌ NAD(aq) + D-Glycerate(aq)
    Keq = 8.7e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    name = "glycerate_dehydrogenase"
    vmax = add_vmax(model, name, kcat=398.0)
    model.add_parameter(f"kms_{name}", 0.12)
    model.add_reaction_from_args(
        rate_name=f"{name}",
        function=michaelis_menten_1s,
        stoichiometry={
            # NADH: -1,
            n.hydroxypyruvate(): -1,
            # NAD: 1,
            # glycerate: 1
        },
        args=[
            n.hydroxypyruvate(),
            vmax,
            f"kms_{name}",
        ],
    )
    return model


def _add_catalase(model: Model, per: str) -> Model:
    """catalase

    2 H2O2 <=> 2 H2O + O2

    Equilibrator
    2 H2O2(aq) ⇌ 2 H2O(l) + O2(aq)
    Keq = 4.3e33 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    name = "catalase"
    vmax = add_vmax(model, name, kcat=760500)
    model.add_parameter(f"kms_{name}", 137.9)
    model.add_reaction_from_args(
        rate_name=f"{name}",
        function=michaelis_menten_1s,
        stoichiometry={
            n.h2o2(): -1,
        },
        args=[
            n.h2o2(),
            vmax,
            f"kms_{name}",
        ],
    )
    return model


def get_model(
    *,
    static_co2: bool = True,
    chl_stroma: str = "",
    per: str = "",
    mit: str = "",
) -> Model:
    model = Model()
    model.add_compounds(
        [
            n.glycolate(),
            n.glyoxylate(),
            n.gly(),
            n.ser(),
            n.hydroxypyruvate(),
            n.h2o2(),
        ]
    )
    _add_phosphoglycolate_phosphatase(model=model, chl=chl_stroma)
    _add_glycolate_oxidase(model=model, chl=chl_stroma, per=per)
    _add_glycine_transaminase(model=model, per=per)
    _add_glycine_decarboxylase(
        model=model, per=per, mit=mit, static_co2=static_co2
    )
    _add_serine_glyoxylate_transaminase(model=model, per=per)
    _add_glycerate_dehydrogenase(model=model, per=per)
    _add_catalase(model=model, per=per)
    return model


def get_y0(*, chl: str = "", per: str = "") -> dict[str, float]:
    return {
        n.glycolate(): 0,
        n.glyoxylate(): 0,
        n.glycine(): 0,
        n.serine(): 0,
        n.hydroxypyruvate(): 0,
        n.h2o2(): 0,
    }
