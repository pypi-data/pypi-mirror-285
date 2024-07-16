"""name

EC FIXME

Equilibrator
"""

from __future__ import annotations

import numpy as np
from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n
from qtbmodels.shared import mass_action_1s, mass_action_2s, value

from ._utils import filter_stoichiometry


def _two_div_by(x: float) -> float:
    return 2.0 / x


def _keq_pcp700(
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


def _keq_faf_d(
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


def _rate_ps1(
    A: float,
    ps2cs: float,
    pfd: float,
) -> float:
    return (1 - ps2cs) * pfd * A


def _rate_ps2(
    B1: float,
    k2: float,
) -> float:
    return 0.5 * k2 * B1


def _ps1states_2019(
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
    """
    L = (1 - ps2cs) * pfd
    return PSItot / (
        1
        + L / (kFdred * Fd)
        + (1 + Fdred / (Keq_FAFd * Fd))
        * (PC / (Keq_PCP700 * PCred) + L / (kPCox * PCred))
    )


def _ps1states_2021(
    PC: float,
    PCred: float,
    Fd: float,
    Fdred: float,
    ps2cs: float,
    PSItot: float,
    kFdred: float,
    KeqF: float,
    KeqC: float,
    kPCox: float,
    pfd: float,
    k0: float,
    O2: float,
) -> tuple[float, float, float]:
    """QSSA calculates open state of PSI
    depends on reduction states of plastocyanin and ferredoxin
    C = [PC], F = [Fd] (ox. forms)
    """
    kLI = (1 - ps2cs) * pfd

    y0 = (
        KeqC
        * KeqF
        * PCred
        * PSItot
        * kPCox
        * (Fd * kFdred + O2 * k0)
        / (
            Fd * KeqC * KeqF * PCred * kFdred * kPCox
            + Fd * KeqF * kFdred * (KeqC * kLI + PC * kPCox)
            + Fdred * kFdred * (KeqC * kLI + PC * kPCox)
            + KeqC * KeqF * O2 * PCred * k0 * kPCox
            + KeqC * KeqF * PCred * kLI * kPCox
            + KeqF * O2 * k0 * (KeqC * kLI + PC * kPCox)
        )
    )

    y1 = (
        PSItot
        * (
            Fdred * kFdred * (KeqC * kLI + PC * kPCox)
            + KeqC * KeqF * PCred * kLI * kPCox
        )
        / (
            Fd * KeqC * KeqF * PCred * kFdred * kPCox
            + Fd * KeqF * kFdred * (KeqC * kLI + PC * kPCox)
            + Fdred * kFdred * (KeqC * kLI + PC * kPCox)
            + KeqC * KeqF * O2 * PCred * k0 * kPCox
            + KeqC * KeqF * PCred * kLI * kPCox
            + KeqF * O2 * k0 * (KeqC * kLI + PC * kPCox)
        )
    )
    y2 = PSItot - y0 - y1

    return y0, y1, y2


def _ps2_crosssection(
    LHC: float,
    staticAntII: float,
    staticAntI: float,
) -> float:
    return staticAntII + (1 - staticAntII - staticAntI) * LHC


def _ps2states(
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

    for L_, kH_, k3p_, k3m_ in zip(L, kH, k3p, k3m):  # type: ignore
        M = np.array(
            [
                [-L_ - k3m_, kH_ + kF, k3p_, 0],
                [L_, -(kH_ + kF + k2), 0, 0],
                [0, 0, L_, -(kH_ + kF)],
                [1, 1, 1, 1],
            ]
        )
        A = np.array([0, 0, 0, PSIItot])
        B0, B1, B2, B3 = np.linalg.solve(M, A)
        Bs.append([B0, B1, B2, B3])
    return np.array(Bs).T  # type: ignore


def add_ps2_cross_section(model: Model) -> Model:
    model.add_parameter("staticAntI", 0.37)
    model.add_parameter("staticAntII", 0.1)
    model.add_derived_compound(
        name=n.ps2cs(),
        function=_ps2_crosssection,
        args=[
            n.lhc(),
            "staticAntII",
            "staticAntI",
        ],
    )
    return model


def add_photosystems(model: Model, *, chl_lumen: str, mehler: bool) -> Model:
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

    model.add_derived_parameter(
        n.keq("PCP700"),
        _keq_pcp700,
        ["E^0_PC", "F", "E^0_P700", "RT"],
    )
    model.add_derived_parameter(
        n.keq(n.ferredoxin_reductase()),
        _keq_faf_d,
        ["E^0_FA", "F", "E^0_Fd", "RT"],
    )

    model.add_algebraic_module_from_args(
        module_name="ps2states",
        function=_ps2states,
        derived_compounds=[
            n.b0(),
            n.b1(),
            n.b2(),
            n.b3(),
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
            n.keq(n.pq_red()),
            "kPQred",
            n.pfd(),
            "kH0",
        ],
    )

    enzyme_name = n.ps2()
    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=_rate_ps2,
        stoichiometry={
            n.pq_ox(): -1,
        },
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                function=_two_div_by, args=["bH"]
            ),
        },
        args=[
            n.b1(),
            "k2",
        ],
    )

    enzyme_name = n.ps1()
    if not mehler:
        model.add_derived_compound(
            name=n.a1(),
            function=_ps1states_2019,
            args=[
                n.pc_ox(),
                n.pc_red(),
                n.fd_ox(),
                n.fd_red(),
                n.ps2cs(),
                "PSI_total",
                "kFdred",
                n.keq(n.ferredoxin_reductase()),
                n.keq("PCP700"),
                "kPCox",
                n.pfd(),
            ],
        )
        model.add_reaction_from_args(
            rate_name=enzyme_name,
            function=_rate_ps1,
            stoichiometry={
                n.fd_ox(): -1,
                n.pc_ox(): 1,
            },
            args=[
                n.a1(),
                n.ps2cs(),
                n.pfd(),
            ],
        )
    else:
        model.add_parameter("kMehler", 1.0)
        model.add_algebraic_module_from_args(
            module_name="ps1states",
            function=_ps1states_2021,
            derived_compounds=[n.a0(), n.a1(), n.a2()],
            args=[
                n.pc_ox(),
                n.pc_red(),
                n.fd_ox(),
                n.fd_red(),
                n.ps2cs(),
                "PSI_total",
                "kFdred",
                n.keq(n.ferredoxin_reductase()),
                n.keq("PCP700"),
                "kPCox",
                n.pfd(),
                "kMehler",
                n.o2(chl_lumen),
            ],
        )
        model.add_reaction_from_args(
            rate_name=enzyme_name,
            function=_rate_ps1,
            stoichiometry={
                n.pc_ox(): 1,
            },
            args=[n.a0(), n.ps2cs(), n.pfd()],
        )
        model.add_reaction_from_args(
            rate_name=n.mehler(),
            function=mass_action_2s,
            stoichiometry={},
            derived_stoichiometry={
                n.h2o2(): DerivedStoichiometry(value, ["convf"])
            },
            args=[
                n.a1(),
                n.o2(chl_lumen),
                "kMehler",
            ],
        )
    return model


def add_energy_production(model: Model) -> Model:
    model.add_parameter(k := n.k(n.pfd()), 1 / 145)  # Fitted
    model.add_parameter(n.pfd(), 700)

    model.add_reaction_from_args(
        n.petc(),
        mass_action_1s,
        filter_stoichiometry(
            model,
            {
                # Substrates
                # Products
                n.energy(): 1,
            },
        ),
        [n.pfd(), k],
    )
    return model
