from __future__ import annotations

from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n
from qtbmodels.v1.saadat2021 import _add_thioredoxin_regulation
from qtbmodels.v1.saadat2021 import get_model as get_saadat2021
from qtbmodels.v1.shared import (
    add_vmax,
    michaelis_menten_1s_1i,
    michaelis_menten_2s,
    proportional,
    reversible_michaelis_menten_1s_1p_1i,
    reversible_michaelis_menten_2s_2p,
    reversible_michaelis_menten_3s_4p,
)
from qtbmodels.v1.yokota1985 import get_model as get_yokota1985


def get_redox_pair(oxidised_form: str) -> tuple[str, str]:
    if oxidised_form == n.nad():
        return n.nad(), n.nadh()
    elif oxidised_form == n.nadp():
        return n.nadp(), n.nadph()
    else:
        msg = "Unknown redox pair"
        raise NotImplementedError(msg)


def one_div(x: float) -> float:
    return 1 / x


def mul(x: float, y: float) -> float:
    return x * y


def div(x: float, y: float) -> float:
    return x / y


def glycerate_kinase(
    s1: float,
    s2: float,
    i1: float,
    vmax: float,
    km_s1: float,
    km_s2: float,
    ki1: float,
) -> float:
    return (
        vmax * s1 * s2 / (s1 * s2 + s1 * km_s1 + s2 * km_s2 * (1 + i1 / ki1))
    )


def P_i(
    phosphate_total: float,
    pga: float,
    bpga: float,
    gap: float,
    dhap: float,
    fbp: float,
    f6p: float,
    g6p: float,
    g1p: float,
    sbp: float,
    s7p: float,
    e4p: float,
    x5p: float,
    r5p: float,
    rubp: float,
    ru5p: float,
    atp: float,
    pgo: float,
) -> float:
    return phosphate_total - (
        pga
        + 2 * bpga
        + gap
        + dhap
        + 2 * fbp
        + f6p
        + g6p
        + g1p
        + 2 * sbp
        + s7p
        + e4p
        + x5p
        + r5p
        + 2 * rubp
        + ru5p
        + atp
        + pgo
    )


def _update_phosphoglycolate_phosphatase(model: Model) -> Model:
    """phosphoglycolate phosphatase, EC 3.1.3.18

    H2O(chl) + PGO(chl) <=> Orthophosphate(chl) + Glycolate(chl)

    Equilibrator
    H2O(l) + PGO(aq) ⇌ Orthophosphate(aq) + Glycolate(aq)
    Keq = 3.1e5 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    enzyme = "phosphoglycolate_phosphatase"
    model.remove_parameters(["pgo_influx"])

    vmax = add_vmax(model, enzyme, kcat=292)
    model.add_parameter(f"kms_{enzyme}", 0.029)
    model.add_parameter(f"kmi_{enzyme}_pi", 12.0)
    model.update_reaction_from_args(
        rate_name=enzyme,
        function=michaelis_menten_1s_1i,
        stoichiometry={
            n.pgo(): -1,
            # H2O: -1
            n.glycolate(): 1,
            # n.pi(): 1,
        },
        args=[
            n.pgo(),
            n.pi(),
            vmax,
            f"kms_{enzyme}",
            f"kmi_{enzyme}_pi",
        ],
    )
    return model


def _update_glycerate_dehydrogenase(model: Model) -> Model:
    """glycerate dehydrogenase

    NADH + Hydroxypyruvate <=> NAD  + D-Glycerate

    Equilibrator
    NADH(aq) + Hydroxypyruvate(aq) ⇌ NAD(aq) + D-Glycerate(aq)
    Keq = 8.7e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.update_reaction_from_args(
        rate_name="glycerate_dehydrogenase",
        function=michaelis_menten_2s,
        stoichiometry={
            n.nadph(): -1,
            n.hydroxypyruvate(): -1,
            # NADP: 1,
            n.glycerate(): 1,
        },
        args=[
            n.hydroxypyruvate(),
            n.nadph(),
            "Vmax_glycerate_dehydrogenase",
            "kms_glycerate_dehydrogenase",
        ],
    )
    return model


