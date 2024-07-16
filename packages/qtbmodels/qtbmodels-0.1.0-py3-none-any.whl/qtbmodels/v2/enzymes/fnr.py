r"""Ferredoxin-NADP reductase

2 reduced ferredoxin + NADP+ + H+ ⇌ \rightleftharpoons 2 oxidized ferredoxin + NADPH

EC 1.18.1.2

Equilibrator
"""

from typing import Literal

import numpy as np
from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n
from qtbmodels.shared import michaelis_menten_1s, michaelis_menten_2s, value

from ._utils import add_parameter_if_missing, filter_stoichiometry, static_vmax

ENZYME = n.fnr()


def _keq_fnr(
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


def _rate_fnr2016(
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


def _rate_fnr_2019(
    Fd_ox: float,
    Fd_red: float,
    NADPH: float,
    NADP: float,
    KM_FNR_F: float,
    KM_FNR_N: float,
    EFNR: float,
    kcatFNR: float,
    Keq_FNR: float,
    convf: float,
) -> float:
    fdred = Fd_red / KM_FNR_F
    fdox = Fd_ox / KM_FNR_F
    nadph = NADPH / convf / KM_FNR_N
    nadp = NADP / convf / KM_FNR_N
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


def add_fnr(
    model: Model,
    *,
    chl_stroma: str,
    stroma_unit: Literal["mM", "mmol/mol Chl"],
) -> Model:
    model.add_parameter("KM_FNR_F", 1.56)
    model.add_parameter("KM_FNR_N", 0.22)
    model.add_parameter("EFNR", 3.0)
    model.add_parameter("kcatFNR", 500.0)
    model.add_derived_parameter(
        n.keq(ENZYME),
        _keq_fnr,
        [
            "E^0_Fd",
            "F",
            "E^0_NADP",
            n.ph(chl_stroma),
            "dG_pH",
            "RT",
        ],
    )

    args = [
        n.fd_ox(),
        n.fd_red(),
        n.nadph(),
        n.nadp(),
        "KM_FNR_F",
        "KM_FNR_N",
        "EFNR",
        "kcatFNR",
        n.keq(ENZYME),
    ]
    if stroma_unit == "mmol/mol Chl":
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=_rate_fnr2016,
            stoichiometry={
                n.fd_ox(): 2,
            },
            args=args,
        )
    else:
        add_parameter_if_missing(model, "convf", 3.2e-2)
        model.add_reaction_from_args(
            rate_name=ENZYME,
            function=_rate_fnr_2019,
            stoichiometry={
                n.fd_ox(): 2,
            },
            derived_stoichiometry={
                n.nadph(): DerivedStoichiometry(function=value, args=["convf"])
            },
            args=[*args, "convf"],
        )
    return model


def add_fnr_static(model: Model, *, e0: float = 1.0) -> Model:
    """Saadat version to put into Poolman model"""
    vmax = static_vmax(model, enzyme_name=ENZYME, kcat=2.816, e0=e0).vmax
    model.add_parameter(km := n.km(ENZYME), 0.19)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_1s,
        stoichiometry={
            # n.nadp(): -1.0,
            n.nadph(): 1.0,
        },
        args=[
            n.nadp(),
            vmax,
            km,
        ],
    )

    return model


def add_fnr_energy_dependent(
    model: Model, *, compartment: str, e0: float = 1.0
) -> Model:
    vmax = static_vmax(
        model,
        enzyme_name=ENZYME,
        kcat=2.816,
        e0=e0,
    ).vmax
    model.add_parameter(km := n.km(ENZYME), 0.19)

    model.add_reaction_from_args(
        rate_name=ENZYME,
        function=michaelis_menten_2s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                # Substrates
                n.nadp(compartment): -1.0,
                n.energy(compartment): -1.0,
                # Products
                n.nadph(compartment): 1.0,
            },
        ),
        args=[
            n.nadp(),
            n.energy(),
            vmax,
            km,
        ],
    )

    return model
