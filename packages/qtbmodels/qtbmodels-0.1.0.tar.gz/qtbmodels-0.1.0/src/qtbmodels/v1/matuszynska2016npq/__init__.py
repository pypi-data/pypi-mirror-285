"""Matuszyńska et al PETC model


FIXME: build this from Ebenhöh 2014
"""

from __future__ import annotations

import math
from typing import cast

import numpy as np
from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n
from qtbmodels.v1.shared import mass_action_1s, moiety_1, neg_div, proportional


def neg_one_div_by(x: float) -> float:
    return -1.0 / x


def two_div_by(x: float) -> float:
    return 2.0 / x


def four_div_by(x: float) -> float:
    return 4.0 / x


def keq_atp(
    pH: float,
    DeltaG0_ATP: float,
    dG_pH: float,
    HPR: float,
    pHstroma: float,
    Pi_mol: float,
    RT: float,
) -> float:
    DG = DeltaG0_ATP - dG_pH * HPR * (pHstroma - pH)
    Keq = Pi_mol * np.exp(-DG / RT)
    return cast(float, Keq)


def keq_cytb6f(
    pH: float,
    F: float,
    E0_PQ: float,
    E0_PC: float,
    pHstroma: float,
    RT: float,
    dG_pH: float,
) -> float:
    DG1 = -2 * F * E0_PQ
    DG2 = -F * E0_PC
    DG = -(DG1 + 2 * dG_pH * pH) + 2 * DG2 + 2 * dG_pH * (pHstroma - pH)
    Keq = np.exp(-DG / RT)
    return cast(float, Keq)


def ph_lumen(protons: float) -> float:
    return cast(float, -np.log10(protons * 0.00025))


def quencher(
    Psbs: float,
    Vx: float,
    Psbsp: float,
    Zx: float,
    y0: float,
    y1: float,
    y2: float,
    y3: float,
    kZSat: float,
) -> tuple[float]:
    """co-operative 4-state quenching mechanism
    gamma0: slow quenching of (Vx - protonation)
    gamma1: fast quenching (Vx + protonation)
    gamma2: fastest possible quenching (Zx + protonation)
    gamma3: slow quenching of Zx present (Zx - protonation)
    """
    ZAnt = Zx / (Zx + kZSat)
    return (
        y0 * Vx * Psbs
        + y1 * Vx * Psbsp
        + y2 * ZAnt * Psbsp
        + y3 * ZAnt * Psbs,
    )


def ps2states(
    PQ: float,
    PQred: float,
    ps2cs: float,
    Q: float,
    PSIItot: float,
    k2: float,
    kF: float,
    _kH: float,
    Keq_PQred: float,
    kPQred: float,
    pfd: float,
    kH0: float,
) -> tuple[float, float, float, float]:
    L = ps2cs * pfd
    kH = kH0 + _kH * Q
    k3p = kPQred * PQ
    k3m = kPQred * PQred / Keq_PQred

    Bs = []

    if isinstance(kH, float) and isinstance(PQ, np.ndarray):
        kH = np.repeat(kH, len(PQ))

    for L, kH, k3p, k3m in zip(L, kH, k3p, k3m):  # type: ignore
        M = np.array(
            [
                [-L - k3m, kH + kF, k3p, 0],
                [L, -(kH + kF + k2), 0, 0],
                [0, 0, L, -(kH + kF)],
                [1, 1, 1, 1],
            ]
        )
        A = np.array([0, 0, 0, PSIItot])
        B0, B1, B2, B3 = np.linalg.solve(M, A)
        Bs.append([B0, B1, B2, B3])
    return np.array(Bs).T  # type: ignore


def fluorescence(
    Q: float,
    B0: float,
    B2: float,
    ps2cs: float,
    k2: float,
    kF: float,
    kH: float,
) -> float:
    return ps2cs * kF * B0 / (kF + k2 + kH * Q) + ps2cs * kF * B2 / (
        kF + kH * Q
    )


def ps1states(
    PC: float,
    PCred: float,
    Fd: float,
    Fdred: float,
    ps2cs: float,
    PSItot: float,
    kFdred: float,
    Keq_FAFd: float,
    Keq_PCP700: float,
    kPCox: float,
    pfd: float,
) -> tuple[float]:
    """QSSA calculates open state of PSI
    depends on reduction states of plastocyanin and ferredoxin
    C = [PC], F = [Fd] (ox. forms)
    """
    L = (1 - ps2cs) * pfd
    A1 = PSItot / (
        1
        + L / (kFdred * Fd)
        + (1 + Fdred / (Keq_FAFd * Fd))
        * (PC / (Keq_PCP700 * PCred) + L / (kPCox * PCred))
    )
    return (A1,)


