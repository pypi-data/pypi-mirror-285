"""Model builds on top of Matuszynska 2016

Changes
    - Coupled with Poolman 2000 model
    - Requires changing units of ATP/ADP, NADPH/NADP
    - Requires speeding up CBB via PFD

https://doi.org/10.1111/ppl.12962
"""
from __future__ import annotations

from modelbase.ode import DerivedStoichiometry, Model

from qtbmodels import names as n
from qtbmodels.v1.matuszynska2016npq import get_model as get_matuszynska
from qtbmodels.v1.poolman2000 import get_model as get_poolman2000
from qtbmodels.v1.shared import (
    michaelis_menten_1s,
    moiety_1,
    neg_div,
    proportional,
    value,
)
from qtbmodels.v1.utils import rename_parameter


def normalize_concentration(concentration: float, total: float) -> float:
    return concentration / total


###############################################################################
# Rates
###############################################################################


def atp_synthase(
    ATP: float,
    ADP: float,
    Keq_ATPsynthase: float,
    kATPsynth: float,
    convf: float,
) -> float:
    return kATPsynth * (ADP / convf - ATP / convf / Keq_ATPsynthase)


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


###############################################################################
# Changes
###############################################################################


def _remove_static_atp_production(model: Model) -> Model:
    model.remove_reaction("atp_synthase")
    model.remove_algebraic_module("ADP_moiety")
    model.remove_compound(n.atp())
    model.remove_derived_parameter("Vmax_atp_synthase")
    model.remove_parameters(
        ["E0_atp_synthase", "kcat_atp_synthase", "kms_16_1", "kms_16_2"]
    )
    return model


def _remove_static_nadph(model: Model) -> Model:
    model.remove_parameters([n.nadph(), n.nadp()])
    return model


def _update_dynamic_nadph(model: Model) -> Model:
    # FIXME: this one is kinda silly, but needs to be done with the
    # current way of doing things for the rubisco parameters annotation
    # to work
    model.update_reaction_from_args(
        "rubisco_co2",
        args=model.rates["rubisco_co2"].args,  # FIXME: stupid
    )

    # This one is an actual change
    model.update_reaction_from_args(
        rate_name="gadph",
        stoichiometry={
            n.bpga(): -1,
            n.nadph(): -1,
            n.gap(): 1,
        },
        args=model.rates["gadph"].args,  # FIXME: Here again ...
    )
    return model


def _make_nadph_dynamic(model: Model) -> Model:
    model.remove_derived_parameter(n.nadp())
    model.remove_parameter(n.nadph())

    model.add_compound(n.nadph())
    model.add_algebraic_module_from_args(
        module_name=n.nadp(),
        function=moiety_1,
        derived_compounds=[n.nadp()],
        args=[n.nadph(), "NADP_total"],
    )
    # FNR is expanded in _convert_units
    return model


def _convert_units(model: Model, chl_lumen: str) -> Model:
    """Convert units mM to mmol / mol Chl

    Important for ATP and NADPH
    """
    model.add_parameter("convf", 3.2e-2)

    model.update_reaction_from_args(
        rate_name="FNR",
        function=fnr,
        derived_stoichiometry={
            n.nadph(): DerivedStoichiometry(function=value, args=["convf"])
        },
        args=[*model.rates["FNR"].args, "convf"],
    )
    model.update_reaction_from_args(
        rate_name="atp_synthase",
        function=atp_synthase,
        stoichiometry={},
        derived_stoichiometry={
            n.h(chl_lumen): DerivedStoichiometry(
                function=neg_div, args=["HPR", "bH"]
            ),
            n.atp(): DerivedStoichiometry(function=value, args=["convf"]),
        },
        args=[*model.rates["atp_synthase"].args, "convf"],
    )
    return model


