from __future__ import annotations

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.v1.shared import (
    add_vmax,
    diffusion,
    michaelis_menten_1s_1i,
    michaelis_menten_1s_2i,
    moiety_1,
    proportional,
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
    )


def translocator_N(
    pi: float,
    pga: float,
    gap: float,
    dhap: float,
    k_pxt: float,
    p_ext: float,
    k_pi: float,
    k_pga: float,
    k_gap: float,
    k_dhap: float,
) -> float:
    return 1 + (1 + k_pxt / p_ext) * (
        pi / k_pi + pga / k_pga + gap / k_gap + dhap / k_dhap
    )


def rapid_equilibrium_1s_1p(
    s1: float,
    p1: float,
    k_re: float,
    q: float,
) -> float:
    return k_re * (s1 - p1 / q)


def rapid_equilibrium_2s_1p(
    s1: float,
    s2: float,
    p1: float,
    k_re: float,
    q: float,
) -> float:
    return k_re * (s1 * s2 - p1 / q)


def rapid_equilibrium_2s_2p(
    s1: float,
    s2: float,
    p1: float,
    p2: float,
    k_re: float,
    q: float,
) -> float:
    return k_re * (s1 * s2 - p1 * p2 / q)


def rapid_equilibrium_3s_3p(
    s1: float,
    s2: float,
    s3: float,
    p1: float,
    p2: float,
    p3: float,
    k_re: float,
    q: float,
) -> float:
    return k_re * (s1 * s2 * s3 - p1 * p2 * p3 / q)


def v13(
    ru5p: float,
    atp: float,
    pi: float,
    pga: float,
    rubp: float,
    adp: float,
    v13: float,
    km131: float,
    km132: float,
    ki131: float,
    ki132: float,
    ki133: float,
    ki134: float,
    ki135: float,
) -> float:
    return (
        v13
        * ru5p
        * atp
        / (
            (ru5p + km131 * (1 + pga / ki131 + rubp / ki132 + pi / ki133))
            * (atp * (1 + adp / ki134) + km132 * (1 + adp / ki135))
        )
    )


def v16(
    adp: float,
    pi: float,
    v16: float,
    km161: float,
    km162: float,
) -> float:
    return v16 * adp * pi / ((adp + km161) * (pi + km162))


def vStarchProduction(
    g1p: float,
    atp: float,
    adp: float,
    pi: float,
    pga: float,
    f6p: float,
    fbp: float,
    v_st: float,
    kmst1: float,
    kmst2: float,
    ki_st: float,
    kast1: float,
    kast2: float,
    kast3: float,
) -> float:
    return (
        v_st
        * g1p
        * atp
        / (
            (g1p + kmst1)
            * (
                (1 + adp / ki_st) * (atp + kmst2)
                + kmst2 * pi / (kast1 * pga + kast2 * f6p + kast3 * fbp)
            )
        )
    )


def rubisco(
    rubp: float,
    pga: float,
    co2: float,
    fbp: float,
    sbp: float,
    pi: float,
    nadph: float,
    vmax: float,
    kms_rubp: float,
    kms_co2: float,
    ki_pga: float,
    ki_fbp: float,
    ki_sbp: float,
    ki_p: float,
    ki_nadph: float,
) -> float:
    top = vmax * rubp * co2
    btm = (
        rubp
        + kms_rubp
        * (
            1
            + pga / ki_pga
            + fbp / ki_fbp
            + sbp / ki_sbp
            + pi / ki_p
            + nadph / ki_nadph
        )
    ) * (co2 + kms_co2)
    return top / btm


def v_out(
    s1: float,
    n_total: float,
    vmax_efflux: float,
    k_efflux: float,
) -> float:
    return vmax_efflux * s1 / (n_total * k_efflux)


