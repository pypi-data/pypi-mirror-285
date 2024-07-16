"""Matuszyńska 2016 PhD
doi: 10.1016/j.bbabio.2016.09.003

re-implementation of model from Matuszyńska et al 2016 PhD

"""

from __future__ import annotations

import numpy as np
from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n
from qtbmodels.v1.shared import proportional, value


def two_div_by(x: float) -> float:
    return 2.0 / x


def pH(H: float) -> float:
    value = H * 2.5e-4
    return -np.log10(value)  # type: ignore


def pHinv(pH: float) -> float:
    return 4e3 * 10**-pH


# Auxiliary functions
def ps2states(
    P: float,
    Q: float,
    light: float,
    PQtot: float,
    kPQred: float,
    KeqQAPQ: float,
    kH: float,
    kF: float,
    kP: float,
    PSIItot: float,
) -> float:
    """Calculates the states of photosystem II
    accepts:
    P: reduced fraction of PQ pool (PQH2)
    Q: Quencher
    returns:
    B: array of PSII states
    """
    Bs = []
    Pox = PQtot - P
    b0 = light + kPQred * P / KeqQAPQ
    b1 = kH * Q + kF
    b2 = kH * Q + kF + kP

    for Pox, b0, b1, b2 in zip(Pox, b0, b1, b2):  # type: ignore
        A = np.array(
            [
                [-b0, b1, kPQred * Pox, 0],  # B0
                [light, -b2, 0, 0],  # B1
                [0, 0, light, -b1],  # B3
                [1, 1, 1, 1],
            ]
        )

        b = np.array([0, 0, 0, PSIItot])
        B0, B1, B2, B3 = np.linalg.solve(A, b)
        Bs.append([B0, B1, B2, B3])
    return np.array(Bs).T  # type: ignore


def Keqcytb6f(
    H: float,
    F: float,
    E0PQPQH2: float,
    RT: float,
    E0PCPCm: float,
    pHstroma: float,
) -> float:
    """Equilibriu constant of Cytochrome b6f"""
    DG1 = -2 * F * E0PQPQH2 + 2 * RT * np.log(10) * pH(H)
    DG2 = -F * E0PCPCm
    DG3 = RT * np.log(10) * (pHstroma - pH(H))
    DG = -DG1 + 2 * DG2 + 2 * DG3
    return np.exp(-DG / RT)


def KeqATPsyn(
    H: float, DG0ATP: float, pHstroma: float, RT: float, Pi: float
) -> float:
    """Equilibrium constant of ATP synthase. For more
    information see Matuszynska et al 2016 or Ebenhöh et al. 2011,2014
    """
    DG = DG0ATP - np.log(10) * (pHstroma - pH(H)) * (14 / 3) * RT
    return Pi * np.exp(-DG / RT)


# Conserved quantities
def pqmoiety(P: float, PQtot: float) -> float:
    return PQtot - P


def atpmoiety(A: float, APtot: float) -> float:
    return APtot - A


def psbsmoiety(Pr: float, PsbStot: float) -> float:
    return PsbStot - Pr


def xcycmoiety(V: float, Xtot: float) -> float:
    return Xtot - V


# rate equations


# FIXME: what's with all those parameters??
def Fluorescence(
    P: float,
    Q: float,
    B0: float,
    B2: float,
    light: float,
    PQtot: float,
    kPQred: float,
    KeqQAPQ: float,
    kH: float,
    kF: float,
    kP: float,
    PSIItot: float,
) -> float:
    """Fluorescence function"""
    return kF / (kH * Q + kF + kP) * B0 + kF / (kH * Q + kF) * B2


def Quencher(
    Pr: float,
    V: float,
    Xtot: float,
    PsbStot: float,
    Kzsat: float,
    gamma0: float,
    gamma1: float,
    gamma2: float,
    gamma3: float,
) -> float:
    """Quencher mechanism
    accepts:
    Pr: fraction of non-protonated PsbS protein
    V: fraction of Violaxanthin
    """
    Z = Xtot - V
    P = PsbStot - Pr
    Zs = Z / (Z + Kzsat)

    return (
        gamma0 * (1 - Zs) * Pr
        + gamma1 * (1 - Zs) * P
        + gamma2 * Zs * P
        + gamma3 * Zs * Pr
    )


