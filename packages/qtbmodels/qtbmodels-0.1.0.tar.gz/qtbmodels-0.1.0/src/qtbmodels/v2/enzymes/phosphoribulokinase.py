"""phosphoribulokinase

EC 2.7.1.19

Equilibrator
    ATP(aq) + D-Ribulose 5-phosphate(aq) ⇌ ADP(aq) + D-Ribulose 1,5-bisphosphate(aq)
    Keq = 1e5 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.phosphoribulokinase()


def _rate_prk(
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


def add_phosphoribulokinase(
    model: Model,
    *,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    model.add_parameter("kms_prk_ru5p", 0.05)
    model.add_parameter("kms_prk_atp", 0.05)
    model.add_parameter("ki_prk_1", 2.0)
    model.add_parameter("ki_prk_2", 0.7)
    model.add_parameter("ki_prk_3", 4.0)
    model.add_parameter("ki_prk_4", 2.5)
    model.add_parameter("ki_prk_5", 0.4)
    kcat = 0.9999 * 8

    vmax = build_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=kcat,
        enzyme_factor=enzyme_factor,
        e0=e0,
    ).vmax

    stoichiometry = filter_stoichiometry(
        model,
        {
            n.ru5p(chl_stroma): -1.0,
            n.atp(chl_stroma): -1.0,
            n.rubp(chl_stroma): 1.0,
            n.adp(chl_stroma): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_prk,
        stoichiometry=stoichiometry,
        args=[
            n.ru5p(chl_stroma),
            n.atp(chl_stroma),
            n.pi(chl_stroma),
            n.pga(chl_stroma),
            n.rubp(chl_stroma),
            n.adp(chl_stroma),
            vmax,
            "kms_prk_ru5p",
            "kms_prk_atp",
            "ki_prk_1",
            "ki_prk_2",
            "ki_prk_3",
            "ki_prk_4",
            "ki_prk_5",
        ],
    )
    return model