def _add_constants(model: Model, chl_stroma: str) -> Model:
    model.add_parameter("kms_6", 0.03)
    model.add_parameter("kms_9", 0.013)
    model.add_parameter("kms_13_1", 0.05)
    model.add_parameter("kms_13_2", 0.05)
    model.add_parameter("kms_16_1", 0.014)
    model.add_parameter("kms_16_2", 0.3)
    model.add_parameter("kms_starch_1", 0.08)
    model.add_parameter("kms_starch_2", 0.08)
    model.add_parameter("K_pga", 0.25)
    model.add_parameter("K_gap", 0.075)
    model.add_parameter("K_dhap", 0.077)
    model.add_parameter("K_pi", 0.63)
    model.add_parameter("K_pxt", 0.74)
    model.add_parameter("Ki_1_1", 0.04)
    model.add_parameter("Ki_1_2", 0.04)
    model.add_parameter("Ki_1_3", 0.075)
    model.add_parameter("Ki_1_4", 0.9)
    model.add_parameter("Ki_1_5", 0.07)
    model.add_parameter("Ki_6_1", 0.7)
    model.add_parameter("Ki_6_2", 12.0)
    model.add_parameter("Ki_9", 12.0)
    model.add_parameter("Ki_13_1", 2.0)
    model.add_parameter("Ki_13_2", 0.7)
    model.add_parameter("Ki_13_3", 4.0)
    model.add_parameter("Ki_13_4", 2.5)
    model.add_parameter("Ki_13_5", 0.4)
    model.add_parameter("Ki_starch", 10.0)
    model.add_parameter("Ka_starch_1", 0.1)
    model.add_parameter("Ka_starch_2", 0.02)
    model.add_parameter("Ka_starch_3", 0.02)
    model.add_parameter("k_rapid_eq", 800000000.0)
    model.add_parameter("q2", 0.00031)
    model.add_parameter("q3", 16000000.0)
    model.add_parameter("q4", 22.0)
    model.add_parameter("q5", 7.1)
    model.add_parameter("q7", 0.084)
    model.add_parameter("q8", 13.0)
    model.add_parameter("q10", 0.85)
    model.add_parameter("q11", 0.4)
    model.add_parameter("q12", 0.67)
    model.add_parameter("q14", 2.3)
    model.add_parameter("q15", 0.058)
    model.add_parameter("Phosphate_total", 15.0)
    model.add_parameter("AP_total", 0.5)
    model.add_parameter("external_orthophosphate", 0.5)
    model.add_parameter(n.h(chl_stroma), 1.2589254117941661e-05)
    model.add_parameter(n.nadph(), 0.21)
    model.add_parameter(n.nadp(), 0.29)
    return model


def add_co2_dissolving(model: Model, chl_stroma: str) -> Model:
    """atmospheric CO2: ~400 ppm
    dissolved CO2:
        - freshwater: 5-20 ppm
        - seawater: 20-90 ppm
        - plant cell: 10-100 ppm

    Use 50 ppm as internal (0.012 mM), which then corresponds to 8*0.012 = 0.096 mM atmospheric CO2

    """
    model.add_parameters(
        {
            "CO2_atmosphere": 0.096,  # mM
            "k_co2_dissolving": 4.5,  # fitted
        }
    )
    model.add_reaction_from_args(
        rate_name="co2_dissolving",
        function=diffusion,
        stoichiometry={
            n.co2(): 1,
        },
        args=[
            n.co2(),
            "CO2_atmosphere",
            "k_co2_dissolving",
        ],
    )
    return model


def add_co2(model: Model, chl_stroma: str, static: bool) -> Model:
    if static:
        model.add_parameter(n.co2(), 0.2)
    else:
        model.add_compound(n.co2())
        add_co2_dissolving(model, chl_stroma)
    return model


def _add_adp_moiety(model: Model) -> Model:
    model.add_algebraic_module_from_args(
        module_name="ADP_moiety",
        function=moiety_1,
        derived_compounds=[n.adp()],
        args=[n.atp(), "AP_total"],
    )
    return model


def _add_phosphate_moiety(model: Model) -> Model:
    model.add_algebraic_module_from_args(
        module_name="Phosphate_moiety",
        function=P_i,
        derived_compounds=[n.pi()],
        args=[
            "Phosphate_total",
            n.pga(),
            n.bpga(),
            n.gap(),
            n.dhap(),
            n.fbp(),
            n.f6p(),
            n.g6p(),
            n.g1p(),
            n.sbp(),
            n.s7p(),
            n.e4p(),
            n.x5p(),
            n.r5p(),
            n.rubp(),
            n.ru5p(),
            n.atp(),
        ],
    )
    return model


def _add_translocator_moiety(model: Model) -> Model:
    model.add_algebraic_module_from_args(
        module_name="N_translocator",
        function=translocator_N,
        derived_compounds=["N_translocator"],
        args=[
            n.pi(),
            n.pga(),
            n.gap(),
            n.dhap(),
            "K_pxt",
            "external_orthophosphate",
            "K_pi",
            "K_pga",
            "K_gap",
            "K_dhap",
        ],
    )
    return model


