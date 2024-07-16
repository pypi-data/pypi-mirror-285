"""https://doi.org/10.1098/rstb.2013.0223


Model consists of

Variables
    - Oxidised fraction of the plastoquinone pool (P)
    - Oxidised fraction of the plastocyanin pool (C)
    - Oxidised fraction of ferredoxin pool (F)
    - Stromal concentration of ATP (T)
    - Stromal concentration of NADPH (N)
    - Lumenal proton concentration (H)
    - Fraction of mobile antenna associated with PSII (A)

Reactions
    - Cytochrome b6f
    - FNR
    - Cyclic electron flow
    - ATP synthase
    - Proton leak
    - PTOX
    - NADH reductase (NDH)
    - PSI
    - PSII
    - Fluorescence
    - State transitions (Stt7, Pph1)
"""

from __future__ import annotations

import numpy as np
from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n
from qtbmodels.v1.shared import moiety_1, proportional


def two_div_by(x: float) -> float:
    return 2.0 / x


def four_div_by(x: float) -> float:
    return 4.0 / x


def neg_div(x: float, y: float) -> float:
    return -x / y


def neg_one_div_by(x: float) -> float:
    return -1.0 / x


def calculate_pHinv(x: float) -> float:
    return 4e3 * 10 ** (-x)


def dG_pH(r: float, t: float) -> float:
    return np.log(10) * r * t  # type: ignore


def Hstroma(pHstroma: float) -> float:
    return 3.2e4 * 10 ** (-pHstroma)


def kProtonation(Hstroma: float) -> float:
    return 4e-3 / Hstroma