def ps2_crosssection(
    LHC: float,
    staticAntII: float,
    staticAntI: float,
) -> float:
    return staticAntII + (1 - staticAntII - staticAntI) * LHC


def dG_pH(r: float, t: float) -> float:
    return math.log(10) * r * t


def keq_pq_red(
    E0_QA: float,
    F: float,
    E0_PQ: float,
    pHstroma: float,
    dG_pH: float,
    RT: float,
) -> float:
    DG1 = -E0_QA * F
    DG2 = -2 * E0_PQ * F
    DG = -2 * DG1 + DG2 + 2 * pHstroma * dG_pH
    K: float = np.exp(-DG / RT)
    return K


def keq_cyc(
    E0_Fd: float,
    F: float,
    E0_PQ: float,
    pHstroma: float,
    dG_pH: float,
    RT: float,
) -> float:
    DG1 = -E0_Fd * F
    DG2 = -2 * E0_PQ * F
    DG = -2 * DG1 + DG2 + 2 * dG_pH * pHstroma
    K: float = np.exp(-DG / RT)
    return K


def keq_faf_d(
    E0_FA: float,
    F: float,
    E0_Fd: float,
    RT: float,
) -> float:
    DG1 = -E0_FA * F
    DG2 = -E0_Fd * F
    DG = -DG1 + DG2
    K: float = np.exp(-DG / RT)
    return K


def keq_pcp700(
    E0_PC: float,
    F: float,
    E0_P700: float,
    RT: float,
) -> float:
    DG1 = -E0_PC * F
    DG2 = -E0_P700 * F
    DG = -DG1 + DG2
    K: float = np.exp(-DG / RT)
    return K


def keq_fnr(
    E0_Fd: float,
    F: float,
    E0_NADP: float,
    pHstroma: float,
    dG_pH: float,
    RT: float,
) -> float:
    DG1 = -E0_Fd * F
    DG2 = -2 * E0_NADP * F
    DG = -2 * DG1 + DG2 + dG_pH * pHstroma
    K: float = np.exp(-DG / RT)
    return K


def ps1(
    A: float,
    ps2cs: float,
    pfd: float,
) -> float:
    return (1 - ps2cs) * pfd * A


def ps2(
    B1: float,
    k2: float,
) -> float:
    return 0.5 * k2 * B1


def ptox(
    pq_red: float,
    kPTOX: float,
    O2: float,
) -> float:
    """calculates reaction rate of PTOX"""
    return pq_red * kPTOX * O2


def b6f(
    PC_ox: float,
    PQ_ox: float,
    PQ_red: float,
    PC_red: float,
    Keq_B6f: float,
    kCytb6f: float,
) -> float:
    return cast(
        float,
        np.maximum(
            kCytb6f * (PQ_red * PC_ox**2 - PQ_ox * PC_red**2 / Keq_B6f),
            -kCytb6f,
        ),
    )


def cyclic_electron_flow(
    Pox: float,
    Fdred: float,
    kcyc: float,
) -> float:
    return kcyc * Fdred**2 * Pox


def fnr(
    Fd_ox: float,
    Fd_red: float,
    NADPH: float,
    NADP: float,
    KM_FNR_F: float,
    KM_FNR_N: float,
    EFNR: float,
    kcatFNR: float,
    Keq_FNR: float,
) -> float:
    fdred = Fd_red / KM_FNR_F
    fdox = Fd_ox / KM_FNR_F
    nadph = NADPH / KM_FNR_N
    nadp = NADP / KM_FNR_N
    return (
        EFNR
        * kcatFNR
        * (fdred**2 * nadp - fdox**2 * nadph / Keq_FNR)
        / (
            (1 + fdred + fdred**2) * (1 + nadp)
            + (1 + fdox + fdox**2) * (1 + nadph)
            - 1
        )
    )


def protons_stroma(ph: float) -> float:
    return 4000.0 * 10 ** (-ph)


def leak(
    protons_lumen: float,
    k_leak: float,
    ph_stroma: float,
) -> float:
    return k_leak * (protons_lumen - protons_stroma(ph_stroma))