def _add_rubisco_carboxylase(model: Model, static_co2: bool) -> Model:
    """Poolman / Pettersson name: v1

    Equilibrator
    D-Ribulose 1,5-bisphosphate(aq) + CO2(total) ⇌ 2 3-Phospho-D-glycerate(aq)
    Keq = 1.6e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.add_parameters(
        {
            "E0_rubisco": 1,
            "kcat_rubisco_co2": 0.34 * 8,
            "kms_rubisco_co2": 0.0107,
            "kms_rubisco_rubp": 0.02,
        }
    )
    model.add_derived_parameter(
        "Vmax_rubisco_co2",
        proportional,
        ["E0_rubisco", "kcat_rubisco_co2"],
    )

    stoichiometry: dict[str, float] = {
        n.rubp(): -1,
        n.pga(): 2,
    }
    if not static_co2:
        stoichiometry |= {n.co2(): -1}

    model.add_reaction_from_args(
        rate_name="rubisco_co2",
        function=rubisco,
        stoichiometry=stoichiometry,
        args=[
            n.rubp(),
            n.pga(),
            n.co2(),
            n.fbp(),
            n.sbp(),
            n.pi(),
            n.nadph(),
            "Vmax_rubisco_co2",
            "kms_rubisco_rubp",
            "kms_rubisco_co2",
            "Ki_1_1",
            "Ki_1_2",
            "Ki_1_3",
            "Ki_1_4",
            "Ki_1_5",
        ],
    )
    return model


def _add_phosphoglycerate_kinase(model: Model) -> Model:
    """Phosphoglycerate kinase (PGK), EC 2.7.2.3

    PGA + ATP <=> BPGA + ADP

    Poolman / Pettersson name: v2

    Equilibrator
    ATP(aq) + 3-Phospho-D-glycerate(aq) ⇌ ADP(aq) + 3-Phospho-D-glyceroyl phosphate(aq)
    Keq = 3.7e-4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.add_reaction_from_args(
        rate_name="pgk",
        function=rapid_equilibrium_2s_2p,
        stoichiometry={
            n.pga(): -1,
            n.atp(): -1,
            n.bpga(): 1,
        },
        args=[
            n.pga(),
            n.atp(),
            n.bpga(),
            n.adp(),
            "k_rapid_eq",
            "q2",
        ],
    )
    return model


def _add_glyceraldehyde_phosphate_dehydrogenase(
    model: Model, chl_stroma: str
) -> Model:
    """Glyceraldehyde 3-phosphate dehydrogenase (GADPH), EC 1.2.1.13

    BPGA + NADPH <=> GAP + NADP + Pi

    Poolman / Pettersson name: v3

    Equilibrator
    NADPH(aq) + 3-Phospho-D-glyceroyl phosphate(aq) ⇌ NADP (aq) + Orthophosphate(aq) + D-Glyceraldehyde 3-phosphate(aq)
    Keq = 2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.add_reaction_from_args(
        rate_name="gadph",
        function=rapid_equilibrium_3s_3p,
        stoichiometry={n.bpga(): -1, n.gap(): 1},
        args=[
            n.bpga(),
            n.nadph(),
            n.h(chl_stroma),
            n.gap(),
            n.nadp(),
            n.pi(),
            "k_rapid_eq",
            "q3",
        ],
    )
    return model


def _add_triose_phosphate_isomerase(model: Model) -> Model:
    """triose-phosphate isomerase, EC 5.3.1.1

    GAP <=> DHAP

    Poolman / Pettersson name: v4

    Equilibrator
    D-Glyceraldehyde 3-phosphate(aq) ⇌ Glycerone phosphate(aq)
    Keq = 10 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.add_reaction_from_args(
        rate_name="tpi",
        function=rapid_equilibrium_1s_1p,
        stoichiometry={n.gap(): -1, n.dhap(): 1},
        args=[n.gap(), n.dhap(), "k_rapid_eq", "q4"],
    )
    return model