def keq_PQred(
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
    return np.exp(-DG / RT)


def Keq_cyc(
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
    return np.exp(-DG / RT)


def Keq_FAFd(
    E0_FA: float,
    F: float,
    E0_Fd: float,
    RT: float,
) -> float:
    DG1 = -E0_FA * F
    DG2 = -E0_Fd * F
    DG = -DG1 + DG2
    return np.exp(-DG / RT)


def Keq_PCP700(
    E0_PC: float,
    F: float,
    E0_P700: float,
    RT: float,
) -> float:
    DG1 = -E0_PC * F
    DG2 = -E0_P700 * F
    DG = -DG1 + DG2
    return np.exp(-DG / RT)


def Keq_FNR(
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
    return np.exp(-DG / RT)


def Keq_ATP(
    pH: float,
    DeltaG0_ATP: float,
    dG_pH: float,
    HPR: float,
    pHstroma: float,
    Pi_mol: float,
    RT: float,
) -> float:
    DG = DeltaG0_ATP - dG_pH * HPR * (pHstroma - pH)
    return Pi_mol * np.exp(-DG / RT)


def Keq_cytb6f(
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
    return np.exp(-DG / RT)


def lhcmoiety(
    LHC: float,
) -> float:
    return 1 - LHC


def ps2crosssection(
    LHC: float,
    staticAntII: float,
    staticAntI: float,
) -> float:
    """calculates the cross section of PSII"""
    return staticAntII + (1 - staticAntII - staticAntI) * LHC


def ps2states(
    PQ: float,
    PQred: float,
    ps2cs: float,
    PSIItot: float,
    k2: float,
    kF: float,
    _kH: float,
    kH0: float,
    Keq_PQred: float,
    kPQred: float,
    pfd: float,
) -> float:
    L = ps2cs * pfd
    kH = kH0
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
) -> float:
    """QSSA calculates open state of PSI
    depends on reduction states of plastocyanin and ferredoxin
    C = [PC], F = [Fd] (ox. forms)
    accepts: light, y as an array of arrays
    returns: array of PSI open
    """
    L = (1 - ps2cs) * pfd

    return PSItot / (
        1
        + L / (kFdred * Fd)
        + (1 + Fdred / (Keq_FAFd * Fd))
        * (PC / (Keq_PCP700 * PCred) + L / (kPCox * PCred))
    )


def fluorescence(
    B0: float,
    B2: float,
    ps2cs: float,
    k2: float,
    kF: float,
    kH: float,
    kH0: float,
) -> float:
    return (ps2cs * kF * B0) / (kF + kH0 + k2 + kH) + (ps2cs * kF * B2) / (
        kF + kH0 + kH
    )


def calculate_pH(
    x: float,
) -> float:
    return -np.log(x * (2.5e-4)) / np.log(10)  # type: ignore


def PS2(
    B1: float,
    k2: float,
) -> float:
    """reaction rate constant for photochemistry"""
    return 0.5 * k2 * B1


def PS1(
    A: float,
    ps2cs: float,
    pfd: float,
) -> float:
    """reaction rate constant for open PSI"""
    L = (1 - ps2cs) * pfd
    return L * A


###############################################################################
# Other reaction rates
###############################################################################


def PTOX(
    Pred: float,
    kPTOX: float,
    O2ext: float,
) -> float:
    """calculates reaction rate of PTOX"""
    return Pred * kPTOX * O2ext


def NDH(
    Pox: float,
    kNDH: float,
) -> float:
    """calculates reaction rate of PQ reduction under absence of oxygen
    can be mediated by NADH reductase NDH
    """
    return kNDH * Pox


def B6f(
    PC: float,
    Pox: float,
    Pred: float,
    PCred: float,
    pH: float,
    kCytb6f: float,
    F: float,
    E0_PQ: float,
    E0_PC: float,
    pHstroma: float,
    RT: float,
    dG_pH: float,
) -> float:
    """calculates reaction rate of cytb6f"""
    Keq = Keq_cytb6f(pH, F, E0_PQ, E0_PC, pHstroma, RT, dG_pH)
    return np.maximum(kCytb6f * (Pred * PC**2 - (Pox * PCred**2) / Keq), -kCytb6f)


def Cyc(
    Pox: float,
    Fdred: float,
    kcyc: float,
) -> float:
    """calculates reaction rate of cyclic electron flow
    considered as practically irreversible
    """
    return kcyc * ((Fdred**2) * Pox)


def FNR(
    Fd: float,
    Fdred: float,
    NADPH: float,
    NADP: float,
    KM_FNR_F: float,
    KM_FNR_N: float,
    EFNR: float,
    kcatFNR: float,
    Keq_FNR: float,
) -> float:
    """Reaction rate mediated by the Ferredoxin—NADP(+) reductase (FNR)
    Kinetic: convenience kinetics Liebermeister and Klipp, 2006
    Compartment: lumenal side of the thylakoid membrane
    Units:
    Reaction rate: mmol/mol Chl/s
    [F], [Fdred] in mmol/mol Chl/s
    [NADPH] in mM
    """
    fdred = Fdred / KM_FNR_F
    fdox = Fd / KM_FNR_F
    nadph = (
        NADPH
    ) / KM_FNR_N  # NADPH requires conversion to mmol/mol of chlorophyll
    nadp = (
        NADP
    ) / KM_FNR_N  # NADP requires conversion to mmol/mol of chlorophyll
    return (
        EFNR
        * kcatFNR
        * ((fdred**2) * nadp - ((fdox**2) * nadph) / Keq_FNR)
        / (
            (1 + fdred + fdred**2) * (1 + nadp)
            + (1 + fdox + fdox**2) * (1 + nadph)
            - 1
        )
    )


def Leak(
    H: float,
    kLeak: float,
    pHstroma: float,
) -> float:
    """rate of leak of protons through the membrane"""
    return kLeak * (H - calculate_pHinv(pHstroma))


def St12(
    Ant: float,
    Pox: float,
    kStt7: float,
    PQtot: float,
    KM_ST: float,
    n_ST: float,
) -> float:
    """reaction rate of state transitions from PSII to PSI
    Ant depending on module used corresponds to non-phosphorylated antennae
    or antennae associated with PSII
    """
    kKin = kStt7 * (1 / (1 + ((Pox / PQtot) / KM_ST) ** n_ST))
    return kKin * Ant


def St21(LHCp: float, kPph1: float) -> float:
    """reaction rate of state transitions from PSI to PSII"""
    return kPph1 * LHCp


def ATPsynthase(
    ATP: float,
    ADP: float,
    pH: float,
    kATPsynth: float,
    DeltaG0_ATP: float,
    dG_pH: float,
    HPR: float,
    pHstroma: float,
    Pi_mol: float,
    RT: float,
) -> float:
    """Reaction rate of ATP production
    Kinetic: simple mass action with PH dependant equilibrium
    Compartment: lumenal side of the thylakoid membrane
    Units:
    Reaction rate: mmol/mol Chl/s
    [ATP], [ADP] in mM
    """
    return kATPsynth * (
        ADP - ATP / Keq_ATP(pH, DeltaG0_ATP, dG_pH, HPR, pHstroma, Pi_mol, RT)
    )


def _add_derived_parameters(m: Model) -> Model:
    m.add_derived_parameter(
        parameter_name="RT",
        function=proportional,
        parameters=["R", "T"],
    )

    m.add_derived_parameter(
        parameter_name="dG_pH",
        function=dG_pH,
        parameters=["R", "T"],
    )

    # m.add_derived_parameter(
    #     parameter_name=n.h(chl_stroma),
    #     function=Hstroma,
    #     parameters=["pHstroma"],
    # )

    # m.add_derived_parameter(
    #     parameter_name="kProtonation",
    #     function=kProtonation,
    #     parameters=[n.h(chl_stroma)],
    # )

    m.add_derived_parameter(
        parameter_name="Keq_PQred",
        function=keq_PQred,
        parameters=["E0_QA", "F", "E0_PQ", "pHstroma", "dG_pH", "RT"],
    )

    # m.add_derived_parameter(
    #     parameter_name="Keq_cyc",
    #     function=Keq_cyc,
    #     parameters=["E0_Fd", "F", "E0_PQ", "pHstroma", "dG_pH", "RT"],
    # )

    m.add_derived_parameter(
        parameter_name="Keq_FAFd",
        function=Keq_FAFd,
        parameters=["E0_FA", "F", "E0_Fd", "RT"],
    )

    m.add_derived_parameter(
        parameter_name="Keq_PCP700",
        function=Keq_PCP700,
        parameters=["E0_PC", "F", "E0_P700", "RT"],
    )

    m.add_derived_parameter(
        parameter_name="Keq_FNR",
        function=Keq_FNR,
        parameters=["E0_Fd", "F", "E0_NADP", "pHstroma", "dG_pH", "RT"],
    )
    return m


def _add_algebraic_modules(m: Model, chl_lumen: str) -> Model:
    m.add_algebraic_module_from_args(
        module_name="pq_alm",
        function=moiety_1,
        derived_compounds=["PQred"],
        args=[n.pq_ox(), "PQtot"],
    )

    m.add_algebraic_module_from_args(
        module_name="pc_alm",
        function=moiety_1,
        derived_compounds=["PCred"],
        args=[n.pc_ox(), "PCtot"],
    )

    m.add_algebraic_module_from_args(
        module_name="fd_alm",
        function=moiety_1,
        derived_compounds=["Fdred"],
        args=[n.fd_ox(), "Fdtot"],
    )

    m.add_algebraic_module_from_args(
        module_name="adp_alm",
        function=moiety_1,
        derived_compounds=[n.adp()],
        args=[n.atp(), "APtot"],
    )

    m.add_algebraic_module_from_args(
        module_name="nadp_alm",
        function=moiety_1,
        derived_compounds=[n.nadp()],
        args=[n.nadph(), "NADPtot"],
    )

    m.add_algebraic_module_from_args(
        module_name="lhc_alm",
        function=lhcmoiety,
        derived_compounds=[n.lhcp()],
        args=[n.lhc()],
    )

    m.add_algebraic_module_from_args(
        module_name="ps2crosssection",
        function=ps2crosssection,
        derived_compounds=[n.ps2cs()],
        args=[n.lhc(), "staticAntII", "staticAntI"],
    )

    m.add_algebraic_module_from_args(
        module_name="ps2states",
        function=ps2states,
        derived_compounds=[n.b0(), n.b1(), n.b2(), "B3"],
        args=[
            n.pq_ox(),
            "PQred",
            n.ps2cs(),
            "PSIItot",
            "k2",
            "kF",
            "kH",
            "kH0",
            "Keq_PQred",
            "kPQred",
            n.pfd(),
        ],
    )

    m.add_algebraic_module_from_args(
        module_name="ps1states",
        function=ps1states,
        derived_compounds=[n.a1()],
        args=[
            n.pc_ox(),
            "PCred",
            n.fd_ox(),
            "Fdred",
            n.ps2cs(),
            "PSItot",
            "kFdred",
            "Keq_FAFd",
            "Keq_PCP700",
            "kPCox",
            n.pfd(),
        ],
    )

    m.add_readout(
        name=n.fluorescence(),
        function=fluorescence,
        args=[n.b0(), n.b2(), n.ps2cs(), "k2", "kF", "kH", "kH0"],
    )

    m.add_algebraic_module_from_args(
        module_name="calculate_pH",
        function=calculate_pH,
        derived_compounds=["pH"],
        args=[n.h(chl_lumen)],
    )
    return m


def _add_reactions(m: Model, chl_lumen: str) -> Model:
    m.add_reaction_from_args(
        rate_name="PS2",
        function=PS2,
        stoichiometry={n.pq_ox(): -1},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(two_div_by, ["bH"])
        },
        args=[n.b1(), "k2"],
    )

    m.add_reaction_from_args(
        rate_name="PS1",
        function=PS1,
        stoichiometry={n.fd_ox(): -1, n.pc_ox(): 1},
        args=[n.a1(), n.ps2cs(), n.pfd()],
    )

    m.add_reaction_from_args(
        rate_name="PTOX",
        function=PTOX,
        stoichiometry={n.pq_ox(): 1},
        args=["PQred", "kPTOX", "O2ext"],
    )

    m.add_reaction_from_args(
        rate_name="NDH",
        function=NDH,
        stoichiometry={n.pq_ox(): -1},
        args=[n.pq_ox(), "kNDH"],
    )

    m.add_reaction_from_args(
        rate_name="B6f",
        function=B6f,
        stoichiometry={n.pc_ox(): -2, n.pq_ox(): 1},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(four_div_by, ["bH"])
        },
        args=[
            n.pc_ox(),
            n.pq_ox(),
            "PQred",
            "PCred",
            "pH",
            "kCytb6f",
            "F",
            "E0_PQ",
            "E0_PC",
            "pHstroma",
            "RT",
            "dG_pH",
        ],
    )

    m.add_reaction_from_args(
        rate_name="Cyc",
        function=Cyc,
        stoichiometry={n.pq_ox(): -1, n.fd_ox(): 2},
        args=[n.pq_ox(), "Fdred", "kcyc"],
    )

    m.add_reaction_from_args(
        rate_name="FNR",
        function=FNR,
        stoichiometry={n.fd_ox(): 2, n.nadph(): 1},
        args=[
            n.fd_ox(),
            "Fdred",
            n.nadph(),
            n.nadp(),
            "KM_FNR_F",
            "KM_FNR_N",
            "EFNR",
            "kcatFNR",
            "Keq_FNR",
        ],
    )

    m.add_reaction_from_args(
        rate_name="Leak",
        function=Leak,
        stoichiometry={},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(neg_one_div_by, ["bH"])
        },
        args=[n.h(chl_lumen), "kLeak", "pHstroma"],
    )

    m.add_reaction_from_args(
        rate_name="St12",
        function=St12,
        stoichiometry={n.lhc(): -1},
        args=[n.lhc(), n.pq_ox(), "kStt7", "PQtot", "KM_ST", "n_ST"],
    )

    m.add_reaction_from_args(
        rate_name="St21",
        function=St21,
        stoichiometry={n.lhc(): 1},
        args=[n.lhcp(), "kPph1"],
    )

    m.add_reaction_from_args(
        rate_name="ATPsynthase",
        function=ATPsynthase,
        stoichiometry={n.atp(): 1},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(neg_div, ["HPR", "bH"])
        },
        args=[
            n.atp(),
            n.adp(),
            "pH",
            "kATPsynth",
            "DeltaG0_ATP",
            "dG_pH",
            "HPR",
            "pHstroma",
            "Pi_mol",
            "RT",
        ],
    )

    m.add_reaction_from_args(
        rate_name="ATPconsumption",
        function=proportional,
        stoichiometry={n.atp(): -1},
        args=[n.atp(), "kATPcons"],
    )

    m.add_reaction_from_args(
        rate_name="NADPHconsumption",
        function=proportional,
        stoichiometry={n.nadph(): -1},
        args=[n.nadph(), "kNADPHcons"],
    )
    return m