def glycine_decarboxylase(
    s1: float,
    s2: float,
    vmax: float,
    km: float,
) -> float:
    """Simplified ping-pong mechanism, when only one km is known"""
    s2 = s2 / 2
    return vmax * s1 * s2 / (s1 * s2 + km * s1 + km * s2)


def _update_glycine_decarboxylase(model: Model, static_co2: bool) -> Model:
    """glycine decarboxylase

    2 Glycine + NAD + 2 H2O ⇌ Serine + NH3 + NADH + CO2

    Equilibrator
    2 Glycine(aq) + NAD(aq) + 2 H2O(l) ⇌ Serine(aq) + NH3(aq) + NADH(aq) + CO2(total)
    Keq = 2.4e-4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    if not static_co2:
        raise NotImplementedError
    name = "glycine_decarboxylase"
    model.update_reaction_from_args(
        rate_name=name,
        function=glycine_decarboxylase,
        stoichiometry=model.stoichiometries[name] | {n.nadph(): 0.5},
        args=[
            n.gly(),
            n.nadp(),
            "Vmax_glycine_decarboxylase",
            "kms_glycine_decarboxylase",
        ],
    )
    return model


def _update_phosphate_moiety(model: Model) -> Model:
    model.update_algebraic_module_from_args(
        "Phosphate_moiety",
        function=P_i,
        args=[*model.algebraic_modules["Phosphate_moiety"].args, n.pgo()],
    )
    return model


def _add_glycerate_kinase(model: Model) -> Model:
    """glycerate kinase

    ATP + D-Glycerate <=> ADP + 3-Phospho-D-glycerate

    Equilibrator
    ATP(aq) + D-Glycerate(aq) ⇌ ADP(aq) + 3-Phospho-D-glycerate(aq)
    Keq = 4.9e2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    vmax = add_vmax(model, "glycerate_kinase", kcat=5.71579)
    model.add_parameter("kms_glycerate_kinase_glycerate", 0.25)
    model.add_parameter("kms_glycerate_kinase_atp", 0.21)
    model.add_parameter("ki_glycerate_kinase_pga", 0.36)
    model.add_reaction_from_args(
        rate_name="glycerate_kinase",
        function=glycerate_kinase,
        stoichiometry={
            n.glycerate(): -1,
            n.atp(): -1,
            n.pga(): 1,
        },
        args=[
            n.glycerate(),
            n.atp(),
            n.pga(),
            vmax,
            "kms_glycerate_kinase_glycerate",
            "kms_glycerate_kinase_atp",
            "ki_glycerate_kinase_pga",
        ],
    )
    return model


def _convert_yokota_kcats(model: Model) -> Model:
    """Convert kcat parameters from 1/hour to 1/second"""
    for i in (
        "kcat_glycolate_oxidase",
        "kcat_glycine_transaminase",
        "kcat_glycine_decarboxylase",
        "kcat_serine_glyoxylate_transaminase",
        "kcat_glycerate_dehydrogenase",
        "kcat_catalase",
    ):
        model.update_parameter(
            parameter_name=i, parameter_value=model.parameters[i] / 3600
        )
    return model


def _add_yokota_speedup_factor(
    model: Model, f_scale_yokota: float = 10
) -> Model:
    """As rubisco fluxes are higher in the combined model, it was necessary to give
    the yokota model a speedup
    """
    # model.add_parameter("f_scale_yokota", 10)
    for name in [
        "E0_phosphoglycolate_phosphatase",
        "E0_glycolate_oxidase",
        "E0_glycine_transaminase",
        "E0_glycine_decarboxylase",
        "E0_serine_glyoxylate_transaminase",
        "E0_glycerate_dehydrogenase",
        "E0_glycerate_kinase",
        "E0_catalase",
    ]:
        model.scale_parameter(name, f_scale_yokota)

        # base_value = model.parameters[name]
        # model.remove_parameter(name)
        # base_name = f"{name}_base"
        # model.add_parameter(base_name, base_value)
        # model.add_derived_parameter(
        #     parameter_name=name,
        #     function=proportional,
        #     parameters=["f_scale_yokota", base_name],
        # )
    return model