# FIXME: what's with all those parameters??
def ps2(
    B1: float,
    light: float,
    PQtot: float,
    kPQred: float,
    KeqQAPQ: float,
    kH: float,
    kF: float,
    kP: float,
    PSIItot: float,
) -> float:
    """Reduction of PQ due to ps2"""
    return kP * 0.5 * B1


def PQox(
    P: float,
    H: float,
    light: float,
    kCytb6f: float,
    kPTOX: float,
    O2ex: float,
    PQtot: float,
    F: float,
    E0PQPQH2: float,
    RT: float,
    E0PCPCm: float,
    pHstroma: float,
) -> float:
    """Oxidation of the PQ pool through cytochrome and PTOX"""
    kPFD = kCytb6f * light
    kPTOX = kPTOX * O2ex
    Keq = Keqcytb6f(H, F, E0PQPQH2, RT, E0PCPCm, pHstroma)
    a1 = kPFD * Keq / (Keq + 1)
    a2 = kPFD / (Keq + 1)
    return (a1 + kPTOX) * P - a2 * (PQtot - P)


def ATPsynthase(
    A: float,
    H: float,
    E: float,
    kATPsynthase: float,
    DG0ATP: float,
    pHstroma: float,
    RT: float,
    Pi: float,
    APtot: float,
) -> float:
    """Production of ATP by ATPsynthase"""
    return (
        E
        * kATPsynthase
        * (APtot - A - A / KeqATPsyn(H, DG0ATP, pHstroma, RT, Pi))
    )


def ATPactivity(
    E: float, light: float, kActATPase: float, kDeactATPase: float
) -> float:
    """Activation of ATPsynthase by light"""
    switch = light > 0
    return kActATPase * switch * (1 - E) - kDeactATPase * (1 - switch) * E


def Leak(H: float, kleak: float, pHstroma: float) -> float:
    """Transmembrane proton leak"""
    return kleak * (H - pHinv(pHstroma))


def ATPcons(A: float, kATPconsumption: float) -> float:
    """ATP consuming reaction"""
    return kATPconsumption * A


def Xcyc(
    V: float,
    H: float,
    nHX: float,
    KphSatZ: float,
    kDeepoxV: float,
    kEpoxZ: float,
    Xtot: float,
) -> float:
    """Xanthophyll cycle"""
    a = H**nHX / (H**nHX + pHinv(KphSatZ) ** nHX)
    return kDeepoxV * a * V - kEpoxZ * (Xtot - V)


def PsbSP(
    Pr: float,
    H: float,
    nHL: float,
    KphSatLHC: float,
    kProt: float,
    kDeprot: float,
    PsbStot: float,
) -> float:
    """Protonation of PsbS protein"""
    a = H**nHL / (H**nHL + pHinv(KphSatLHC) ** nHL)
    return kProt * a * Pr - kDeprot * (PsbStot - Pr)


def _KeqQAPQ(
    F: float, E0QAQAm: float, E0PQPQH2: float, pHstroma: float, RT: float
) -> float:
    DG1 = -F * E0QAQAm
    DG2 = -2 * F * E0PQPQH2 + 2 * pHstroma * np.log(10) * RT
    DG0 = -2 * DG1 + DG2
    return np.exp(-DG0 / RT)


