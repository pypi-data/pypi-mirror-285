"""http://doi.org/10.1016/j.biosystems.2010.10.011"""

from __future__ import annotations

import numpy as np
from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n
from qtbmodels.v1.shared import neg, proportional, twice, value

__all__ = ["get_model"]


def times_minus_fourteen_thirds(x: float) -> float:
    return -x * 14 / 3


def pH(H: float) -> float:
    return -np.log10(H * 2.5e-4)  # type: ignore


def Keq(
    H: float,
    DG0: float,
    Hst: float,
    RT: float,
    Pi: float,
) -> float:
    DG = DG0 - np.log(10) * (pH(Hst) - pH(H)) * (14 / 3) * RT
    return Pi * np.exp(-DG / RT)  # type: ignore


def v1(
    N: float,
    A1: float,
    PFD: float,
    cPFD: float,
) -> float:
    return (1 - N) * PFD * cPFD * A1


def v2(
    A2: float,
    k2: float,
) -> float:
    return k2 * A2


def v3(
    A1: float,
    A2: float,
    P: float,
    D: float,
    X: float,
    k3p: float,
    k3m: float,
) -> float:  # P seems to be reduce and Q oxidized ?
    A3 = D - A1 - A2
    Q = X - P
    return k3p * A3 * Q - k3m * A1 * P


def v5(
    T: float,
    H: float,
    A: float,
    k5: float,
    DG0: float,
    Hst: float,
    RT: float,
    Pi: float,
) -> float:
    return k5 * (A - T * (1 + 1 / Keq(H, DG0, Hst, RT, Pi)))


def v6(
    N: float,
    H: float,
    k6: float,
    n: float,
    KQ: float,
) -> float:
    return k6 * (1 - N) * ((H**n) / (H**n + KQ**n))  # type: ignore


def v8(
    H: float,
    Hst: float,
    k8: float,
) -> float:
    return k8 * (H - Hst)


def _add_derived_parameters(m: Model) -> Model:
    m.add_derived_parameter(
        parameter_name="RT",
        function=proportional,
        parameters=["R", "Temp"],
    )
    return m


def _add_reactions(m: Model, chl_lumen: str) -> Model:
    m.add_reaction_from_args(
        rate_name="v1",
        function=v1,
        stoichiometry={n.a1(): -1, n.a2(): 1},
        args=[n.quencher(), n.a1(), n.pfd(), "cPFD"],
    )

    m.add_reaction_from_args(
        rate_name="v2",
        function=v2,
        stoichiometry={n.a2(): -1},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                twice,
                args=["bH"],
            ),
        },
        args=[n.a2(), "k2"],
    )

    m.add_reaction_from_args(
        rate_name="v3",
        function=v3,
        stoichiometry={n.a1(): 1, n.pq_ox(): 1},
        args=[n.a1(), n.a2(), n.pq_ox(), "D", "X", "k3p", "k3m"],
    )

    m.add_reaction_from_args(
        rate_name="v4",
        function=proportional,
        stoichiometry={n.pq_ox(): -1},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                value,
                args=["bH"],
            ),
        },
        args=[n.pq_ox(), "k4"],
    )

    m.add_reaction_from_args(
        rate_name="v5",
        function=v5,
        stoichiometry={n.atp(): 1},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                times_minus_fourteen_thirds,
                args=["bH"],
            ),
        },
        args=[n.atp(), n.h(chl_lumen), "A", "k5", "DG0", "Hst", "RT", n.pi()],
    )

    m.add_reaction_from_args(
        rate_name="v6",
        function=v6,
        stoichiometry={n.quencher(): 1},
        args=[n.quencher(), n.h(chl_lumen), "k6", "n", "KQ"],
    )

    m.add_reaction_from_args(
        rate_name="v7",
        function=proportional,
        stoichiometry={n.quencher(): -1},
        args=[n.quencher(), "k7"],
    )

    m.add_reaction_from_args(
        rate_name="v8",
        function=v8,
        stoichiometry={},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                neg,
                args=["bH"],
            ),
        },
        args=[n.h(chl_lumen), "Hst", "k8"],
    )

    m.add_reaction_from_args(
        rate_name="v9",
        function=proportional,
        stoichiometry={n.atp(): -1},
        args=[n.atp(), "k9"],
    )
    return m


def get_model(chl_lumen: str = "_lumen") -> Model:
    m = Model()
    m.add_compounds(
        [
            n.a1(),
            n.a2(),
            n.pq_ox(),
            n.h(chl_lumen),
            n.quencher(),
            n.atp(),
        ]
    )
    m.add_parameters(
        {
            "k2": 3.4e6,
            "k3p": 1.56e5,
            "k3m": 3.12e4,
            "k4": 50,
            "k5": 80,
            "k6": 0.05,
            "k7": 0.004,
            "k8": 10,
            "k9": 20,
            "D": 2.5,
            "X": 17.5,
            "A": 32,
            "KQ": 0.004,
            "n": 5,
            "bH": 0.01,
            "cPFD": 4 / 3,
            "DG0": 30.6,
            n.pi(): 0.01,  # mM in M and conversion to mmol/(mol*Chl^-1)
            "Hst": 6.34e-5,  # Why should this correspond to an pH of 7.8 (units mmol(mol*Chl^-1))?
            "R": 0.0083,
            "Temp": 298,
            n.pfd(): 10,
        }
    )
    m = _add_derived_parameters(m)
    return _add_reactions(m, chl_lumen=chl_lumen)


def get_y0(chl_lumen: str = "_lumen") -> dict[str, float]:
    return {
        n.a1(): 2.4809993028001993,
        n.a2(): 9.48076726500766e-06,
        n.pq_ox(): 0.644692174020521,
        n.h(chl_lumen): 0.0011657529833317927,
        n.quencher(): 0.025555690463791844,
        n.atp(): 1.0359943132847658,
    }
