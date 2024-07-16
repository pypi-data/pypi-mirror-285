"""name

Equilibrator
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n

from ._utils import build_vmax, filter_stoichiometry

if TYPE_CHECKING:
    from modelbase.ode import Model

ENZYME = n.ex_g1p()


def _rate_starch(
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


def add_g1p_efflux(
    model: Model,
    *,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    model.add_parameter(kms1 := n.km(ENZYME, "1"), 0.08)
    model.add_parameter(kms2 := n.km(ENZYME, "2"), 0.08)
    model.add_parameter(ki := n.ki(ENZYME), 10.0)
    model.add_parameter(ka1 := n.ka(ENZYME, "1"), 0.1)
    model.add_parameter(ka2 := n.ka(ENZYME, "2"), 0.02)
    model.add_parameter(ka3 := n.ka(ENZYME, "3"), 0.02)
    kcat = 0.04 * 8

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
            n.g1p(chl_stroma): -1.0,
            n.atp(chl_stroma): -1.0,
            n.adp(chl_stroma): 1.0,
        },
        optional={
            n.starch(chl_stroma): 1.0,
        },
    )

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=_rate_starch,
        stoichiometry=stoichiometry,
        args=[
            n.g1p(chl_stroma),
            n.atp(chl_stroma),
            n.adp(chl_stroma),
            n.pi(chl_stroma),
            n.pga(chl_stroma),
            n.f6p(chl_stroma),
            n.fbp(chl_stroma),
            vmax,
            kms1,
            kms2,
            ki,
            ka1,
            ka2,
            ka3,
        ],
    )
    return model