def rubisco_witzel_5i(
    rubp: float,
    s2: float,
    vmax: float,
    gamma_or_omega: float,
    co2: float,
    o2: float,
    lr: float,
    lc: float,
    lo: float,
    lrc: float,
    lro: float,
    i1: float,
    ki1: float,
    i2: float,
    ki2: float,
    i3: float,
    ki3: float,
    i4: float,
    ki4: float,
    i5: float,
    ki5: float,
) -> float:
    vmax_app = (gamma_or_omega * vmax * s2 / lr) / (
        1 / lr + co2 / lrc + o2 / lro
    )
    km_app = 1 / (1 / lr + co2 / lrc + o2 / lro)
    return (vmax_app * rubp) / (
        rubp
        + km_app
        * (
            1
            + co2 / lc
            + o2 / lo
            + i1 / ki1
            + i2 / ki2
            + i3 / ki3
            + i4 / ki4
            + i5 / ki5
        )
    )


def _add_rubisco_witzel2010(model: Model, static_co2: bool) -> Model:
    """gamma = 1 / km_co2
    omega = 1 / km_o2
    lr = k_er_minus / k_er_plus
    lc = k_er_minus / (omega * kcat_carb)
    lrc = k_er_minus / (gamma * k_er_plus)
    lro = k_er_minus / (omega * k_er_plus)
    lo = k_er_minus / (omega * k_oxy)
    """
    model.remove_reaction("rubisco_co2")
    model.remove_parameters({"kms_rubisco_co2", "kms_rubisco_rubp"})
    model.update_parameters(
        {
            "kcat_rubisco_co2": 3.1,
        }
    )

    model.add_parameters(
        {
            "k_er_plus": 0.15 * 1000,  # 1 / (mM * s)
            "k_er_minus": 0.0048,  # 1 / s
            "km_co2": 10.7 / 1000,  # mM
            "km_o2": 295 / 1000,  # mM
            "kcat_rubisco_o2": 1.125,
        }
    )

    # with new description, rubisco needed to be scaled down
    model.scale_parameter("E0_rubisco_base", 0.16)

    model.add_algebraic_module_from_args(
        module_name="E0_rubisco_o2",
        function=proportional,
        derived_compounds=["E0_rubisco_o2"],
        args=[n.e_active(), "E0_rubisco_base"],
    )
    model.add_algebraic_module_from_args(
        module_name="Vmax_rubisco_o2",
        function=proportional,
        derived_compounds=["Vmax_rubisco_o2"],
        args=[
            "E0_rubisco_o2",
            "kcat_rubisco_o2",
        ],
    )

    model.add_derived_parameter("gamma", one_div, ["km_co2"])
    model.add_derived_parameter("omega", one_div, ["km_o2"])
    model.add_derived_parameter(
        "omega_kcat_carb", mul, ["omega", "kcat_rubisco_co2"]
    )
    model.add_derived_parameter(
        "omega_koxy", mul, ["omega", "kcat_rubisco_o2"]
    )
    model.add_derived_parameter("omega_ker_plus", mul, ["omega", "k_er_plus"])
    model.add_derived_parameter("gamma_ker_plus", mul, ["gamma", "k_er_plus"])
    model.add_derived_parameter("lr", div, ["k_er_minus", "k_er_plus"])
    model.add_derived_parameter("lc", div, ["k_er_minus", "omega_kcat_carb"])
    model.add_derived_parameter("lrc", div, ["k_er_minus", "gamma_ker_plus"])
    model.add_derived_parameter("lro", div, ["k_er_minus", "omega_ker_plus"])
    model.add_derived_parameter("lo", div, ["k_er_minus", "omega_koxy"])

    args_carb = [
        n.rubp(),
        n.co2(),
        "Vmax_rubisco_co2",
        "gamma",  # 1 / km_co2
        n.co2(),
        "O2_stroma",
        "lr",
        "lc",
        "lo",
        "lrc",
        "lro",
        n.pga(),
        "Ki_1_1",
        n.fbp(),
        "Ki_1_2",
        n.sbp(),
        "Ki_1_3",
        n.pi(),
        "Ki_1_4",
        n.nadph(),
        "Ki_1_5",
    ]
    args_oxy = [
        n.rubp(),
        "O2_stroma",
        "Vmax_rubisco_o2",
        "omega",  # 1 / km_o2
        n.co2(),
        "O2_stroma",
        "lr",
        "lc",
        "lo",
        "lrc",
        "lro",
        n.pga(),
        "Ki_1_1",
        n.fbp(),
        "Ki_1_2",
        n.sbp(),
        "Ki_1_3",
        n.pi(),
        "Ki_1_4",
        n.nadph(),
        "Ki_1_5",
    ]

    stoichiometry_co2 = {
        n.rubp(): -1.0,
        n.pga(): 2.0,
    }
    stoichiometry_o2 = {
        n.rubp(): -1.0,
        n.atp(): -0.5,
        n.pga(): 1.5,
        n.pgo(): 1.0,
    }

    if static_co2:
        model.update_parameter(n.co2(), 0.012)
    else:
        stoichiometry_co2 |= {n.co2(): -1.0}

    model.add_reaction_from_args(
        rate_name="rubisco_co2",
        function=rubisco_witzel_5i,
        stoichiometry=stoichiometry_co2,
        args=args_carb,
    )
    model.add_reaction_from_args(
        rate_name="rubisco_o2",
        function=rubisco_witzel_5i,
        stoichiometry=stoichiometry_o2,
        args=args_oxy,
    )
    return model