def _add_aldolase(model: Model) -> Model:
    """fructose-bisphosphate aldolase, EC 4.1.2.13

    Reaction 1:
    GAP + DHAP <=> FBP
    Poolman / Pettersson name: v5

    Equilibrator
    Glycerone phosphate(aq) + D-Glyceraldehyde 3-phosphate(aq) ⇌ D-Fructose 1,6-bisphosphate(aq)
    Keq = 1.1e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

    Reaction 2:
    DHAP + EAP <=> SBP
    Poolman / Pettersson name: v8

    Equilibrator
    Glycerone phosphate(aq) + D-Erythrose 4-phosphate(aq) ⇌ Sedoheptulose 1,7-bisphosphate(aq)
    Keq = 4.8e3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)


    """
    model.add_reaction_from_args(
        rate_name="aldolase_gap_dhap",
        function=rapid_equilibrium_2s_1p,
        stoichiometry={
            n.gap(): -1,
            n.dhap(): -1,
            n.fbp(): 1,
        },
        args=[
            n.gap(),
            n.dhap(),
            n.fbp(),
            "k_rapid_eq",
            "q5",
        ],
    )
    model.add_reaction_from_args(
        rate_name="aldolase_dhap_e4p",
        function=rapid_equilibrium_2s_1p,
        stoichiometry={
            n.dhap(): -1,
            n.e4p(): -1,
            n.sbp(): 1,
        },
        args=[
            n.dhap(),
            n.e4p(),
            n.sbp(),
            "k_rapid_eq",
            "q8",
        ],
    )
    return model


def _add_fbpase(model: Model) -> Model:
    """fructose-1,6-bisphosphatase, EC 3.1.3.11

    FBP -> F6P + Pi
    Poolman / Pettersson name: v6

    Equilibrator
    H2O(l) + D-Fructose 1,6-bisphosphate(aq) ⇌ Orthophosphate(aq) + D-Fructose 6-phosphate(aq)
    Keq = 1.2e3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    vmax = add_vmax(model, "fbpase", kcat=0.2 * 8)
    model.add_reaction_from_args(
        rate_name="fbpase",
        function=michaelis_menten_1s_2i,
        stoichiometry={n.fbp(): -1, n.f6p(): 1},
        args=[
            n.fbp(),
            n.f6p(),
            n.pi(),
            vmax,
            "kms_6",
            "Ki_6_1",
            "Ki_6_2",
        ],
    )
    return model


def _add_transketolase(model: Model) -> Model:
    """Transketolase, EC 2.2.1.1

    Reaction 1:
    GAP + F6P <=> E4P + X5P
    Poolman / Pettersson name: v7

    Equilibrator
    D-Glyceraldehyde 3-phosphate(aq) + D-Fructose 6-phosphate(aq) ⇌ D-Xylulose 5-phosphate(aq) + D-Erythrose 4-phosphate(aq)
    Keq = 0.02 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

    Reaction 2:
    GAP + S7P <=> R5P + X5P
    Poolman / Pettersson name: v10

    Equilibrator
    D-Glyceraldehyde 3-phosphate(aq) + Sedoheptulose 7-phosphate(aq) ⇌ D-Ribose 5-phosphate(aq) + D-Xylulose 5-phosphate(aq)
    Keq = 0.2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.add_reaction_from_args(
        rate_name="transketolase_1",
        function=rapid_equilibrium_2s_2p,
        stoichiometry={
            n.gap(): -1,
            n.f6p(): -1,
            n.e4p(): 1,
            n.x5p(): 1,
        },
        args=[
            n.gap(),
            n.f6p(),
            n.e4p(),
            n.x5p(),
            "k_rapid_eq",
            "q7",
        ],
    )
    model.add_reaction_from_args(
        rate_name="transketolase_2",
        function=rapid_equilibrium_2s_2p,
        stoichiometry={
            n.gap(): -1,
            n.s7p(): -1,
            n.r5p(): 1,
            n.x5p(): 1,
        },
        args=[
            n.gap(),
            n.s7p(),
            n.r5p(),
            n.x5p(),
            "k_rapid_eq",
            "q10",
        ],
    )
    return model


