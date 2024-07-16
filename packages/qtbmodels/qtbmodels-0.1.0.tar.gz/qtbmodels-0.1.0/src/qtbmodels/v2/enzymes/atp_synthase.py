"""H+-transporting two-sector ATPase

ADP + Orthophosphate -> ATP

EC 3.6.3.14

Equilibrator
ADP(aq) + Orthophosphate(aq) ⇌ ATP(aq) + H2O(l)
Keq = 6.4e-6 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import Literal, cast

import numpy as np
from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n
from qtbmodels.shared import neg_div, value

from ._utils import add_parameter_if_missing, build_vmax, filter_stoichiometry

ENZYME = n.atp_synthase()


def _keq_atp(
    pH: float,
    DeltaG0_ATP: float,
    dG_pH: float,
    HPR: float,
    pHstroma: float,
    Pi_mol: float,
    RT: float,
) -> float:
    delta_g = DeltaG0_ATP - dG_pH * HPR * (pHstroma - pH)
    return cast(float, Pi_mol * np.exp(-delta_g / RT))


def _rate_atp_synthase_2000(
    adp: float,
    pi: float,
    v16: float,
    km161: float,
    km162: float,
) -> float:
    return v16 * adp * pi / ((adp + km161) * (pi + km162))


def _rate_atp_synthase_2016(
    ATP: float,
    ADP: float,
    Keq_ATPsynthase: float,
    kATPsynth: float,
) -> float:
    return kATPsynth * (ADP - ATP / Keq_ATPsynthase)


def _rate_atp_synthase_2019(
    ATP: float,
    ADP: float,
    Keq_ATPsynthase: float,
    kATPsynth: float,
    convf: float,
) -> float:
    return kATPsynth * (ADP / convf - ATP / convf / Keq_ATPsynthase)


def add_atp_synthase(
    model: Model,
    *,
    chl_stroma: str,
    chl_lumen: str = "_lumen",
    stroma_unit: Literal["mM", "mmol/mol Chl"],
) -> Model:
    add_parameter_if_missing(model, "HPR", 14.0 / 3.0)
    add_parameter_if_missing(model, "bH", 100.0)
    model.add_parameter("kATPsynth", 20.0)
    model.add_parameter("Pi_mol", 0.01)
    model.add_parameter("DeltaG0_ATP", 30.6)

    model.add_derived_compound(
        name=n.keq(ENZYME),
        function=_keq_atp,
        args=[
            n.ph(chl_lumen),
            "DeltaG0_ATP",
            "dG_pH",
            "HPR",
            n.ph(chl_stroma),
            "Pi_mol",
            "RT",
        ],
    )

    if stroma_unit == "mmol/mol Chl":
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=_rate_atp_synthase_2016,
            stoichiometry={n.atp(chl_stroma): 1.0},
            derived_stoichiometry={
                n.h(chl_lumen): DerivedStoichiometry(
                    function=neg_div, args=["HPR", "bH"]
                ),
            },
            args=[
                n.atp(chl_stroma),
                n.adp(chl_stroma),
                n.keq(ENZYME),
                "kATPsynth",
            ],
        )

    else:
        add_parameter_if_missing(model, "convf", 3.2e-2)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=_rate_atp_synthase_2019,
            stoichiometry={},
            derived_stoichiometry={
                n.h(chl_lumen): DerivedStoichiometry(
                    function=neg_div, args=["HPR", "bH"]
                ),
                n.atp(chl_stroma): DerivedStoichiometry(
                    function=value, args=["convf"]
                ),
            },
            args=[
                n.atp(chl_stroma),
                n.adp(chl_stroma),
                n.keq(ENZYME),
                "kATPsynth",
                "convf",
            ],
        )

    return model


def add_atp_synthase_static_protons(
    model: Model,
    *,
    chl_stroma: str,
    e0: float = 1.0,
    enzyme_factor: str | None = None,
) -> Model:
    """Used by Poolman 2000"""
    stoichiometry: dict[str, float] = filter_stoichiometry(
        model,
        {
            n.adp(chl_stroma): -1.0,
            n.atp(chl_stroma): 1.0,
        },
    )

    enzyme = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=2.8,
        e0=e0,
        enzyme_factor=enzyme_factor,
    )
    model.add_parameter(km1 := n.km(ENZYME, n.adp()), 0.014)
    model.add_parameter(km2 := n.km(ENZYME, n.pi()), 0.3)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_atp_synthase_2000,
        stoichiometry=stoichiometry,
        args=[
            n.adp(chl_stroma),
            n.pi(chl_stroma),
            enzyme.vmax,
            km1,
            km2,
        ],
    )
    return model


def _rate_static_energy(
    adp: float,
    pi: float,
    energy: float,
    v16: float,
    km161: float,
    km162: float,
) -> float:
    return adp * pi * energy * v16 / ((adp + km161) * (pi + km162))


def add_atp_synthase_energy_dependent(
    model: Model,
    *,
    chl_stroma: str,
    e0: float = 1.0,
    enzyme_factor: str | None = None,
) -> Model:
    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=2.8,
        e0=e0,
        enzyme_factor=enzyme_factor,
    ).vmax
    model.add_parameter(km1 := n.km(ENZYME, n.adp()), 0.014)
    model.add_parameter(km2 := n.km(ENZYME, n.pi()), 0.3)
    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_static_energy,
        stoichiometry=filter_stoichiometry(
            model,
            {
                # Substrates
                n.adp(chl_stroma): -1.0,
                n.energy(chl_stroma): -1.0,
                # Products
                n.atp(chl_stroma): 1.0,
            },
        ),
        args=[
            n.adp(chl_stroma),
            n.pi(chl_stroma),
            n.energy(chl_stroma),
            vmax,
            km1,
            km2,
        ],
    )
    return model


def ATP_gamma(
    Pi: float,
    ATP: float,
    ADP: float,
    convf: float,
) -> float:
    return (ATP / convf) / ((ADP / convf) * (Pi / 1000))


def deltagATPsyn(
    pH: float,
    gammaATP: float,
    DeltaG0_ATP: float,
    dG_pH: float,
    HPR: float,
    pHstroma: float,
    RT: float,
) -> float:
    return cast(
        float,
        DeltaG0_ATP - dG_pH * HPR * (pHstroma - pH) + RT * np.log(gammaATP),
    )


def vATPsynthase2(
    DeltaGATPsyn: float,
    ATPturnover: float,
) -> float:
    return -DeltaGATPsyn * ATPturnover


def add_atp_synthase_2024(
    model: Model,
    *,
    chl_lumen: str,
    chl_stroma: str,
) -> Model:
    add_parameter_if_missing(model, "convf", 3.2e-2)
    add_parameter_if_missing(model, "HPR", 14.0 / 3.0)
    add_parameter_if_missing(model, "bH", 100.0)

    model.add_parameter("DeltaG0_ATP", 30.6)
    model.add_parameter(atp_turnover := "ATPturnover", 90)

    model.add_derived_compound(
        name="ATP_gamma",
        function=ATP_gamma,
        args=[n.pi(), n.atp(), n.adp(), "convf"],
    )

    model.add_derived_compound(
        name="DeltaGATPsyn",
        function=deltagATPsyn,
        args=[
            n.ph(chl_lumen),
            "ATP_gamma",
            "DeltaG0_ATP",
            "dG_pH",
            "HPR",
            n.ph(chl_stroma),
            "RT",
        ],
    )

    model.add_reaction_from_args(
        rate_name="vATPsynthase",
        function=vATPsynthase2,
        stoichiometry={},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                function=neg_div, args=["HPR", "bH"]
            ),
            n.atp(chl_stroma): DerivedStoichiometry(
                function=value, args=["convf"]
            ),
        },
        args=[
            "DeltaGATPsyn",
            atp_turnover,
        ],
    )
    return model