def state_transition_ps1_ps2(
    Ant: float,
    Pox: float,
    kStt7: float,
    PQtot: float,
    KM_ST: float,
    n_ST: float,
) -> float:
    kKin = kStt7 * (1 / (1 + (Pox / PQtot / KM_ST) ** n_ST))
    return kKin * Ant  # type: ignore


def atp_synthase(
    ATP: float,
    ADP: float,
    Keq_ATPsynthase: float,
    kATPsynth: float,
) -> float:
    return kATPsynth * (ADP - ATP / Keq_ATPsynthase)


def protonation_hill(
    Vx: float,
    H: float,
    nH: float,
    k_fwd: float,
    kphSat: float,
) -> float:
    return k_fwd * (H**nH / (H**nH + protons_stroma(kphSat) ** nH)) * Vx  # type: ignore


def _add_derived_constants(model: Model) -> Model:
    model.add_parameter("E^0_QA", -0.14)
    model.add_parameter("E^0_PQ", 0.354)
    model.add_parameter("E^0_PC", 0.38)
    model.add_parameter("E^0_P700", 0.48)
    model.add_parameter("E^0_FA", -0.55)
    model.add_parameter("E^0_Fd", -0.43)
    model.add_parameter("E^0_NADP", -0.113)
    model.add_derived_parameter("RT", proportional, ["R", "T"])
    model.add_derived_parameter("dG_pH", dG_pH, ["R", "T"])
    model.add_derived_parameter(
        "Keq_PQred",
        keq_pq_red,
        ["E^0_QA", "F", "E^0_PQ", "pHstroma", "dG_pH", "RT"],
    )
    model.add_derived_parameter(
        "Keq_FAFd", keq_faf_d, ["E^0_FA", "F", "E^0_Fd", "RT"]
    )
    model.add_derived_parameter(
        "Keq_PCP700", keq_pcp700, ["E^0_PC", "F", "E^0_P700", "RT"]
    )
    model.add_derived_parameter(
        "Keq_FNR",
        keq_fnr,
        ["E^0_Fd", "F", "E^0_NADP", "pHstroma", "dG_pH", "RT"],
    )

    model.add_parameter("NADP_total", 0.8)
    model.add_derived_parameter(
        parameter_name=n.nadp(),
        function=moiety_1,
        parameters=[n.nadph(), "NADP_total"],
    )
    return model


def _add_moieties(model: Model) -> Model:
    model.add_parameter("PQ_total", 17.5)
    model.add_parameter("PC_total", 4.0)
    model.add_parameter("Fd_total", 5.0)
    model.add_parameter("AP_total", 2.55)
    model.add_parameter("LHC_total", 1)
    model.add_parameter("PSBS_total", 1.0)
    model.add_parameter("Carotenoids_total", 1.0)

    model.add_algebraic_module_from_args(
        module_name=n.adp(),
        function=moiety_1,
        derived_compounds=[n.adp()],
        args=[n.atp(), "AP_total"],
    )
    model.add_algebraic_module_from_args(
        module_name=n.pq_red(),
        function=moiety_1,
        derived_compounds=[n.pq_red()],
        args=[n.pq_ox(), "PQ_total"],
    )
    model.add_algebraic_module_from_args(
        module_name=n.pc_red(),
        function=moiety_1,
        derived_compounds=[n.pc_red()],
        args=[n.pc_ox(), "PC_total"],
    )
    model.add_algebraic_module_from_args(
        module_name=n.fd_red(),
        function=moiety_1,
        derived_compounds=[n.fd_red()],
        args=[n.fd_ox(), "Fd_total"],
    )
    model.add_algebraic_module_from_args(
        module_name="LHC_protonation",
        function=moiety_1,
        derived_compounds=[n.lhcp()],
        args=[n.lhc(), "LHC_total"],
    )
    model.add_algebraic_module_from_args(
        module_name=n.zx(),
        function=moiety_1,
        derived_compounds=[n.zx()],
        args=[n.vx(), "Carotenoids_total"],
    )
    model.add_algebraic_module_from_args(
        module_name="PSBS_protonation",
        function=moiety_1,
        derived_compounds=[n.psbs_pr()],
        args=[n.psbs_de(), "PSBS_total"],
    )
    return model


def _add_ps2_cross_section(model: Model) -> Model:
    model.add_parameter("staticAntI", 0.37)
    model.add_parameter("staticAntII", 0.1)
    model.add_algebraic_module_from_args(
        module_name="ps2crosssection",
        function=ps2_crosssection,
        derived_compounds=[n.ps2cs()],
        args=[n.lhc(), "staticAntII", "staticAntI"],
    )
    return model