def _speed_up_cbb(m: Model) -> Model:
    m.add_parameters(
        {
            "Km_fcbb": 150.0,
            "Vmax_fcbb": 6.0,
        }
    )

    m.add_derived_parameter(
        "fCBB", michaelis_menten_1s, [n.pfd(), "Vmax_fcbb", "Km_fcbb"]
    )
    rename_parameter(m, "E0_rubisco", "E0_rubisco_base")
    m.add_derived_parameter(
        "E0_rubisco", proportional, ["E0_rubisco_base", "fCBB"]
    )

    rename_parameter(m, "E0_fbpase", "E0_fbpase_base")
    m.add_derived_parameter(
        "E0_fbpase", proportional, ["E0_fbpase_base", "fCBB"]
    )

    rename_parameter(m, "E0_sbpase", "E0_sbpase_base")
    m.add_derived_parameter(
        "E0_sbpase", proportional, ["E0_sbpase_base", "fCBB"]
    )

    rename_parameter(m, "E0_prk", "E0_prk_base")
    m.add_derived_parameter("E0_prk", proportional, ["E0_prk_base", "fCBB"])

    rename_parameter(m, "E0_ex_starch", "E0_ex_starch_base")
    m.add_derived_parameter(
        "E0_ex_starch", proportional, ["E0_ex_starch_base", "fCBB"]
    )

    return m


def _remove_atp_consumption(model: Model) -> Model:
    model.remove_reaction("ex_atp")
    model.remove_parameter("kATPconsumption")
    return model


def _add_convenience_readouts(model: Model) -> Model:
    model.add_algebraic_module_from_args(
        module_name="pq_redoxstate",
        function=normalize_concentration,
        derived_compounds=["PQ_ox/tot"],
        args=[n.pq_red(), "PQ_total"],
    )
    model.add_algebraic_module_from_args(
        module_name="fd_redoxstate",
        function=normalize_concentration,
        derived_compounds=["Fd_ox/tot"],
        args=[n.fd_red(), "Fd_total"],
    )
    model.add_algebraic_module_from_args(
        module_name="pc_redoxstate",
        function=normalize_concentration,
        derived_compounds=["PC_ox/tot"],
        args=[n.pc_red(), "PC_total"],
    )
    model.add_algebraic_module_from_args(
        module_name="nadp_redoxstate",
        function=normalize_concentration,
        derived_compounds=["NADPH/tot"],
        args=[n.nadph(), "NADP_total"],
    )
    model.add_algebraic_module_from_args(
        module_name="energystate",
        function=normalize_concentration,
        derived_compounds=["ATP/tot"],
        args=[n.atp(), "AP_total"],
    )
    return model


def get_model(chl_lumen: str = "_lumen", static_co2: bool = True) -> Model:
    poolman = get_poolman2000(static_co2=static_co2)
    poolman.update_parameter("Phosphate_total", 17.05)
    _remove_static_atp_production(poolman)
    _remove_static_nadph(poolman)

    matuszynska = get_matuszynska(chl_lumen=chl_lumen)
    _make_nadph_dynamic(matuszynska)
    _convert_units(matuszynska, chl_lumen=chl_lumen)
    _remove_atp_consumption(matuszynska)

    model = poolman + matuszynska
    _update_dynamic_nadph(model)
    _speed_up_cbb(model)

    _add_convenience_readouts(model)

    return model


def get_y0(chl_lumen: str = "_lumen") -> dict[str, float]:
    return {
        n.pga(): 0.9928653922138561,
        n.bpga(): 0.0005297732935310749,
        n.gap(): 0.0062663539939955834,
        n.dhap(): 0.13785977143668732,
        n.fbp(): 0.006133532145409954,
        n.f6p(): 0.31271973359685457,
        n.g6p(): 0.719255387166192,
        n.g1p(): 0.041716812452951633,
        n.sbp(): 0.013123745088361893,
        n.s7p(): 0.15890073845176905,
        n.e4p(): 0.007322797350442026,
        n.x5p(): 0.022478763225333428,
        n.r5p(): 0.037651927659696716,
        n.rubp(): 0.13184790283048484,
        n.ru5p(): 0.015060770937455408,
        n.atp(): 1.612922506604933,
        n.fd_ox(): 3.8624032084329674,
        n.h(chl_lumen): 0.002208423037307405,
        n.lhc(): 0.80137477470646,
        n.nadph(): 0.491395685599137,
        n.pc_ox(): 1.885391998090184,
        n.pq_ox(): 10.991562708096392,
        n.psbs_de(): 0.9610220887579118,
        n.vx(): 0.9514408605906095,
    }