def _update_yokota_thermo(model: Model, redox_pair: str) -> Model:
    """This is done to avoid substrate accumulation around either
    glyoxylate or glycine

    Yokota reactions

    phosphoglycolate_phosphatase, keq = 31000
        PGO -> glycolate
    glycolate_oxidase, keq = 3e15
        glycolate -> glyoxylate
    glycine_transaminase, keq = 30
        glyoxylate -> glycine
    glycine_decarboxylase, keq = 0.00024
        glycine -> serine
    serine_glyoxylate_transaminase, keq = 6
        serine -> hydroxypyruvate
    glycerate_dehydrogenase, keq = 87000.0
        hydroxypyruvate -> glycerate
    glycerate_kinase, keq = 490.0
        glycerate -> PGA

    Reactions assumed to be irreversible
        - glycolate_oxidase
    """
    ox_eq, red_eq = get_redox_pair(redox_pair)

    name = "phosphoglycolate_phosphatase"
    model.add_parameter(f"kmp_{name}", 1)
    model.add_parameter(f"Keq_{name}", 310000.0)
    model.update_reaction_from_args(
        rate_name=f"{name}",
        function=reversible_michaelis_menten_1s_1p_1i,
        args=[
            n.pgo(),
            n.glycolate(),
            n.pi(),
            f"Vmax_{name}",
            f"kms_{name}",
            f"kmp_{name}",
            f"kmi_{name}_pi",
            f"Keq_{name}",
        ],
    )

    name = "glycine_transaminase"
    model.add_parameter(f"kmp_{name}", 1)
    model.add_parameter(f"Keq_{name}", 30)
    model.update_reaction_from_args(
        rate_name=f"{name}",
        function=reversible_michaelis_menten_2s_2p,
        args=[
            n.glutamate(),
            n.glyoxylate(),
            n.oxoglutarate(),
            n.gly(),
            f"Vmax_{name}",
            f"kms_{name}",
            f"kmp_{name}",
            f"Keq_{name}",
        ],
    )

    name = "glycine_decarboxylase"
    model.add_parameter(f"kmp_{name}", 1)
    model.add_parameter(f"Keq_{name}", 0.00024)
    model.update_reaction_from_args(
        rate_name=f"{name}",
        function=reversible_michaelis_menten_3s_4p,
        args=[
            n.gly(),
            n.gly(),
            ox_eq,
            n.ser(),
            n.nh4(),
            red_eq,
            n.co2(),
            f"Vmax_{name}",
            f"kms_{name}",
            f"kmp_{name}",
            f"Keq_{name}",
        ],
    )

    name = "serine_glyoxylate_transaminase"
    model.add_parameter(f"kmp_{name}", 1)
    model.add_parameter(f"Keq_{name}", 6)
    model.update_reaction_from_args(
        rate_name=f"{name}",
        function=reversible_michaelis_menten_2s_2p,
        args=[
            n.glyoxylate(),
            n.ser(),
            n.gly(),
            n.hydroxypyruvate(),
            f"Vmax_{name}",
            "kms_transaminase_serine",
            f"kmp_{name}",
            f"Keq_{name}",
        ],
    )

    name = "glycerate_dehydrogenase"
    model.add_parameter(f"kmp_{name}", 1)
    model.add_parameter(f"Keq_{name}", 87000.0)
    model.update_reaction_from_args(
        rate_name=f"{name}",
        function=reversible_michaelis_menten_2s_2p,
        args=[
            n.hydroxypyruvate(),
            red_eq,
            n.glycerate(),
            ox_eq,
            f"Vmax_{name}",
            f"kms_{name}",
            f"kmp_{name}",
            f"Keq_{name}",
        ],
    )

    name = "glycerate_kinase"
    model.add_parameter(f"kmp_{name}", 1)
    model.add_parameter(f"Keq_{name}", 490.0)
    model.update_reaction_from_args(
        rate_name=f"{name}",
        function=reversible_michaelis_menten_2s_2p,
        args=[
            n.glycerate(),
            n.atp(),
            n.pga(),
            n.adp(),
            f"Vmax_{name}",
            "kms_glycerate_kinase_glycerate",
            f"kmp_{name}",
            f"Keq_{name}",
        ],
    )
    return model