def _add_quencher(model: Model) -> Model:
    model.add_parameter("gamma0", 0.1)
    model.add_parameter("gamma1", 0.25)
    model.add_parameter("gamma2", 0.6)
    model.add_parameter("gamma3", 0.15)
    model.add_parameter("kZSat", 0.12)
    model.add_algebraic_module_from_args(
        module_name=n.quencher(),
        function=quencher,
        derived_compounds=[n.quencher()],
        args=[
            n.psbs_de(),
            n.vx(),
            n.psbs_pr(),
            n.zx(),
            "gamma0",
            "gamma1",
            "gamma2",
            "gamma3",
            "kZSat",
        ],
    )
    return model


def _add_photosystems(model: Model, chl_lumen: str) -> Model:
    """PSII: 2 H2O + 2 PQ + 4 H_stroma -> O2 + 2 PQH2 + 4 H_lumen
    PSI: Fd_ox + PC_red -> Fd_red + PC_ox
    """
    model.add_parameter("PSII_total", 2.5)
    model.add_parameter("PSI_total", 2.5)
    model.add_parameter("kH0", 500000000.0)
    model.add_parameter("kPQred", 250.0)
    model.add_parameter("kPCox", 2500.0)
    model.add_parameter("kFdred", 250000.0)
    model.add_parameter("k2", 5000000000.0)
    model.add_parameter("kH", 5000000000.0)
    model.add_parameter("kF", 625000000.0)
    model.add_algebraic_module_from_args(
        module_name="ps2states",
        function=ps2states,
        derived_compounds=[
            n.b0(),
            n.b1(),
            n.b2(),
            "B3",
        ],
        args=[
            n.pq_ox(),
            n.pq_red(),
            n.ps2cs(),
            n.quencher(),
            "PSII_total",
            "k2",
            "kF",
            "kH",
            "Keq_PQred",
            "kPQred",
            n.pfd(),
            "kH0",
        ],
    )
    model.add_algebraic_module_from_args(
        module_name="ps1states",
        function=ps1states,
        derived_compounds=[n.a1()],
        args=[
            n.pc_ox(),
            n.pc_red(),
            n.fd_ox(),
            n.fd_red(),
            n.ps2cs(),
            "PSI_total",
            "kFdred",
            "Keq_FAFd",
            "Keq_PCP700",
            "kPCox",
            n.pfd(),
        ],
    )
    model.add_readout(
        name=n.fluorescence(),
        function=fluorescence,
        args=[
            n.quencher(),
            n.b0(),
            n.b2(),
            n.ps2cs(),
            "k2",
            "kF",
            "kH",
        ],
    )
    model.add_reaction_from_args(
        rate_name="PSII",
        function=ps2,
        stoichiometry={n.pq_ox(): -1},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                function=two_div_by, args=["bH"]
            ),
        },
        args=[n.b1(), "k2"],
    )
    model.add_reaction_from_args(
        rate_name="PSI",
        function=ps1,
        stoichiometry={n.fd_ox(): -1, n.pc_ox(): 1},
        args=[n.a1(), n.ps2cs(), n.pfd()],
    )
    return model


def _add_ph_lumen(model: Model, chl_lumen: str) -> Model:
    model.add_algebraic_module_from_args(
        module_name="ph_lumen",
        function=ph_lumen,
        derived_compounds=[n.ph(chl_lumen)],
        args=[n.h(chl_lumen)],
    )
    return model


def _add_ptox(model: Model) -> Model:
    """Plastid terminal oxidase

    2 QH2 + O2 -> 2 Q + 2 H2O
    """
    model.add_parameter("kPTOX", 0.01)
    model.add_reaction_from_args(
        rate_name="PTOX",
        function=ptox,
        stoichiometry={n.pq_ox(): 1},
        args=[n.pq_red(), "kPTOX", "O2_lumen"],
    )
    return model


def _add_ndh(model: Model) -> Model:
    """NAD(P)H dehydrogenase-like complex (NDH)

    PQH2 -> PQ

    """
    model.add_parameter("kNDH", 0.002)
    model.add_reaction_from_args(
        rate_name="NDH",
        function=mass_action_1s,
        stoichiometry={n.pq_ox(): -1},
        args=[n.pq_ox(), "kNDH"],
    )
    return model


