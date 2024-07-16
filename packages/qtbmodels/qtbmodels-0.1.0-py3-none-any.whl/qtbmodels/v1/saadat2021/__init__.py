from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n
from qtbmodels.v1.matuszynska2019 import get_model as get_matuszynska2019
from qtbmodels.v1.shared import (
    mass_action_1s,
    mass_action_2s,
    moiety_1,
    proportional,
)

if TYPE_CHECKING:
    from modelbase.ode import Model


def PS1(
    A: float,
    ps2cs: float,
    pfd: float,
) -> float:
    """reaction rate constant for open PSI"""
    return (1 - ps2cs) * pfd * A


def ps1analytic_mehler(
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


def Fd_red(
    Fd: float,
    Fdred: float,
    A1: float,
    A2: float,
    kFdred: float,
    Keq_FAFd: float,
) -> float:
    """rate of the redcution of Fd by the activity of PSI
    used to be equall to the rate of PSI but now
    alternative electron pathway from Fd allows for the production of ROS
    hence this rate has to be separate
    """
    return kFdred * Fd * A1 - kFdred / Keq_FAFd * Fdred * A2


def Ascorbate(
    A: float,
    H: float,
    kf1: float,
    kr1: float,
    kf2: float,
    kr2: float,
    kf3: float,
    kf4: float,
    kr4: float,
    kf5: float,
    XT: float,
) -> float:
    """lumped reaction of ascorbate peroxidase
    the cycle stretched to a linear chain with
    two steps producing the MDA
    two steps releasing ASC
    and one step producing hydrogen peroxide
    """
    nom = A * H * XT
    denom = (
        A * H * (1 / kf3 + 1 / kf5)
        + A / kf1
        + H / kf4
        + H * kr4 / (kf4 * kf5)
        + H / kf2
        + H * kr2 / (kf2 * kf3)
        + kr1 / (kf1 * kf2)
        + kr1 * kr2 / (kf1 * kf2 * kf3)
    )
    return nom / denom


def MDAreduct(
    NADPH: float,
    MDA: float,
    kcatMDAR: float,
    KmMDAR_NADPH: float,
    KmMDAR_MDA: float,
    MDAR0: float,
) -> float:
    """Compare Valero et al. 2016"""
    nom = kcatMDAR * MDAR0 * NADPH * MDA
    denom = (
        KmMDAR_NADPH * MDA
        + KmMDAR_MDA * NADPH
        + NADPH * MDA
        + KmMDAR_NADPH * KmMDAR_MDA
    )
    return nom / denom


def Mehler(
    A: float,
    O2ext: float,
    kMehler: float,
) -> float:
    """Draft Mehler reaction inspired from PSI reaction.
    This reaction is lumping the reduction of O2 instead of Fd
    resulting in Superoxide, as well as the Formation of H2O2 in one reaction.
    The entire reaction is scaled by the arbitrary parameter kMehler
    """
    return A * kMehler * O2ext


def GR(
    NADPH: float,
    GSSG: float,
    kcat_GR: float,
    GR0: float,
    KmNADPH: float,
    KmGSSG: float,
) -> float:
    nom = kcat_GR * GR0 * NADPH * GSSG
    denom = KmNADPH * GSSG + KmGSSG * NADPH + NADPH * GSSG + KmNADPH * KmGSSG
    return nom / denom


def DHAR(
    DHA: float,
    GSH: float,
    kcat_DHAR: float,
    DHAR0: float,
    KmDHA: float,
    K: float,
    KmGSH: float,
) -> float:
    nom = kcat_DHAR * DHAR0 * DHA * GSH
    denom = K + KmDHA * GSH + KmGSH * DHA + DHA * GSH
    return nom / denom


def v3ASC(
    MDA: float,
    k3: float,
) -> float:
    return k3 * MDA**2


def ascorbate_moiety(
    MDA: float,
    DHA: float,
    ASCtotal: float,
) -> float:
    return ASCtotal - MDA - DHA


def glutathion_moiety(
    GSSG: float,
    GStotal: float,
) -> float:
    return GStotal - 2 * GSSG


def _add_consumption(model: Model) -> Model:
    model.add_parameters(
        {
            "k_ex_atp": 0.2,
            "k_ex_nadph": 0.2,
        }
    )
    model.add_reaction_from_args(
        rate_name="EX_ATP",
        function=mass_action_1s,
        stoichiometry={n.atp(): -1},
        args=[n.atp(), "k_ex_atp"],
    )
    model.add_reaction_from_args(
        rate_name="EX_NADPH",
        function=mass_action_1s,
        stoichiometry={n.nadph(): -1},
        args=[n.nadph(), "k_ex_nadph"],
    )
    return model


def _add_thioredoxin_regulation(
    model: Model, rate_name: str, enzyme_name: str | None = None
) -> Model:
    if enzyme_name is None:
        enzyme_name = rate_name

    kcat_name = f"kcat_{rate_name}"
    vmax_name = f"Vmax_{rate_name}"

    e0_name = f"E0_{enzyme_name}"
    e0_base_name = f"E0_{enzyme_name}_base"

    if vmax_name in model.parameters:
        model.remove_derived_parameter(vmax_name)
    if e0_name in model.derived_parameters:
        # _base already exists, so we can just remove this
        model.remove_derived_parameter(e0_name)
    if e0_name in model._parameters:
        model.add_parameter(e0_base_name, model.parameters[e0_name])
        model.remove_parameter(e0_name)

    # Dynamic E0
    model.add_algebraic_module_from_args(
        module_name=rate_name,
        function=proportional,
        derived_compounds=[e0_name],
        args=[n.e_active(), e0_base_name],
    )

    # Dynamic Vmax
    model.add_algebraic_module_from_args(
        module_name=f"Vmax_{rate_name}",
        function=proportional,
        derived_compounds=[vmax_name],
        args=[e0_name, kcat_name],
    )

    # FIXME: stupid update :(
    model.update_reaction_from_args(
        rate_name=rate_name,
        args=model.rates[rate_name].args,
    )
    return model


def _replace_cbb_light_activation_with_thioredoxin(model: Model) -> Model:
    model.add_compounds([n.tr_ox(), n.e_inactive()])
    model.add_parameters(
        {
            "thioredoxin_tot": 1,
            "e_cbb_tot": 6,
            "k_fd_tr_reductase": 1,
            "k_e_cbb_activation": 1,
            "k_e_cbb_relaxation": 0.1,
        }
    )
    model.add_algebraic_module_from_args(
        module_name="thioredoxin_alm",
        function=moiety_1,
        derived_compounds=["TR_red"],
        args=[n.tr_ox(), "thioredoxin_tot"],
    )
    model.add_algebraic_module_from_args(
        module_name="e_cbb_alm",
        function=moiety_1,
        derived_compounds=[n.e_active()],
        args=[n.e_inactive(), "e_cbb_tot"],
    )

    model.add_reaction_from_args(
        rate_name="FdTrReductase",
        function=mass_action_2s,
        stoichiometry={n.tr_ox(): -1, n.fd_ox(): 1},
        args=[n.tr_ox(), n.fd_red(), "k_fd_tr_reductase"],
    )
    model.add_reaction_from_args(
        rate_name="E_activation",
        function=mass_action_2s,
        stoichiometry={n.e_inactive(): -5, n.tr_ox(): 5},
        args=[n.e_inactive(), "TR_red", "k_e_cbb_activation"],
    )
    model.add_reaction_from_args(
        rate_name="E_inactivation",
        function=mass_action_1s,
        stoichiometry={n.e_inactive(): 5},
        args=[n.e_active(), "k_e_cbb_relaxation"],
    )

    for rate_name in ["fbpase", "sbpase", "prk", "ex_starch"]:
        _add_thioredoxin_regulation(model, rate_name)
    _add_thioredoxin_regulation(model, "rubisco_co2", "rubisco")

    model.remove_derived_parameter("fCBB")
    model.remove_parameters(["Km_fcbb", "Vmax_fcbb"])
    return model


def _add_mehler(m: Model) -> Model:
    m.add_parameters(
        {
            "kf1": 10000.0,
            "kr1": 220.0,
            "kf2": 10000.0,
            "kr2": 4000.0,
            "kf3": 2510.0,
            "kf4": 10000.0,
            "kr4": 4000.0,
            "kf5": 2510.0,
            "XT": 0.07,  # according to Valero
            "kMehler": 1.0,
            "kcat_GR": 595,
            "kcat_DHAR": 142,
            "k3": 0.5 / 1e-3,
            "KmNADPH": 3e-3,
            "KmGSSG": 2e2 * 1e-3,
            "KmDHA": 70e-3,
            "KmGSH": 2.5e3 * 1e-3,
            "K": 5e5 * (1e-3) ** 2,  # ?
            "GR0": 1.4e-3,
            "DHAR0": 1.7e-3,
            "Glutathion_total": 10,
            "Ascorbate_total": 10,
            "kcatMDAR": 1080000 / (60 * 60),
            "KmMDAR_NADPH": 23e-3,
            "KmMDAR_MDA": 1.4e-3,
            "MDAR0": 2e-3,
        }
    )
    m.add_compounds(
        [
            n.mda(),
            n.h2o2(),
            n.dha(),
            n.glutathion_ox(),
        ]
    )

    m.add_algebraic_module_from_args(
        module_name="ascorbate_alm",
        function=ascorbate_moiety,
        derived_compounds=[n.ascorbate()],
        args=[n.mda(), n.dha(), "Ascorbate_total"],
    )

    m.add_algebraic_module_from_args(
        module_name="glutathion_alm",
        function=glutathion_moiety,
        derived_compounds=["GSH"],
        args=[n.glutathion_ox(), "Glutathion_total"],
    )

    m.update_algebraic_module_from_args(
        module_name="ps1states",
        function=ps1analytic_mehler,
        derived_compounds=["A0", n.a1(), n.a2()],
        args=[
            n.pc_ox(),
            n.pc_red(),
            n.fd_ox(),
            n.fd_red(),
            n.ps2cs(),
            "PSI_total",
            "kFdred",
            "Keq_FAFd",
            "Keq_PCP700",
            "kPCox",
            n.pfd(),
            "kMehler",
            "O2_lumen",
        ],
    )

    m.update_reaction(
        rate_name="PSI",
        function=PS1,
        stoichiometry={n.pc_ox(): 1},
        modifiers=["A0", n.ps2cs()],
        dynamic_variables=["A0", n.ps2cs()],
        parameters=[n.pfd()],
    )

    m.add_reaction_from_args(
        rate_name="Fdred",
        function=Fd_red,
        stoichiometry={n.fd_ox(): -1},
        args=[n.fd_ox(), n.fd_red(), n.a1(), n.a2(), "kFdred", "Keq_FAFd"],
    )

    m.add_reaction_from_args(
        rate_name="Ascorbate",
        function=Ascorbate,
        stoichiometry={n.h2o2(): -1, n.mda(): 2},
        args=[
            n.ascorbate(),
            n.h2o2(),
            "kf1",
            "kr1",
            "kf2",
            "kr2",
            "kf3",
            "kf4",
            "kr4",
            "kf5",
            "XT",
        ],
    )

    m.add_reaction_from_args(
        rate_name="MDAreduct",
        function=MDAreduct,
        stoichiometry={n.nadph(): -1, n.mda(): -2},
        args=[
            n.nadph(),
            n.mda(),
            "kcatMDAR",
            "KmMDAR_NADPH",
            "KmMDAR_MDA",
            "MDAR0",
        ],
    )

    m.add_reaction_from_args(
        rate_name="Mehler",
        function=Mehler,
        stoichiometry={
            n.h2o2(): 1 * m.get_parameter("convf")
        },  # required to convert as rates of PSI are expressed in mmol/mol Chl
        args=[n.a1(), "O2_lumen", "kMehler"],
    )

    m.add_reaction_from_args(
        rate_name="GR",
        function=GR,
        stoichiometry={n.nadph(): -1, n.glutathion_ox(): -1},
        args=[
            n.nadph(),
            n.glutathion_ox(),
            "kcat_GR",
            "GR0",
            "KmNADPH",
            "KmGSSG",
        ],
    )

    m.add_reaction_from_args(
        rate_name="DHAR",
        function=DHAR,
        stoichiometry={n.dha(): -1, n.glutathion_ox(): 1},
        args=[n.dha(), "GSH", "kcat_DHAR", "DHAR0", "KmDHA", "K", "KmGSH"],
    )

    m.add_reaction_from_args(
        rate_name="3ASC",
        function=v3ASC,
        stoichiometry={n.mda(): -2, n.dha(): 1},
        args=[n.mda(), "k3"],
    )
    return m


def get_model(chl_lumen: str = "_lumen", static_co2: bool = True) -> Model:
    m = get_matuszynska2019(static_co2=static_co2, chl_lumen=chl_lumen)
    m = _replace_cbb_light_activation_with_thioredoxin(m)
    m = _add_consumption(m)
    return _add_mehler(m)


def get_y0(chl_lumen: str = "_lumen") -> dict[str, float]:
    return {
        n.pga(): 0.9167729479368978,
        n.bpga(): 0.0003814495319659031,
        n.gap(): 0.00580821050261484,
        n.dhap(): 0.1277806166216142,
        n.fbp(): 0.005269452472931973,
        n.f6p(): 0.2874944558066638,
        n.g6p(): 0.6612372482712676,
        n.g1p(): 0.03835176039761378,
        n.sbp(): 0.011101373736607443,
        n.s7p(): 0.1494578301900007,
        n.e4p(): 0.00668295494870102,
        n.x5p(): 0.020988553174809618,
        n.r5p(): 0.035155825913785584,
        n.rubp(): 0.11293260727162346,
        n.ru5p(): 0.014062330254191594,
        n.atp(): 1.4612747767895344,
        n.fd_ox(): 3.715702384326767,
        n.h(chl_lumen): 0.002086128887296243,
        n.lhc(): 0.7805901436176024,
        n.nadph(): 0.5578718406315588,
        n.pc_ox(): 1.8083642974980014,
        n.pq_ox(): 10.251099271612473,
        n.psbs_de(): 0.9667381262477079,
        n.vx(): 0.9629870646993118,
        n.tr_ox(): 0.9334426859846461,
        n.e_inactive(): 3.6023635680406634,
        n.mda(): 2.0353396709300447e-07,
        n.h2o2(): 1.2034405327140102e-07,
        n.dha(): 1.0296456279861962e-11,
        n.glutathion_ox(): 4.99986167652437e-12,
    }
