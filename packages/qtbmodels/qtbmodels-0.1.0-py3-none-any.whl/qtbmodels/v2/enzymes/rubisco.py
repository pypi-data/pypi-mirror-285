"""Ribulose-1,5-bisphosphate carboxylase/oxygenase

Enzyme catalysing both carboxylation as well as oxygenation of ribulose-1,5-bisphosphate
leading to either 2xPGA or 1xPGA and 1xPGO


Equilibrator (carboxylation)
    D-Ribulose 1,5-bisphosphate(aq) + CO2(total) ⇌ 2 3-Phospho-D-glycerate(aq)
    Keq = 1.6e4 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)

Equilibrator (oxygenation)
    Oxygen(aq) + D-Ribulose 1,5-bisphosphate(aq) ⇌ 3-Phospho-D-glycerate(aq) + 2-Phosphoglycolate(aq)
    Keq = 2.9e91 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)


Following inhibition mechanisms are known
    - PGA (Poolman 2000)
    - FBP (Poolman 2000)
    - SBP (Poolman 2000)
    - Orthophosphate (Poolman 2000)
    - NADPH (Poolman 2000)
    - PGO (FIXME)


Because of it's complex dynamics, multiple kinetic descriptions of rubisco are possible,
some of which have been implemented here.
    - Poolman 2000, doi: FIXME
    - Witzel 2010, doi: FIXME

Kinetic parameters
------------------
kcat (CO2)
    - 3 s^1 (Stitt 2010)

Witzel:
    gamma = 1 / km_co2
    omega = 1 / km_o2
    lr = k_er_minus / k_er_plus
    lc = k_er_minus / (omega * kcat_carb)
    lrc = k_er_minus / (gamma * k_er_plus)
    lro = k_er_minus / (omega * k_er_plus)
    lo = k_er_minus / (omega * k_oxy)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from qtbmodels import names as n
from qtbmodels.shared import div, mul, one_div

from ._utils import (
    EnzymeNames,
    dynamic_vmax_multiple,
    filter_stoichiometry,
    static_vmax_multiple,
)

if TYPE_CHECKING:
    from modelbase.ode import Model


def _rate_poolman_0i(
    rubp: float, co2: float, vmax: float, kms_rubp: float, kms_co2: float
) -> float:
    return vmax * rubp * co2 / ((rubp + kms_rubp) * (co2 + kms_co2))


def _rate_poolman_1i() -> float:
    raise NotImplementedError


def _rate_poolman_2i() -> float:
    raise NotImplementedError


def _rate_poolman_3i() -> float:
    raise NotImplementedError


def _rate_poolman_4i() -> float:
    raise NotImplementedError


def _rate_poolman_5i(
    rubp: float,
    pga: float,
    co2: float,
    vmax: float,
    kms_rubp: float,
    kms_co2: float,
    # inhibitors
    ki_pga: float,
    fbp: float,
    ki_fbp: float,
    sbp: float,
    ki_sbp: float,
    pi: float,
    ki_p: float,
    nadph: float,
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


def _rate_witzel_1i() -> float:
    raise NotImplementedError


def _rate_witzel_2i() -> float:
    raise NotImplementedError


def _rate_witzel_3i() -> float:
    raise NotImplementedError


def _rate_witzel_4i() -> float:
    raise NotImplementedError


def _rate_witzel_5i(
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
    i1: float,  # pga
    ki1: float,
    i2: float,  # fbp
    ki2: float,
    i3: float,  # sbp
    ki3: float,
    i4: float,  # pi
    ki4: float,
    i5: float,  # nadph
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


def _add_rubisco_poolman(
    model: Model,
    chl_stroma: str,
    enzyme: dict[str, EnzymeNames],
    stoichiometry_carb: dict[str, float],
    ki1: str,
    ki2: str,
    ki3: str,
    ki4: str,
    ki5: str,
) -> None:
    model.add_parameter("kms_rubisco_co2", 0.0107)
    model.add_parameter("kms_rubisco_rubp", 0.02)
    args = [
        n.rubp(chl_stroma),
        n.pga(chl_stroma),
        n.co2(chl_stroma),
        enzyme[n.rubisco_carboxylase()].vmax,
        "kms_rubisco_rubp",
        "kms_rubisco_co2",
        # pga again?
        ki1,
        n.fbp(chl_stroma),
        ki2,
        n.sbp(chl_stroma),
        ki3,
        n.pi(chl_stroma),
        ki4,
        n.nadph(chl_stroma),
        ki5,
    ]

    model.add_reaction_from_args(
        rate_name=n.rubisco_carboxylase(),
        function=_rate_poolman_5i,
        stoichiometry=stoichiometry_carb,
        args=args,
    )


def _add_rubisco_witzel(
    model: Model,
    chl_stroma: str,
    enzyme: dict[str, EnzymeNames],
    stoichiometry_carb: dict[str, float],
    stoichiometry_oxy: dict[str, float],
    ki1: str,
    ki2: str,
    ki3: str,
    ki4: str,
    ki5: str,
) -> None:
    model.add_parameters(
        {
            "k_er_plus": 0.15 * 1000,  # 1 / (mM * s)
            "k_er_minus": 0.0048,  # 1 / s
            "km_co2": 10.7 / 1000,  # mM
            "km_o2": 295 / 1000,  # mM
        }
    )
    model.add_derived_parameter("gamma", one_div, ["km_co2"])
    model.add_derived_parameter("omega", one_div, ["km_o2"])
    model.add_derived_parameter(
        "omega_kcat_carb", mul, ["omega", n.kcat(n.rubisco_carboxylase())]
    )
    model.add_derived_parameter(
        "omega_koxy", mul, ["omega", n.kcat(n.rubisco_oxygenase())]
    )
    model.add_derived_parameter("omega_ker_plus", mul, ["omega", "k_er_plus"])
    model.add_derived_parameter("gamma_ker_plus", mul, ["gamma", "k_er_plus"])
    model.add_derived_parameter("lr", div, ["k_er_minus", "k_er_plus"])
    model.add_derived_parameter("lc", div, ["k_er_minus", "omega_kcat_carb"])
    model.add_derived_parameter("lrc", div, ["k_er_minus", "gamma_ker_plus"])
    model.add_derived_parameter("lro", div, ["k_er_minus", "omega_ker_plus"])
    model.add_derived_parameter("lo", div, ["k_er_minus", "omega_koxy"])
    model.add_reaction_from_args(
        rate_name=n.rubisco_carboxylase(),
        function=_rate_witzel_5i,
        stoichiometry=stoichiometry_carb,
        args=[
            n.rubp(),
            n.co2(chl_stroma),
            enzyme[n.rubisco_carboxylase()].vmax,
            "gamma",  # 1 / km_co2
            n.co2(chl_stroma),
            n.o2(chl_stroma),
            "lr",
            "lc",
            "lo",
            "lrc",
            "lro",
            n.pga(),
            ki1,
            n.fbp(),
            ki2,
            n.sbp(),
            ki3,
            n.pi(),
            ki4,
            n.nadph(),
            ki5,
        ],
    )
    model.add_reaction_from_args(
        rate_name=n.rubisco_oxygenase(),
        function=_rate_witzel_5i,
        stoichiometry=stoichiometry_oxy,
        args=[
            n.rubp(chl_stroma),
            n.o2(chl_stroma),
            enzyme[n.rubisco_oxygenase()].vmax,
            "omega",  # 1 / km_o2
            n.co2(chl_stroma),
            n.o2(chl_stroma),
            "lr",
            "lc",
            "lo",
            "lrc",
            "lro",
            n.pga(),
            ki1,
            n.fbp(),
            ki2,
            n.sbp(),
            ki3,
            n.pi(),
            ki4,
            n.nadph(),
            ki5,
        ],
    )


def add_rubisco(
    model: Model,
    *,
    variant: Literal["poolman", "witzel"],
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float | None = None,
) -> Model:
    enzyme_name = n.rubisco()

    model.add_parameter(ki1 := "ki_1_1", 0.04)
    model.add_parameter(ki2 := "ki_1_2", 0.04)
    model.add_parameter(ki3 := "ki_1_3", 0.075)
    model.add_parameter(ki4 := "ki_1_4", 0.9)
    model.add_parameter(ki5 := "ki_1_5", 0.07)

    if variant == "poolman":
        reaction_names = [n.rubisco_carboxylase()]
        e0 = 1.0 if e0 is None else e0
        kcats = [0.34 * 8]
    else:
        reaction_names = [n.rubisco_carboxylase(), n.rubisco_oxygenase()]
        e0 = 0.16 if e0 is None else e0
        kcats = [3.1, 1.125]

    if enzyme_factor is None:
        enzyme = static_vmax_multiple(
            model,
            enzyme_name=enzyme_name,
            reaction_names=reaction_names,
            kcats=kcats,
            e0=e0,
        )
    else:
        enzyme = dynamic_vmax_multiple(
            model,
            enzyme_name=enzyme_name,
            reaction_names=reaction_names,
            kcats=kcats,
            e_factor=enzyme_factor,
            e0=e0,
        )

    stoichiometry_carb = filter_stoichiometry(
        model,
        {
            n.rubp(chl_stroma): -1.0,
            n.pga(chl_stroma): 2.0,
            n.co2(chl_stroma): -1,
        },
    )

    stoichiometry_oxy = {
        n.rubp(): -1.0,
        n.pga(): 1.0,
        n.pgo(): 1.0,
    }

    if variant == "poolman":
        _add_rubisco_poolman(
            model,
            chl_stroma,
            enzyme,
            stoichiometry_carb,
            ki1,
            ki2,
            ki3,
            ki4,
            ki5,
        )
    else:
        _add_rubisco_witzel(
            model,
            chl_stroma,
            enzyme,
            stoichiometry_carb,
            stoichiometry_oxy,
            ki1,
            ki2,
            ki3,
            ki4,
            ki5,
        )

    return model