def _add_b6f(model: Model, chl_lumen: str) -> Model:
    model.add_parameter("kCytb6f", 2.5)
    model.add_algebraic_module_from_args(
        module_name="Keq_B6f",
        function=keq_cytb6f,
        derived_compounds=["Keq_B6f"],
        args=[
            n.ph(chl_lumen),
            "F",
            "E^0_PQ",
            "E^0_PC",
            "pHstroma",
            "RT",
            "dG_pH",
        ],
    )
    model.add_reaction_from_args(
        rate_name="B6f",
        function=b6f,
        stoichiometry={n.pc_ox(): -2, n.pq_ox(): 1},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                function=four_div_by, args=["bH"]
            )
        },
        args=[
            n.pc_ox(),
            n.pq_ox(),
            n.pq_red(),
            n.pc_red(),
            "Keq_B6f",
            "kCytb6f",
        ],
    )
    return model


def _add_cyclic_electron_flow(model: Model) -> Model:
    model.add_parameter("kcyc", 1.0)
    model.add_reaction_from_args(
        rate_name="cyclic_electron_flow",
        function=cyclic_electron_flow,
        stoichiometry={n.pq_ox(): -1, n.fd_ox(): 2},
        args=[n.pq_ox(), n.fd_red(), "kcyc"],
    )
    return model


def _add_fnr(model: Model) -> Model:
    """Ferredoxin-NADP reductase"""
    model.add_parameter("KM_FNR_F", 1.56)
    model.add_parameter("KM_FNR_N", 0.22)
    model.add_parameter("EFNR", 3.0)
    model.add_parameter("kcatFNR", 500.0)
    model.add_reaction_from_args(
        rate_name="FNR",
        function=fnr,
        stoichiometry={n.fd_ox(): 2},
        args=[
            n.fd_ox(),
            n.fd_red(),
            n.nadph(),
            n.nadp(),
            "KM_FNR_F",
            "KM_FNR_N",
            "EFNR",
            "kcatFNR",
            "Keq_FNR",
        ],
    )
    return model


def _add_state_transitions(model: Model) -> Model:
    model.add_parameter("kStt7", 0.0035)
    model.add_parameter("KM_ST", 0.2)
    model.add_parameter("n_ST", 2.0)
    model.add_parameter("kPph1", 0.0013)
    model.add_reaction_from_args(
        rate_name="St12",
        function=state_transition_ps1_ps2,
        stoichiometry={n.lhc(): -1},
        args=[
            n.lhc(),
            n.pq_ox(),
            "kStt7",
            "PQ_total",
            "KM_ST",
            "n_ST",
        ],
    )
    model.add_reaction_from_args(
        rate_name="St21",
        function=mass_action_1s,
        stoichiometry={n.lhc(): 1},
        args=[n.lhcp(), "kPph1"],
    )
    return model


def _add_atp_synthase(model: Model, chl_lumen: str) -> Model:
    model.add_parameter("kATPsynth", 20.0)
    model.add_parameter("Pi_mol", 0.01)
    model.add_parameter("HPR", 14.0 / 3.0)
    model.add_parameter("DeltaG0_ATP", 30.6)
    model.add_algebraic_module_from_args(
        module_name="Keq_ATPsynthase",
        function=keq_atp,
        derived_compounds=["Keq_ATPsynthase"],
        args=[
            n.ph(chl_lumen),
            "DeltaG0_ATP",
            "dG_pH",
            "HPR",
            "pHstroma",
            "Pi_mol",
            "RT",
        ],
    )
    model.add_reaction_from_args(
        rate_name="atp_synthase",
        function=atp_synthase,
        stoichiometry={n.atp(): 1},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                function=neg_div, args=["HPR", "bH"]
            ),
        },
        args=[
            n.atp(),
            n.adp(),
            "Keq_ATPsynthase",
            "kATPsynth",
        ],
    )
    return model


def _add_atp_consumption(model: Model) -> Model:
    model.add_parameter("kATPconsumption", 10.0)
    model.add_reaction_from_args(
        rate_name="ex_atp",
        function=mass_action_1s,
        stoichiometry={n.atp(): -1},
        args=[n.atp(), "kATPconsumption"],
    )
    return model