def _add_sbpase(model: Model) -> Model:
    """SBPase, EC 3.1.3.37

    SBP -> S7P + Pi
    Poolman / Pettersson name: v9

    Equilibrator
    H2O(l) + Sedoheptulose 1,7-bisphosphate(aq) ⇌ Orthophosphate(aq) + Sedoheptulose 7-phosphate(aq)
    Keq = 2e2 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    vmax = add_vmax(model, "sbpase", kcat=0.04 * 8)
    model.add_reaction_from_args(
        rate_name="sbpase",
        function=michaelis_menten_1s_1i,
        stoichiometry={n.sbp(): -1, n.s7p(): 1},
        args=[
            n.sbp(),
            n.pi(),
            vmax,
            "kms_9",
            "Ki_9",
        ],
    )
    return model


def _add_ribose_5_phosphate_isomerase(model: Model) -> Model:
    """ribose-5-phosphate isomerase, EC 5.3.1.6

    R5P <=> Ru5P
    Poolman / Pettersson name: v11

    Equilibrator
    D-Ribose 5-phosphate(aq) ⇌ D-Ribulose 5-phosphate(aq)
    Keq = 0.4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.add_reaction_from_args(
        rate_name="rpi",
        function=rapid_equilibrium_1s_1p,
        stoichiometry={n.r5p(): -1, n.ru5p(): 1},
        args=[n.r5p(), n.ru5p(), "k_rapid_eq", "q11"],
    )
    return model


def _add_ribulose_5_phosphate_3_epimerase(model: Model) -> Model:
    """ribulose-phosphate 3-epimerase, EC 5.1.3.1

    X5P <=> Ru5P
    Poolman / Pettersson name: v12

    Equilibrator
    D-Xylulose 5-phosphate(aq) ⇌ D-Ribulose 5-phosphate(aq)
    Keq = 0.3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.add_reaction_from_args(
        rate_name="rpe",
        function=rapid_equilibrium_1s_1p,
        stoichiometry={n.x5p(): -1, n.ru5p(): 1},
        args=[n.x5p(), n.ru5p(), "k_rapid_eq", "q12"],
    )
    return model


def _add_phosphoribulokinase(model: Model) -> Model:
    """phosphoribulokinase, EC 2.7.1.19

    Ru5P + ATP <=> RuBP + ADP
    Poolman / Pettersson name: v13

    Equilibrator
    ATP(aq) + D-Ribulose 5-phosphate(aq) ⇌ ADP(aq) + D-Ribulose 1,5-bisphosphate(aq)
    Keq = 1e5 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    vmax = add_vmax(model, "prk", kcat=0.9999 * 8)
    model.add_reaction_from_args(
        rate_name="prk",
        function=v13,
        stoichiometry={
            n.ru5p(): -1,
            n.atp(): -1,
            n.rubp(): 1,
        },
        args=[
            n.ru5p(),
            n.atp(),
            n.pi(),
            n.pga(),
            n.rubp(),
            n.adp(),
            vmax,
            "kms_13_1",
            "kms_13_2",
            "Ki_13_1",
            "Ki_13_2",
            "Ki_13_3",
            "Ki_13_4",
            "Ki_13_5",
        ],
    )
    return model


def _add_glucose_6_phosphate_isomerase(model: Model) -> Model:
    """phosphohexomutase, EC 5.3.1.9

    F6P <=> G6P

    Equilibrator
    D-Fructose 6-phosphate(aq) ⇌ D-Glucose 6-phosphate(aq)
    Keq = 3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.add_reaction_from_args(
        rate_name="gpi",
        function=rapid_equilibrium_1s_1p,
        stoichiometry={n.f6p(): -1, n.g6p(): 1},
        args=[n.f6p(), n.g6p(), "k_rapid_eq", "q14"],
    )
    return model


def _add_phosphoglucomutase(model: Model) -> Model:
    """glucose phosphomutase, EC 5.4.2.2

    G6P <=> G1P

    Equilibrator
    Glucose 6-phosphate(aq) ⇌ D-Glucose-1-phosphate(aq)
    Keq = 0.05 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    model.add_reaction_from_args(
        rate_name="pgm",
        function=rapid_equilibrium_1s_1p,
        stoichiometry={n.g6p(): -1, n.g1p(): 1},
        args=[n.g6p(), n.g1p(), "k_rapid_eq", "q15"],
    )
    return model


def _add_atp_syntase(model: Model) -> Model:
    """H+-transporting two-sector ATPase, EC 3.6.3.14

    ADP + Orthophosphate -> ATP
    """
    vmax = add_vmax(model, "atp_synthase", kcat=2.8)
    model.add_reaction_from_args(
        rate_name="atp_synthase",
        function=v16,
        stoichiometry={n.atp(): 1},
        args=[
            n.adp(),
            n.pi(),
            vmax,
            "kms_16_1",
            "kms_16_2",
        ],
    )
    return model