def get_model(chl_lumen: str = "_lumen") -> Model:
    pars = {
        # Pool sizes
        "PSIItot": 2.5,  # [mmol/molChl] total concentration of PSII
        "PQtot": 20,  # [mmol/molChl]
        "APtot": 50,  # [mmol/molChl] Bionumbers ~2.55mM (=81mmol/molChl)
        "PsbStot": 1,  # [relative] LHCs that get phosphorylated and protonated
        "Xtot": 1,  # [relative] xanthophylls
        "O2ex": 8,  # external oxygen, kept constant, corresponds to 250 microM, corr. to 20%
        n.pi(): 0.01,
        # Rate constants and key parameters
        "kCytb6f": 0.104,  # a rough estimate of the transfer from PQ to cyt that is equal to ~ 10ms
        # [1/s*(mmol/(s*m^2))] - gets multiplied by light to determine rate
        "kActATPase": 0.01,  # paramter relating the rate constant of activation of the ATPase in the light
        "kDeactATPase": 0.002,  # paramter relating the deactivation of the ATPase at night
        "kATPsynthase": 20.0,
        "kATPconsumption": 10.0,
        "kPQred": 250.0,  # [1/(s*(mmol/molChl))]
        "kH": 5e9,  # Heatdisipation (rates)
        "kF": 6.25e8,  # fluorescence 16ns
        "kP": 5e9,  # original 5e9 (charge separation limiting step ~ 200ps) - made this faster for higher Fs fluorescence (express in unites of time
        "kPTOX": 0.01,  # ~ 5 electrons / seconds. This gives a bit more (~20)
        "pHstroma": 7.8,  # [1/s] leakage rate
        "kleak": 1000,
        "bH": 100,  # proton buffer: ratio total / free protons
        # Parameter associated with xanthophyll cycle
        "kDeepoxV": 0.0024,  # Aktivierung des Quenchings
        "kEpoxZ": 0.00024,  # 6.e-4,  #converted to [1/s]   # Deaktivierung
        "KphSatZ": 5.8,  # [-] half-saturation pH value for activity de-epoxidase, highest activity at ~pH 5.8
        "nHX": 5.0,  # [-] hill-coefficient for activity of de-epoxidase
        "Kzsat": 0.12,  # [-], half-saturation constant (relative conc. of Z) for quenching of Z
        # Parameter associated with PsbS protonation
        "nHL": 3,
        "kDeprot": 0.0096,
        "kProt": 0.0096,
        "KphSatLHC": 5.8,
        # Fitted quencher contribution factors
        "gamma0": 0.1,  # slow quenching of Vx present despite lack of protonation
        "gamma1": 0.25,  # fast quenching present due to the protonation
        "gamma2": 0.6,  # slow quenching of Zx present despite lack of protonation
        "gamma3": 0.15,  # fastest possible quenching
        # Physical constants
        "F": 96.485,  # Faraday constant
        "R": 8.3e-3,  # universal gas constant
        "T": 298,  # Temperature in K - for now assumed to be constant at 25 C
        # Standard potentials and DG0ATP
        "E0QAQAm": -0.140,
        "E0PQPQH2": 0.354,
        "E0PCPCm": 0.380,
        "DG0ATP": 30.6,  # 30.6kJ/mol / RT
        # PFD
        n.pfd(): 100,
    }

    # define the basic model
    model = Model(pars)

    # add compounds
    model.add_compounds(
        [
            n.pq_ox(),  # reduced Plastoquinone
            n.h(chl_lumen),  # luminal Protons
            "E",  # ATPactivity
            "A",  # ATP
            "Pr",  # fraction of non-protonated PsbS (notation from doctoral thesis Matuszynska 2016)
            "V",  # fraction of Violaxanthin
        ]
    )

    # add derived parameters
    model.add_derived_parameter(
        parameter_name="RT",
        function=proportional,
        parameters=["R", "T"],
    )

    model.add_derived_parameter(
        parameter_name="KeqQAPQ",
        function=_KeqQAPQ,
        parameters=["F", "E0QAQAm", "E0PQPQH2", "pHstroma", "RT"],
    )

    # add algebraic module
    model.add_algebraic_module_from_args(
        module_name="P_am",
        function=pqmoiety,
        derived_compounds=["Pox"],
        args=[n.pq_ox(), "PQtot"],
    )

    model.add_algebraic_module_from_args(
        module_name="A_am",
        function=atpmoiety,
        derived_compounds=[n.adp()],
        args=["A", "APtot"],
    )

    model.add_algebraic_module_from_args(
        module_name="PsbS_am",
        function=psbsmoiety,
        derived_compounds=["Pnr"],
        args=["Pr", "PsbStot"],
    )

    model.add_algebraic_module_from_args(
        module_name="X_am",
        function=xcycmoiety,
        derived_compounds=["Z"],
        args=["V", "Xtot"],
    )

    model.add_algebraic_module_from_args(
        module_name=n.quencher(),
        function=Quencher,
        derived_compounds=[n.quencher()],
        args=[
            "Pr",
            "V",
            "Xtot",
            "PsbStot",
            "Kzsat",
            "gamma0",
            "gamma1",
            "gamma2",
            "gamma3",
        ],
    )

    model.add_algebraic_module_from_args(
        module_name="PSIIstates",
        function=ps2states,
        derived_compounds=[n.b0(), n.b1(), n.b2(), "B3"],
        args=[
            n.pq_ox(),
            n.quencher(),
            n.pfd(),
            "PQtot",
            "kPQred",
            "KeqQAPQ",
            "kH",
            "kF",
            "kP",
            "PSIItot",
        ],
    )

    model.add_readout(
        name=n.fluorescence(),
        function=Fluorescence,
        args=[
            n.pq_ox(),
            n.quencher(),
            n.b0(),
            n.b2(),
            n.pfd(),
            "PQtot",
            "kPQred",
            "KeqQAPQ",
            "kH",
            "kF",
            "kP",
            "PSIItot",
        ],
    )

    # Mock module to get Light vector over all simulated time points
    model.add_algebraic_module_from_args(
        module_name="L",
        function=value,
        derived_compounds=["L"],
        args=[n.pfd()],
    )

    # Add rates to model
    model.add_reaction_from_args(
        rate_name="ps2",
        function=ps2,
        stoichiometry={n.pq_ox(): 1},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(two_div_by, ["bH"])
        },
        args=[
            n.b1(),
            n.pfd(),
            "PQtot",
            "kPQred",
            "KeqQAPQ",
            "kH",
            "kF",
            "kP",
            "PSIItot",
        ],
    )

    model.add_reaction_from_args(
        rate_name="PQox",
        function=PQox,
        stoichiometry={n.pq_ox(): -1, n.h(chl_lumen): 4 / pars["bH"]},
        args=[
            n.pq_ox(),
            n.h(chl_lumen),
            n.pfd(),
            "kCytb6f",
            "kPTOX",
            "O2ex",
            "PQtot",
            "F",
            "E0PQPQH2",
            "RT",
            "E0PCPCm",
            "pHstroma",
        ],
    )

    model.add_reaction_from_args(
        rate_name="ATPsynthase",
        function=ATPsynthase,
        stoichiometry={"A": 1, n.h(chl_lumen): (-14 / 3) / pars["bH"]},
        args=[
            "A",
            n.h(chl_lumen),
            "E",
            "kATPsynthase",
            "DG0ATP",
            "pHstroma",
            "RT",
            n.pi(),
            "APtot",
        ],
    )

    model.add_reaction_from_args(
        rate_name="ATPactivity",
        function=ATPactivity,
        stoichiometry={"E": 1},
        args=["E", n.pfd(), "kActATPase", "kDeactATPase"],
    )

    model.add_reaction_from_args(
        rate_name="Leak",
        function=Leak,
        stoichiometry={n.h(chl_lumen): -1 / pars["bH"]},
        args=[n.h(chl_lumen), "kleak", "pHstroma"],
    )

    model.add_reaction_from_args(
        rate_name="ATPcons",
        function=ATPcons,
        stoichiometry={"A": -1},
        args=["A", "kATPconsumption"],
    )

    model.add_reaction_from_args(
        rate_name="Xcyc",
        function=Xcyc,
        stoichiometry={"V": -1},
        args=[
            "V",
            n.h(chl_lumen),
            "nHX",
            "KphSatZ",
            "kDeepoxV",
            "kEpoxZ",
            "Xtot",
        ],
    )

    model.add_reaction_from_args(
        rate_name=n.psbs_pr(),
        function=PsbSP,
        stoichiometry={"Pr": -1},
        args=[
            "Pr",
            n.h(chl_lumen),
            "nHL",
            "KphSatLHC",
            "kProt",
            "kDeprot",
            "PsbStot",
        ],
    )
    return model


def get_y0() -> dict[str, float]:
    return {}