def _add_epoxidase(model: Model, chl_lumen: str) -> Model:
    """Violaxanthin -> Antheraxanthin -> Zeaxanthin

    Zeaxanthin Epoxidase (stroma):
        Zeaxanthin + NADPH + O2 -> Anteraxanthin + NADP + H2O
        Antheraxanthin + NADPH + O2 -> Violaxanthin + NADP + H2O

    Violaxanthin Deepoxidase (lumen)
        Violaxanthin + Ascorbate -> Antheraxanthin + Dehydroascorbate + H2O
        Antheraxanthin + Ascorbate -> Zeaxanthin + Dehydroascorbate + H2O
    """
    model.add_parameter("kHillX", 5.0)
    model.add_parameter("kDeepoxV", 0.0024)
    model.add_parameter("kEpoxZ", 0.00024)
    model.add_parameter("kphSat", 5.8)
    model.add_reaction_from_args(
        rate_name="Violaxanthin_deepoxidase",
        function=protonation_hill,
        stoichiometry={n.vx(): -1},
        args=[
            n.vx(),
            n.h(chl_lumen),
            "kHillX",
            "kDeepoxV",
            "kphSat",
        ],
    )
    model.add_reaction_from_args(
        rate_name="Zeaxanthin_epoxidase",
        function=mass_action_1s,
        stoichiometry={n.vx(): 1},
        args=[n.zx(), "kEpoxZ"],
    )
    return model


def _add_lhc_protonation(model: Model, chl_lumen: str) -> Model:
    model.add_parameter("kH_LHC", 3.0)
    model.add_parameter("k_lhc_protonation", 0.0096)
    model.add_parameter("k_lhc_deprotonation", 0.0096)
    model.add_parameter("kph_sat_lhc", 5.8)
    model.add_reaction_from_args(
        rate_name="LHC_protonation",
        function=protonation_hill,
        stoichiometry={n.psbs_de(): -1},
        args=[
            n.psbs_de(),
            n.h(chl_lumen),
            "kH_LHC",
            "k_lhc_protonation",
            "kph_sat_lhc",
        ],
    )
    model.add_reaction_from_args(
        rate_name="LHC_deprotonation",
        function=mass_action_1s,
        stoichiometry={n.psbs_de(): 1},
        args=[n.psbs_pr(), "k_lhc_deprotonation"],
    )
    return model


def _add_proton_leak(model: Model, chl_lumen: str) -> Model:
    model.add_parameter("kLeak", 10.0)
    model.add_reaction_from_args(
        rate_name="proton_leak",
        function=leak,
        stoichiometry={},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                function=neg_one_div_by, args=["bH"]
            )
        },
        args=[n.h(chl_lumen), "kLeak", "pHstroma"],
    )
    return model


def get_model(chl_lumen: str = "_lumen") -> Model:
    model = Model()
    model.add_compounds(
        [
            n.atp(),
            n.pq_ox(),
            n.pc_ox(),
            n.fd_ox(),
            n.h(chl_lumen),
            n.lhc(),
            n.psbs_de(),
            n.vx(),
        ]
    )
    model.add_parameters(
        {
            n.nadph(): 0.6,  # FIXME: check this
            "pHstroma": 7.9,
            "bH": 100.0,
            "O2_lumen": 8.0,
            n.pfd(): 100.0,
            "F": 96.485,
            "R": 0.0083,
            "T": 298.0,
        }
    )
    _add_derived_constants(model)
    _add_moieties(model)
    _add_ps2_cross_section(model)
    _add_quencher(model)
    _add_photosystems(model, chl_lumen=chl_lumen)
    _add_ph_lumen(model, chl_lumen=chl_lumen)
    _add_ptox(model)
    _add_ndh(model)
    _add_b6f(model, chl_lumen=chl_lumen)
    _add_cyclic_electron_flow(model)
    _add_fnr(model)
    _add_state_transitions(model)
    _add_epoxidase(model, chl_lumen=chl_lumen)
    _add_lhc_protonation(model, chl_lumen=chl_lumen)
    _add_atp_synthase(model, chl_lumen=chl_lumen)
    _add_atp_consumption(model)
    _add_proton_leak(model, chl_lumen=chl_lumen)
    return model


def get_y0(chl_lumen: str = "_lumen") -> dict[str, float]:
    return {
        n.atp(): 1.6999999999999997,
        n.pq_ox(): 4.706348349506148,
        n.pc_ox(): 3.9414515288091567,
        n.fd_ox(): 3.7761613271207324,
        n.h(chl_lumen): 7.737821100836988,
        n.lhc(): 0.5105293511676007,
        n.psbs_de(): 0.5000000001374878,
        n.vx(): 0.09090909090907397,
    }