def _add_triose_phosphate_exporters(model: Model) -> Model:
    vmax = add_vmax(model, "tp_efflux", kcat=0.25 * 8)
    model.add_reaction_from_args(
        rate_name="EX_PGA",
        function=v_out,
        stoichiometry={n.pga(): -1},
        args=[
            n.pga(),
            "N_translocator",
            vmax,
            "K_pga",
        ],
    )
    model.add_reaction_from_args(
        rate_name="EX_GAP",
        function=v_out,
        stoichiometry={n.gap(): -1},
        args=[n.gap(), "N_translocator", vmax, "K_gap"],
    )
    model.add_reaction_from_args(
        rate_name="EX_DHAP",
        function=v_out,
        stoichiometry={n.dhap(): -1},
        args=[n.dhap(), "N_translocator", vmax, "K_dhap"],
    )
    return model


def _add_starch_production(model: Model) -> Model:
    vmax = add_vmax(model, "ex_starch", kcat=0.04 * 8)
    model.add_reaction_from_args(
        rate_name="ex_starch",
        function=vStarchProduction,
        stoichiometry={n.g1p(): -1, n.atp(): -1},
        args=[
            n.g1p(),
            n.atp(),
            n.adp(),
            n.pi(),
            n.pga(),
            n.f6p(),
            n.fbp(),
            vmax,
            "kms_starch_1",
            "kms_starch_2",
            "Ki_starch",
            "Ka_starch_1",
            "Ka_starch_2",
            "Ka_starch_3",
        ],
    )
    return model


def _add_algebraic_modules(model: Model) -> Model:
    model = _add_adp_moiety(model=model)
    model = _add_phosphate_moiety(model=model)
    return _add_translocator_moiety(model=model)


def _add_rates(model: Model, static_co2: bool, chl_stroma: str) -> Model:
    model = _add_rubisco_carboxylase(model=model, static_co2=static_co2)
    model = _add_phosphoglycerate_kinase(model=model)
    model = _add_glyceraldehyde_phosphate_dehydrogenase(
        model=model, chl_stroma=chl_stroma
    )
    model = _add_triose_phosphate_isomerase(model=model)
    model = _add_aldolase(model=model)
    model = _add_fbpase(model=model)
    model = _add_transketolase(model=model)
    model = _add_sbpase(model=model)
    model = _add_ribose_5_phosphate_isomerase(model=model)
    model = _add_ribulose_5_phosphate_3_epimerase(model=model)
    model = _add_phosphoribulokinase(model=model)
    model = _add_glucose_6_phosphate_isomerase(model=model)
    model = _add_phosphoglucomutase(model=model)
    model = _add_atp_syntase(model=model)
    model = _add_triose_phosphate_exporters(model=model)
    return _add_starch_production(model=model)


def get_model(
    static_co2: bool = True,
    chl_stroma: str = "",
) -> Model:
    model = Model()
    model = _add_constants(model=model, chl_stroma=chl_stroma)
    model = add_co2(model=model, chl_stroma=chl_stroma, static=static_co2)

    model.add_compounds(
        [
            n.pga(),
            n.bpga(),
            n.gap(),
            n.dhap(),
            n.fbp(),
            n.f6p(),
            n.g6p(),
            n.g1p(),
            n.sbp(),
            n.s7p(),
            n.e4p(),
            n.x5p(),
            n.r5p(),
            n.rubp(),
            n.ru5p(),
            n.atp(),
        ]
    )
    model = _add_algebraic_modules(model)
    return _add_rates(model, static_co2=static_co2, chl_stroma=chl_stroma)


def get_y0() -> dict[str, float]:
    return {
        n.pga(): 0.6387788347932627,
        n.bpga(): 0.0013570885908749779,
        n.gap(): 0.011259431827358068,
        n.dhap(): 0.24770748227012374,
        n.fbp(): 0.01980222074817044,
        n.f6p(): 1.093666906864421,
        n.g6p(): 2.5154338857582377,
        n.g1p(): 0.14589516537322303,
        n.sbp(): 0.09132688566151095,
        n.s7p(): 0.23281380022778891,
        n.e4p(): 0.02836065066520614,
        n.x5p(): 0.03647242425941113,
        n.r5p(): 0.06109130988031577,
        n.rubp(): 0.2672164362349537,
        n.ru5p(): 0.0244365238237522,
        n.atp(): 0.43633201706180874,
    }