def get_model(chl_lumen: str = "_lumen") -> Model:
    m = Model()
    m.add_compounds(
        [
            n.pq_ox(),  # oxidised plastoquinone
            n.pc_ox(),  # oxidised plastocyan
            n.fd_ox(),  # oxidised ferrodoxin
            n.atp(),  # stromal concentration of ATP
            n.nadph(),  # stromal concentration of NADPH
            n.h(chl_lumen),  # lumenal protons
            n.lhc(),  # non-phosphorylated LHC
        ]
    )

    m.add_parameters(
        {
            "PSIItot": 2.5,  # [mmol/molChl] total concentration of PSII
            "PSItot": 2.5,
            "PQtot": 17.5,  # [mmol/molChl]
            "PCtot": 4.0,  # Bohme1987 but other sources give different values - seems to depend greatly on organism and conditions
            "Fdtot": 5.0,  # Bohme1987
            "NADPtot": 25.0,  # estimate from ~ 0.8 mM, Heineke1991
            "APtot": 60.0,  # [mmol/molChl] Bionumbers ~2.55mM (=81mmol/molChl) (FIXME: Soma had 50)
            # parameters associated with photosystem II
            "kH": 0.0,
            "kH0": 5e8,  # base quenching" after calculation with Giovanni
            "kF": 6.25e7,  # 6.25e7 fluorescence 16ns
            "k2": 5e9,
            # parameters associated with photosystem I
            "kStt7": 0.0035,  # [s-1] fitted to the FM dynamics
            "kPph1": 0.0013,  # [s-1] fitted to the FM dynamics
            "KM_ST": 0.2,  # Switch point (half-activity of Stt7) for 20% PQ oxidised (80% reduced)
            "n_ST": 2.0,  # Hill coefficient of 4 -> 1/(2.5^4)~1/40 activity at PQox=PQred
            "staticAntI": 0.2,  # corresponds to PSI - LHCI supercomplex, when chlorophyll decreases more relative fixed antennae
            "staticAntII": 0.0,  # corresponds to PSII core
            # ATP and NADPH parameters
            "kATPsynth": 20.0,  # taken from MATLAB
            "kATPcons": 10.0,  # taken from MATLAB
            "Pi_mol": 0.01,
            "DeltaG0_ATP": 30.6,  # 30.6kJ/mol / RT
            "HPR": 14.0 / 3.0,  # Vollmar et al. 2009 (after Zhu et al. 2013)
            "kNADPHcons": 15.0,  # taken from MATLAB
            # global conversion factor of PFD to excitation rate
            # pH and protons
            "pHstroma": 7.8,
            "kLeak": 0.010,  # [1/s] leakage rate -- inconsistency with Kathrine
            "bH": 100.0,  # proton buffer: ratio total / free protons
            # rate constants
            "kPQred": 250.0,  # [1/(s*(mmol/molChl))]
            "kCytb6f": 2.5,  # a rough estimate: transfer PQ->cytf should be ~10ms
            "kPTOX": 0.01,  # ~ 5 electrons / seconds. This gives a bit more (~20)
            "kPCox": 2500.0,  # a rough estimate: half life of PC->P700 should be ~0.2ms
            "kFdred": 2.5e5,  # a rough estimate: half life of PC->P700 should be ~2micro-s
            "kcatFNR": 500.0,  # Carrillo2003 (kcat~500 1/s)
            "kcyc": 1.0,
            "O2ext": 8.0,  # corresponds to 250 microM cor to 20%
            "kNDH": 0.002,  # re-introduce e- into PQ pool. Only positive for anaerobic (reducing) condition
            "EFNR": 3.0,  # Bohme1987
            "KM_FNR_F": 1.56,  # corresponds to 0.05 mM (Aliverti1990)
            "KM_FNR_N": 0.22,  # corresponds to 0.007 mM (Shin1971 Aliverti2004)
            # standard redox potentials (at pH=0) in V
            "E0_QA": -0.140,
            "E0_PQ": 0.354,
            "E0_PC": 0.380,
            "E0_P700": 0.480,
            "E0_FA": -0.550,
            "E0_Fd": -0.430,
            "E0_NADP": -0.113,
            # physical constants
            "F": 96.485,  # Faraday constant
            "R": 8.3e-3,  # universal gas constant
            "T": 298.0,  # Temperature in K - for now assumed to be constant at 25 C
            # light
            n.pfd(): 100.0,
        }
    )

    m = _add_derived_parameters(m)
    m = _add_algebraic_modules(m, chl_lumen=chl_lumen)
    return _add_reactions(m, chl_lumen=chl_lumen)



def get_y0(chl_lumen: str = "_lumen") -> dict[str, float]:
    return {
        n.pq_ox(): 7.575784203321588,
        n.pc_ox(): 1.5029247837209212,
        n.fd_ox(): 4.436134828827484,
        n.atp(): 7.135498751769004,
        n.nadph(): 3.575529857805976,
        n.h(chl_lumen): 0.0015925898860846223,
        n.lhc(): 0.6786229141322606,
    }