def connect_poolman_and_yokota(model: Model, static_co2: bool) -> Model:
    """Short description.

    The Yokota model starts with an influx of glycolate from nothing
        ∅ -> GLYC
    and ends with an efflux of hydroxypyruvate into nothing
        HPA -> ∅

    In order to combine this with the poolman model, we need to add
    phophoglycolate phosphatase as an influx
        2PG -> GLYC
    update glycerate dehydrogenase to output GLYA
        ATP + D-Glycerate <=> ADP + 3-Phospho-D-glycerate
    and add glycerate kinase as an efflux.
        GLYA -> 3PG


    Since the kcat values in the yokota model are in units of 1/hour,
    we also need to transform them into units of 1/second to fit the poolman model.
    """
    _convert_yokota_kcats(model=model)
    _add_rubisco_witzel2010(model=model, static_co2=static_co2)
    _update_phosphoglycolate_phosphatase(model=model)
    _update_glycerate_dehydrogenase(model=model)
    _update_phosphate_moiety(model=model)
    _add_glycerate_kinase(model=model)
    _add_yokota_speedup_factor(model=model)

    # https://doi.org/10.1111/pce.13640
    _add_thioredoxin_regulation(model, "glycine_decarboxylase")

    model.update_parameter("E0_glycine_decarboxylase_base", 10.0)
    model.update_parameter("E0_glycolate_oxidase", 20.0)
    return model


def connect_matuszynska_and_yokota(model: Model, static_co2: bool) -> Model:
    return _update_glycine_decarboxylase(model=model, static_co2=static_co2)


def two_by_convf(convf: float) -> float:
    return 2.0 * convf


def nitrogen_fixation(
    oxo: float,
    atp: float,
    fd_red: float,
    nh4: float,
    k_fwd: float,
    convf: float,
) -> float:
    return k_fwd * oxo * atp * fd_red * convf * nh4


def add_nitrogen_metabolism(model: Model, static_nh4: bool) -> Model:
    """glycine transaminase

    L-Glutamate(per) + Glyoxylate(per) <=> 2-Oxoglutarate(per) + Glycine(per)

    Equilibrator
    L-Glutamate(aq) + Glyoxylate(aq) ⇌ 2-Oxoglutarate(aq) + Glycine(aq)
    Keq = 30 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    if static_nh4:
        model.add_parameter(n.nh4(), 1)
    else:
        model.add_compound(n.nh4())

    name = "glycine_transaminase"
    model.update_reaction_from_args(
        rate_name=name,
        function=michaelis_menten_2s,
        stoichiometry=model.stoichiometries[name]
        | {n.glutamate(): -1, n.oxoglutarate(): 1},
        args=[
            n.glyoxylate(),
            n.glutamate(),
            f"Vmax_{name}",
            f"kms_{name}",
        ],
    )

    name = "nitrogen_fixation"
    model.add_parameter(f"k_{name}", 1.0)
    stoichiometry = {
        n.oxoglutarate(): -1.0,
        n.atp(): -1.0,
        # n.fd_red(): -2.0,
        # n.nh4(): -1.0,
        n.glutamate(): 1.0,
        # ADP: 1.0,
        # n.fd_ox(): 2.0,
    }
    if not static_nh4:
        stoichiometry |= {n.nh4(): -1.0}

    model.add_reaction_from_args(
        name,
        nitrogen_fixation,
        stoichiometry=stoichiometry,
        derived_stoichiometry={
            n.fd_ox(): DerivedStoichiometry(two_by_convf, ["convf"])
        },
        args=[
            n.oxoglutarate(),
            n.atp(),
            n.fd_red(),
            n.nh4(),
            f"k_{name}",
            "convf",
        ],
    )

    name = "glycine_decarboxylase"
    if not static_nh4:
        model.update_reaction_from_args(
            name, stoichiometry=model.stoichiometries[name] | {n.nh4(): 0.5}
        )

    return model


def use_stromal_o2(model: Model) -> Model:
    rate_name = "glycolate_oxidase"
    model.update_reaction_from_args(
        rate_name,
        function=michaelis_menten_2s,
        args=[n.glycolate(), "O2_stroma"] + model.rates[rate_name].args[-2:],
    )
    return model


def get_model(
    chl_lumen: str = "_lumen", static_co2: bool = True, static_nh4: bool = True
) -> Model:
    model = get_saadat2021(static_co2=static_co2, chl_lumen=chl_lumen)
    model += get_yokota1985(static_co2=static_co2)

    model.add_compounds(
        [
            n.pgo(),
            n.glycerate(),
            n.oxoglutarate(),
            n.glutamate(),
        ]
    )
    model.add_parameters({"O2_stroma": 0.25})
    model = connect_poolman_and_yokota(model, static_co2=static_co2)
    model = connect_matuszynska_and_yokota(model, static_co2=static_co2)
    model = use_stromal_o2(model)
    model = add_nitrogen_metabolism(model, static_nh4=static_nh4)
    return _update_yokota_thermo(model, n.nadp())


def get_y0(
    chl_lumen: str = "_lumen", static_co2: bool = True, static_nh4: bool = True
) -> dict[str, float]:
    d = {
        n.pga(): 0.25115945472752155,
        n.bpga(): 0.00026174996017073353,
        n.gap(): 0.00474592159960952,
        n.dhap(): 0.10441026189281974,
        n.fbp(): 0.0035182108117367546,
        n.f6p(): 0.2824917886977682,
        n.g6p(): 0.6497311139358104,
        n.g1p(): 0.037684404606535576,
        n.sbp(): 0.006766411118705844,
        n.s7p(): 0.2119056479551733,
        n.e4p(): 0.0049850789674749695,
        n.x5p(): 0.022590901135337817,
        n.r5p(): 0.03783975884339411,
        n.rubp(): 3.275301654481358,
        n.ru5p(): 0.015135903442328416,
        n.atp(): 1.9653826315616623,
        n.fd_ox(): 3.720137630906563,
        n.h(chl_lumen): 0.002594937687115436,
        n.lhc(): 0.7872501502901426,
        n.nadph(): 0.5594446928084835,
        n.pc_ox(): 1.830325450641911,
        n.pq_ox(): 10.47810012761292,
        n.psbs_de(): 0.9396914553791271,
        n.vx(): 0.8979896438342755,
        n.tr_ox(): 0.9337843790364645,
        n.e_inactive(): 3.6097690248474366,
        n.mda(): 0.0003684677739829048,
        n.h2o2(): 0.0001728652479704914,
        n.dha(): 3.375718985573548e-05,
        n.glutathion_ox(): 1.6387483534653317e-05,
        n.glycine(): 4.747847550003459,
        n.glycolate(): 0.047478475499450765,
        n.glyoxylate(): 0.5480183370803743,
        n.hydroxypyruvate(): 0.007050820771024324,
        n.serine(): 2.0151082531362006,
        n.pgo(): 1.2187262473121726e-06,
        n.glycerate(): 0.00038314541212499146,
        n.oxoglutarate(): 1.0,
        n.glutamate(): 1.0,
    }
    if not static_co2:
        d |= {n.co2(): 0.012}
    if not static_nh4:
        d |= {n.nh4(): 1}
    return d
