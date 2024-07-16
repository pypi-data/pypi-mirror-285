"""Ideas:
? how about add_cbb(...), with e.g. get_poolman being essentially just
    add_cbb(static_co2, ...)

! split weird enzyme descriptions instead of having nested if / else
! remove redox_pair flags, as they also require different keqs

"""

from __future__ import annotations

from modelbase.ode import Model

from qtbmodels import names as n

from .components import (
    add_ascorbate_moiety,
    add_atp_adp,
    add_co2,
    add_enzyme_factor,
    add_ferredoxin_moiety,
    add_glutamate_and_oxoglutarate,
    add_glutathion_moiety,
    add_lhc_moiety,
    add_nadh_static,
    add_nadp_nadph,
    add_nh4,
    add_o2,
    add_orthophosphate_moiety,
    add_ph_lumen,
    add_plastocyanin_moiety,
    add_plastoquinone_keq,
    add_plastoquinone_moiety,
    add_protons_stroma,
    add_psbs_moietry,
    add_quencher,
    add_readouts,
    add_rt,
    add_thioredoxin,
)
from .enzymes import (
    add_aldolase_dhap_e4p,
    add_aldolase_dhap_gap,
    add_ascorbate_peroxidase,
    add_atp_consumption,
    add_atp_synthase,
    add_atp_synthase_2024,
    add_atp_synthase_static_protons,
    add_b6f,
    add_b6f_2024,
    add_carotenoid_moiety,
    add_catalase,
    add_cbb_pfd_speedup,
    add_cyclic_electron_flow,
    add_dehydroascorbate_reductase,
    add_fbpase,
    add_ferredoxin_reductase,
    add_fnr,
    add_g1p_efflux,
    add_gadph,
    add_glucose_6_phosphate_isomerase,
    add_glutathion_reductase,
    add_glycerate_dehydrogenase,
    add_glycerate_kinase,
    add_glycine_decarboxylase_yokota,
    add_glycine_transaminase_yokota,
    add_glycolate_oxidase,
    add_hpa_outflux,
    add_lhc_deprotonation,
    add_lhc_protonation,
    add_mda_reductase2,
    add_nadph_consumption,
    add_ndh,
    add_nitrogen_metabolism,
    add_phosphoglucomutase,
    add_phosphoglycerate_kinase_poolman,
    add_phosphoglycolate_influx,
    add_phosphoglycolate_phosphatase,
    add_phosphoribulokinase,
    add_photosystems,
    add_proton_leak,
    add_ps2_cross_section,
    add_ptox,
    add_ribose_5_phosphate_isomerase,
    add_ribulose_5_phosphate_3_epimerase,
    add_rubisco,
    add_sbpase,
    add_serine_glyoxylate_transaminase,
    add_state_transitions,
    add_thioredoxin_regulation2021,
    add_transketolase_x5p_e4p_f6p_gap,
    add_transketolase_x5p_r5p_s7p_gap,
    add_triose_phosphate_exporters,
    add_triose_phosphate_isomerase,
    add_violaxanthin_epoxidase,
    add_zeaxanthin_epoxidase,
)
from .enzymes.glycine_decarboxylase import (
    add_glycine_decarboxylase_irreversible,
)
from .enzymes.serine_glyoxylate_transaminase import (
    add_serine_glyoxylate_transaminase_irreversible,
)


def get_yokota1985(
    chl_stroma: str = "",
    per: str = "",
) -> Model:
    model = Model()
    model.add_compounds(
        [
            n.glycolate(chl_stroma),  # mit would also be fair
            n.glyoxylate(per),
            n.glycine(per),  # and mit
            n.serine(per),  # and mit
            n.hydroxypyruvate(per),
            n.h2o2(per),
        ]
    )

    add_phosphoglycolate_influx(
        model=model,
        chl_stroma=chl_stroma,
    )
    add_glycolate_oxidase(
        model=model,
        chl_stroma=chl_stroma,
    )
    add_glycine_transaminase_yokota(
        model=model,
    )
    add_glycine_decarboxylase_yokota(
        model=model,
        e0=0.5,
    )
    add_serine_glyoxylate_transaminase_irreversible(
        model=model,
    )
    add_hpa_outflux(
        model=model,
        per=per,
    )
    add_catalase(model=model)
    return model


def get_y0_yokota1985() -> dict[str, float]:
    return {
        n.glycolate(): 0,
        n.glyoxylate(): 0,
        n.glycine(): 0,
        n.serine(): 0,
        n.hydroxypyruvate(): 0,
        n.h2o2(): 0,
    }


def get_poolman2000(
    *,
    static_nadph: bool = True,
    static_co2: bool = True,
    static_atp: bool = False,
    chl_stroma: str = "",
) -> Model:
    model = Model()

    add_co2(
        model,
        chl_stroma=chl_stroma,
        static=static_co2,
        par_value=0.2,
    )
    add_atp_adp(model, compartment=chl_stroma, static=static_atp, total=0.5)
    add_nadp_nadph(
        model,
        compartment=chl_stroma,
        static=static_nadph,
        nadph=0.21,
        total=0.5,
    )
    model.add_compounds(
        [
            n.pga(chl_stroma),
            n.bpga(chl_stroma),
            n.gap(chl_stroma),
            n.dhap(chl_stroma),
            n.fbp(chl_stroma),
            n.f6p(chl_stroma),
            n.g6p(chl_stroma),
            n.g1p(chl_stroma),
            n.sbp(chl_stroma),
            n.s7p(chl_stroma),
            n.e4p(chl_stroma),
            n.x5p(chl_stroma),
            n.r5p(chl_stroma),
            n.rubp(chl_stroma),
            n.ru5p(chl_stroma),
        ]
    )

    # Moieties
    add_protons_stroma(model, chl_stroma=chl_stroma)
    add_orthophosphate_moiety(
        model,
        chl_stroma=chl_stroma,
        total=15.0,
    )

    # Reactions
    add_rubisco(
        model,
        chl_stroma=chl_stroma,
        variant="poolman",
    )
    add_phosphoglycerate_kinase_poolman(model, chl_stroma=chl_stroma)
    add_gadph(model, chl_stroma=chl_stroma)
    add_triose_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_aldolase_dhap_gap(model, chl_stroma=chl_stroma)
    add_aldolase_dhap_e4p(model, chl_stroma=chl_stroma)
    add_fbpase(model, chl_stroma=chl_stroma)
    add_transketolase_x5p_e4p_f6p_gap(model, chl_stroma=chl_stroma)
    add_transketolase_x5p_r5p_s7p_gap(model, chl_stroma=chl_stroma)
    add_sbpase(model, chl_stroma=chl_stroma)
    add_ribose_5_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_ribulose_5_phosphate_3_epimerase(model, chl_stroma=chl_stroma)
    add_phosphoribulokinase(model, chl_stroma=chl_stroma)
    add_glucose_6_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_phosphoglucomutase(model, chl_stroma=chl_stroma)
    add_triose_phosphate_exporters(model, chl_stroma=chl_stroma)
    add_g1p_efflux(model, chl_stroma=chl_stroma)

    # Other
    add_atp_synthase_static_protons(
        model,
        chl_stroma=chl_stroma,
    )

    return model


def get_y0_poolman2000() -> dict[str, float]:
    return {
        n.pga(): 0.6387788347932627,
        n.bpga(): 0.0013570885908749779,
        n.gap(): 0.011259431827358068,
        n.dhap(): 0.24770748227012374,
        n.fbp(): 0.01980222074817044,
        n.f6p(): 1.093666906864421,
        n.g6p(): 2.5154338857582377,
        n.g1p(): 0.14589516537322303,
        n.sbp(): 0.09132688566151095,
        n.s7p(): 0.23281380022778891,
        n.e4p(): 0.02836065066520614,
        n.x5p(): 0.03647242425941113,
        n.r5p(): 0.06109130988031577,
        n.rubp(): 0.2672164362349537,
        n.ru5p(): 0.0244365238237522,
        n.atp(): 0.43633201706180874,
    }


def get_matuszynska2016npq(
    chl_stroma: str = "",
    chl_lumen: str = "_lumen",
    *,
    static_nadph: bool = True,
    mehler: bool = False,
) -> Model:
    model = Model()
    model.add_compounds(
        [
            n.pq_ox(chl_stroma),
            n.pc_ox(chl_stroma),
            n.fd_ox(chl_stroma),
            n.h(chl_lumen),
            n.lhc(),
            n.psbs_de(),
            n.vx(),
        ]
    )
    add_nadp_nadph(
        model,
        compartment=chl_stroma,
        static=static_nadph,
        nadph=0.6,
        total=0.8,
    )
    add_o2(model, compartment=chl_lumen, static=True, par_value=8.0)

    model.add_parameters(
        {
            n.ph(chl_stroma): 7.9,
            n.pfd(): 100.0,
            "bH": 100.0,
            "F": 96.485,
            "E^0_PC": 0.38,
            "E^0_P700": 0.48,
            "E^0_FA": -0.55,
            "E^0_Fd": -0.43,
            "E^0_NADP": -0.113,
        }
    )
    # Moieties / derived compounds
    add_rt(model)
    add_atp_adp(model, compartment=chl_stroma, static=False, total=2.55)
    add_ph_lumen(model, chl_lumen=chl_lumen)
    add_carotenoid_moiety(model)
    add_ferredoxin_moiety(model)
    add_plastocyanin_moiety(model)
    add_psbs_moietry(model)
    add_lhc_moiety(model)
    add_quencher(model)
    add_plastoquinone_keq(model, chl_stroma=chl_stroma)
    add_plastoquinone_moiety(model)
    add_ps2_cross_section(model)

    # Reactions
    add_atp_synthase(
        model,
        chl_stroma=chl_stroma,
        chl_lumen=chl_lumen,
        stroma_unit="mmol/mol Chl",
    )
    add_b6f(model, chl_stroma=chl_stroma, chl_lumen=chl_lumen)
    add_lhc_protonation(model, chl_lumen=chl_lumen)
    add_lhc_deprotonation(model)
    add_cyclic_electron_flow(model)
    add_violaxanthin_epoxidase(model, chl_lumen=chl_lumen)
    add_zeaxanthin_epoxidase(model)
    add_fnr(
        model,
        chl_stroma=chl_stroma,
        stroma_unit="mmol/mol Chl",
    )
    add_ndh(model)
    add_photosystems(model, chl_lumen=chl_lumen, mehler=mehler)
    add_proton_leak(model, chl_stroma=chl_stroma, chl_lumen=chl_lumen)
    add_ptox(model, chl_lumen=chl_lumen)
    add_state_transitions(model)

    # Misc
    add_atp_consumption(model, compartment=chl_stroma, k_val=10.0)
    add_readouts(
        model,
        pq=True,
        fd=True,
        pc=True,
        atp=True,
        fluorescence=True,
    )
    return model


def get_y0_matuszynska2016npq(
    chl_stroma: str = "", chl_lumen: str = "_lumen"
) -> dict[str, float]:
    return {
        n.atp(chl_stroma): 1.6999999999999997,
        n.pq_ox(chl_stroma): 4.706348349506148,
        n.pc_ox(chl_stroma): 3.9414515288091567,
        n.fd_ox(chl_stroma): 3.7761613271207324,
        n.h(chl_lumen): 7.737821100836988,
        n.lhc(): 0.5105293511676007,
        n.psbs_de(): 0.5000000001374878,
        n.vx(): 0.09090909090907397,
    }


def get_matuszynska2019(
    chl_stroma: str = "",
    chl_lumen: str = "_lumen",
    *,
    static_co2: bool = True,
    static_nadph: bool = False,
    mehler: bool = False,
) -> Model:
    model = Model()

    model.add_parameters(
        {
            n.ph(chl_stroma): 7.9,
            n.o2(chl_lumen): 8.0,
            n.pfd(): 100.0,
            "bH": 100.0,
            "F": 96.485,
            "E^0_PC": 0.38,
            "E^0_P700": 0.48,
            "E^0_FA": -0.55,
            "E^0_Fd": -0.43,
            "E^0_NADP": -0.113,
        }
    )

    model.add_compounds(
        [
            # CBB
            n.pga(chl_stroma),
            n.bpga(chl_stroma),
            n.gap(chl_stroma),
            n.dhap(chl_stroma),
            n.fbp(chl_stroma),
            n.f6p(chl_stroma),
            n.g6p(chl_stroma),
            n.g1p(chl_stroma),
            n.sbp(chl_stroma),
            n.s7p(chl_stroma),
            n.e4p(chl_stroma),
            n.x5p(chl_stroma),
            n.r5p(chl_stroma),
            n.rubp(chl_stroma),
            n.ru5p(chl_stroma),
            # PETC
            n.pq_ox(chl_stroma),
            n.pc_ox(chl_stroma),
            n.fd_ox(chl_stroma),
            n.h(chl_lumen),
            n.lhc(),
            n.psbs_de(),
            n.vx(),
        ]
    )
    add_cbb_pfd_speedup(model)

    # Moieties / derived compounds
    add_rt(model)
    add_ph_lumen(model, chl_lumen=chl_lumen)
    add_carotenoid_moiety(model)
    add_ferredoxin_moiety(model)
    add_plastocyanin_moiety(model)
    add_psbs_moietry(model)
    add_lhc_moiety(model)
    add_quencher(model)
    add_plastoquinone_keq(model, chl_stroma=chl_stroma)
    add_plastoquinone_moiety(model)
    add_ps2_cross_section(model)
    add_co2(model, chl_stroma=chl_stroma, static=static_co2, par_value=0.2)
    add_nadp_nadph(
        model, compartment=chl_stroma, static=static_nadph, total=0.8
    )
    add_protons_stroma(model, chl_stroma=chl_stroma)
    add_atp_adp(model, compartment=chl_stroma, static=False, total=2.55)
    add_orthophosphate_moiety(model, chl_stroma=chl_stroma, total=17.05)

    # Reactions
    add_atp_synthase(
        model,
        chl_stroma=chl_stroma,
        chl_lumen=chl_lumen,
        stroma_unit="mM",
    )
    add_b6f(model, chl_stroma=chl_stroma, chl_lumen=chl_lumen)
    add_lhc_protonation(model, chl_lumen=chl_lumen)
    add_lhc_deprotonation(model)
    add_cyclic_electron_flow(model)
    add_violaxanthin_epoxidase(model, chl_lumen=chl_lumen)
    add_zeaxanthin_epoxidase(model)
    add_fnr(
        model,
        chl_stroma=chl_stroma,
        stroma_unit="mM",
    )
    add_ndh(model)
    add_photosystems(model, chl_lumen=chl_lumen, mehler=mehler)
    add_proton_leak(model, chl_stroma=chl_stroma, chl_lumen=chl_lumen)
    add_ptox(model, chl_lumen=chl_lumen)
    add_state_transitions(model)
    add_rubisco(
        model,
        chl_stroma=chl_stroma,
        variant="poolman",
        enzyme_factor="fCBB",
    )
    add_phosphoglycerate_kinase_poolman(model, chl_stroma=chl_stroma)
    add_gadph(model, chl_stroma=chl_stroma)
    add_triose_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_aldolase_dhap_gap(model, chl_stroma=chl_stroma)
    add_aldolase_dhap_e4p(model, chl_stroma=chl_stroma)
    add_fbpase(model, chl_stroma=chl_stroma, enzyme_factor="fCBB")
    add_transketolase_x5p_e4p_f6p_gap(model, chl_stroma=chl_stroma)
    add_transketolase_x5p_r5p_s7p_gap(model, chl_stroma=chl_stroma)
    add_sbpase(model, chl_stroma=chl_stroma, enzyme_factor="fCBB")
    add_ribose_5_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_ribulose_5_phosphate_3_epimerase(model, chl_stroma=chl_stroma)
    add_phosphoribulokinase(
        model,
        chl_stroma=chl_stroma,
        enzyme_factor="fCBB",
    )
    add_glucose_6_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_phosphoglucomutase(model, chl_stroma=chl_stroma)
    add_triose_phosphate_exporters(model, chl_stroma=chl_stroma)
    add_g1p_efflux(
        model,
        chl_stroma=chl_stroma,
        enzyme_factor="fCBB",
    )

    add_readouts(
        model,
        pq=True,
        fd=True,
        pc=True,
        nadph=True,
        atp=True,
        fluorescence=True,
    )
    return model


def get_y0_matuszynska2019(chl_lumen: str = "_lumen") -> dict[str, float]:
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


def get_saadat2021(
    chl_stroma: str = "",
    chl_lumen: str = "_lumen",
    *,
    static_co2: bool = True,
    static_nadph: bool = False,
    mehler: bool = True,
) -> Model:
    model = Model()

    model.add_parameters(
        {
            n.ph(chl_stroma): 7.9,
            n.pfd(): 100.0,
            "bH": 100.0,
            "F": 96.485,
            "E^0_PC": 0.38,
            "E^0_P700": 0.48,
            "E^0_FA": -0.55,
            "E^0_Fd": -0.43,
            "E^0_NADP": -0.113,
        }
    )

    model.add_compounds(
        [
            n.pga(chl_stroma),
            n.bpga(chl_stroma),
            n.gap(chl_stroma),
            n.dhap(chl_stroma),
            n.fbp(chl_stroma),
            n.f6p(chl_stroma),
            n.g6p(chl_stroma),
            n.g1p(chl_stroma),
            n.sbp(chl_stroma),
            n.s7p(chl_stroma),
            n.e4p(chl_stroma),
            n.x5p(chl_stroma),
            n.r5p(chl_stroma),
            n.rubp(chl_stroma),
            n.ru5p(chl_stroma),
            n.pq_ox(chl_stroma),
            n.pc_ox(chl_stroma),
            n.fd_ox(chl_stroma),
            n.h(chl_lumen),
            n.lhc(),
            n.psbs_de(),
            n.vx(),
            # Mehler
            n.mda(),
            n.h2o2(),
            n.dha(),
            n.glutathion_ox(),
        ]
    )

    # Moieties / derived compounds
    add_rt(model)
    add_ph_lumen(model, chl_lumen=chl_lumen)
    add_carotenoid_moiety(model)
    add_ferredoxin_moiety(model)
    add_plastocyanin_moiety(model)
    add_psbs_moietry(model)
    add_lhc_moiety(model)
    add_quencher(model)
    add_plastoquinone_keq(model, chl_stroma=chl_stroma)
    add_plastoquinone_moiety(model)
    add_ps2_cross_section(model)
    add_co2(model, chl_stroma=chl_stroma, static=static_co2, par_value=0.2)
    add_thioredoxin(model)
    add_enzyme_factor(model)

    add_o2(model, compartment=chl_lumen, static=True, par_value=8.0)
    add_nadp_nadph(
        model, compartment=chl_stroma, static=static_nadph, total=0.8
    )
    add_protons_stroma(model, chl_stroma=chl_stroma)
    add_atp_adp(model, compartment=chl_stroma, static=False, total=2.55)
    add_orthophosphate_moiety(model, chl_stroma=chl_stroma, total=17.05)
    add_thioredoxin_regulation2021(model)
    add_ascorbate_moiety(model)
    add_glutathion_moiety(model)

    # Reactions
    ## PETC
    add_atp_synthase(
        model,
        chl_stroma=chl_stroma,
        chl_lumen=chl_lumen,
        stroma_unit="mM",
    )
    add_b6f(model, chl_stroma=chl_stroma, chl_lumen=chl_lumen)
    add_lhc_protonation(model, chl_lumen=chl_lumen)
    add_lhc_deprotonation(model)
    add_cyclic_electron_flow(model)
    add_violaxanthin_epoxidase(model, chl_lumen=chl_lumen)
    add_zeaxanthin_epoxidase(model)
    add_fnr(
        model,
        chl_stroma=chl_stroma,
        stroma_unit="mM",
    )
    add_ndh(model)
    add_photosystems(model, chl_lumen=chl_lumen, mehler=mehler)
    add_ferredoxin_reductase(model)
    add_proton_leak(model, chl_stroma=chl_stroma, chl_lumen=chl_lumen)
    add_ptox(model, chl_lumen=chl_lumen)
    add_state_transitions(model)

    ## CBB
    add_rubisco(
        model,
        chl_stroma=chl_stroma,
        variant="poolman",
        enzyme_factor=n.e_active(),
    )
    add_phosphoglycerate_kinase_poolman(model, chl_stroma=chl_stroma)
    add_gadph(model, chl_stroma=chl_stroma)
    add_triose_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_aldolase_dhap_gap(model, chl_stroma=chl_stroma)
    add_aldolase_dhap_e4p(model, chl_stroma=chl_stroma)
    add_fbpase(model, chl_stroma=chl_stroma, enzyme_factor=n.e_active())
    add_transketolase_x5p_e4p_f6p_gap(model, chl_stroma=chl_stroma)
    add_transketolase_x5p_r5p_s7p_gap(model, chl_stroma=chl_stroma)
    add_sbpase(model, chl_stroma=chl_stroma, enzyme_factor=n.e_active())
    add_ribose_5_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_ribulose_5_phosphate_3_epimerase(model, chl_stroma=chl_stroma)
    add_phosphoribulokinase(
        model,
        chl_stroma=chl_stroma,
        enzyme_factor=n.e_active(),
    )
    add_glucose_6_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_phosphoglucomutase(model, chl_stroma=chl_stroma)
    add_triose_phosphate_exporters(model, chl_stroma=chl_stroma)
    add_g1p_efflux(
        model,
        chl_stroma=chl_stroma,
        enzyme_factor=n.e_active(),
    )

    ## Mehler
    add_mda_reductase2(model)
    add_ascorbate_peroxidase(model)
    add_glutathion_reductase(model)
    add_dehydroascorbate_reductase(model)

    # Misc
    add_atp_consumption(model, compartment=chl_stroma, k_val=0.2)
    add_nadph_consumption(model, compartment=chl_stroma, k_val=0.2)
    add_readouts(
        model,
        pq=True,
        fd=True,
        pc=True,
        nadph=True,
        atp=True,
        fluorescence=True,
    )
    return model


def get_ebeling2024(
    chl_stroma: str = "",
    chl_lumen: str = "_lumen",
    *,
    static_co2: bool = True,
    static_nadph: bool = False,
    mehler: bool = True,
) -> Model:
    model = Model()

    model.add_parameters(
        {
            n.ph(chl_stroma): 7.9,
            n.pfd(): 100.0,
            "bH": 100.0,
            "F": 96.485,
            "E^0_PC": 0.38,
            "E^0_P700": 0.48,
            "E^0_FA": -0.55,
            "E^0_Fd": -0.43,
            "E^0_NADP": -0.113,
        }
    )

    model.add_compounds(
        [
            n.pga(chl_stroma),
            n.bpga(chl_stroma),
            n.gap(chl_stroma),
            n.dhap(chl_stroma),
            n.fbp(chl_stroma),
            n.f6p(chl_stroma),
            n.g6p(chl_stroma),
            n.g1p(chl_stroma),
            n.sbp(chl_stroma),
            n.s7p(chl_stroma),
            n.e4p(chl_stroma),
            n.x5p(chl_stroma),
            n.r5p(chl_stroma),
            n.rubp(chl_stroma),
            n.ru5p(chl_stroma),
            n.pq_ox(chl_stroma),
            n.pc_ox(chl_stroma),
            n.fd_ox(chl_stroma),
            n.h(chl_lumen),
            n.lhc(),
            n.psbs_de(),
            n.vx(),
            # Mehler
            n.mda(),
            n.h2o2(),
            n.dha(),
            n.glutathion_ox(),
        ]
    )

    # Moieties / derived compounds
    add_rt(model)
    add_ph_lumen(model, chl_lumen=chl_lumen)
    add_carotenoid_moiety(model)
    add_ferredoxin_moiety(model)
    add_plastocyanin_moiety(model)
    add_psbs_moietry(model)
    add_lhc_moiety(model)
    add_quencher(model)
    add_plastoquinone_keq(model, chl_stroma=chl_stroma)
    add_plastoquinone_moiety(model)
    add_ps2_cross_section(model)
    add_co2(model, chl_stroma=chl_stroma, static=static_co2, par_value=0.2)
    add_thioredoxin(model)
    add_enzyme_factor(model)

    add_o2(model, compartment=chl_lumen, static=True, par_value=8.0)
    add_nadp_nadph(
        model, compartment=chl_stroma, static=static_nadph, total=0.8
    )
    add_protons_stroma(model, chl_stroma=chl_stroma)
    add_atp_adp(model, compartment=chl_stroma, static=False, total=2.55)
    add_orthophosphate_moiety(model, chl_stroma=chl_stroma, total=17.05)
    add_thioredoxin_regulation2021(model)
    add_ascorbate_moiety(model)
    add_glutathion_moiety(model)

    # Reactions
    ## PETC
    add_atp_synthase_2024(
        model,
        chl_stroma=chl_stroma,
        chl_lumen=chl_lumen,
    )
    add_b6f_2024(model, chl_stroma=chl_stroma, chl_lumen=chl_lumen)
    add_lhc_protonation(model, chl_lumen=chl_lumen)
    add_lhc_deprotonation(model)
    add_cyclic_electron_flow(model)
    add_violaxanthin_epoxidase(model, chl_lumen=chl_lumen)
    add_zeaxanthin_epoxidase(model)
    add_fnr(
        model,
        chl_stroma=chl_stroma,
        stroma_unit="mM",
    )
    add_ndh(model)
    add_photosystems(model, chl_lumen=chl_lumen, mehler=mehler)
    add_ferredoxin_reductase(model)
    add_proton_leak(model, chl_stroma=chl_stroma, chl_lumen=chl_lumen)
    add_ptox(model, chl_lumen=chl_lumen)
    add_state_transitions(model)

    ## CBB
    add_rubisco(
        model,
        chl_stroma=chl_stroma,
        variant="poolman",
        enzyme_factor=n.e_active(),
    )
    add_phosphoglycerate_kinase_poolman(model, chl_stroma=chl_stroma)
    add_gadph(model, chl_stroma=chl_stroma)
    add_triose_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_aldolase_dhap_gap(model, chl_stroma=chl_stroma)
    add_aldolase_dhap_e4p(model, chl_stroma=chl_stroma)
    add_fbpase(model, chl_stroma=chl_stroma, enzyme_factor=n.e_active())
    add_transketolase_x5p_e4p_f6p_gap(model, chl_stroma=chl_stroma)
    add_transketolase_x5p_r5p_s7p_gap(model, chl_stroma=chl_stroma)
    add_sbpase(model, chl_stroma=chl_stroma, enzyme_factor=n.e_active())
    add_ribose_5_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_ribulose_5_phosphate_3_epimerase(model, chl_stroma=chl_stroma)
    add_phosphoribulokinase(
        model,
        chl_stroma=chl_stroma,
        enzyme_factor=n.e_active(),
    )
    add_glucose_6_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_phosphoglucomutase(model, chl_stroma=chl_stroma)
    add_triose_phosphate_exporters(model, chl_stroma=chl_stroma)
    add_g1p_efflux(
        model,
        chl_stroma=chl_stroma,
        enzyme_factor=n.e_active(),
    )

    ## Mehler
    add_mda_reductase2(model)
    add_ascorbate_peroxidase(model)
    add_glutathion_reductase(model)
    add_dehydroascorbate_reductase(model)

    # Misc
    add_atp_consumption(model, compartment=chl_stroma, k_val=0.2)
    add_nadph_consumption(model, compartment=chl_stroma, k_val=0.2)
    add_readouts(
        model,
        pq=True,
        fd=True,
        pc=True,
        nadph=True,
        atp=True,
        fluorescence=True,
    )
    return model


def get_y0_saadat2021(chl_lumen: str = "_lumen") -> dict[str, float]:
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


def get_vanaalst2023(
    chl_stroma: str = "",
    chl_lumen: str = "_lumen",
    per: str = "",
    mit: str = "",
    *,
    static_co2: bool = True,
    static_nadph: bool = False,
    static_nh4: bool = True,
    static_glu: bool = True,
    f_scale_yokota: float = 50.0,
) -> Model:
    """Notes
    - NADPH is super high in our model, but GDC needs NADP to run
        so this leads to buildup of glycine.
        The NADH/NAD ratio in mitochondria is around 0.3, so favoring NAD.
    """
    mehler: bool = False
    model = Model()

    model.add_parameters(
        {
            n.ph(chl_stroma): 7.9,
            n.pfd(): 100.0,
            "bH": 100.0,
            "F": 96.485,
            "E^0_PC": 0.38,
            "E^0_P700": 0.48,
            "E^0_FA": -0.55,
            "E^0_Fd": -0.43,
            "E^0_NADP": -0.113,
        }
    )

    model.add_compounds(
        [
            # Multiple
            n.h2o2(),  # chl_stroma and mit
            # CBB
            n.pga(chl_stroma),
            n.bpga(chl_stroma),
            n.gap(chl_stroma),
            n.dhap(chl_stroma),
            n.fbp(chl_stroma),
            n.f6p(chl_stroma),
            n.g6p(chl_stroma),
            n.g1p(chl_stroma),
            n.sbp(chl_stroma),
            n.s7p(chl_stroma),
            n.e4p(chl_stroma),
            n.x5p(chl_stroma),
            n.r5p(chl_stroma),
            n.rubp(chl_stroma),
            n.ru5p(chl_stroma),
            # PETC
            n.pq_ox(chl_stroma),
            n.pc_ox(chl_stroma),
            n.fd_ox(chl_stroma),
            n.h(chl_lumen),
            n.lhc(),
            n.psbs_de(),
            n.vx(),
            # Mehler
            # n.mda(),
            # n.dha(),
            # n.glutathion_ox(),
            # Yokota
            n.pgo(chl_stroma),
            n.glycolate(chl_stroma),  # mit would also be fair
            n.glyoxylate(per),
            n.glycine(per),  # and mit
            n.serine(per),  # and mit
            n.hydroxypyruvate(per),
            n.glycerate(chl_stroma),  # and mit
        ]
    )

    # Moieties / derived compounds

    add_rt(model)
    add_ph_lumen(model, chl_lumen=chl_lumen)
    add_carotenoid_moiety(model)
    add_ferredoxin_moiety(model)
    add_plastocyanin_moiety(model)
    add_psbs_moietry(model)
    add_lhc_moiety(model)
    add_quencher(model)
    add_plastoquinone_keq(model, chl_stroma=chl_stroma)
    add_plastoquinone_moiety(model)
    add_ps2_cross_section(model)
    add_co2(model, chl_stroma=chl_stroma, static=static_co2, par_value=0.012)
    add_thioredoxin(model)
    add_enzyme_factor(model)

    add_o2(model, compartment=chl_lumen, static=True, par_value=8.0)

    add_o2(model, compartment=chl_stroma, static=True, par_value=0.25)
    add_nadp_nadph(
        model, compartment=chl_stroma, static=static_nadph, total=0.8
    )
    add_nh4(model, static_nh4=static_nh4, par_value=1)
    add_nadh_static(model, compartment=mit)
    add_protons_stroma(model, chl_stroma=chl_stroma)
    add_atp_adp(model, compartment=chl_stroma, static=False, total=2.55)
    add_orthophosphate_moiety(model, chl_stroma=chl_stroma, total=17.05)
    add_thioredoxin_regulation2021(model)
    add_glutamate_and_oxoglutarate(
        model, chl_stroma=chl_stroma, static=static_glu
    )

    # Reactions
    ## PETC
    add_atp_synthase(
        model,
        chl_stroma=chl_stroma,
        chl_lumen=chl_lumen,
        stroma_unit="mM",
    )
    add_b6f(model, chl_stroma=chl_stroma, chl_lumen=chl_lumen)
    add_lhc_protonation(model, chl_lumen=chl_lumen)
    add_lhc_deprotonation(model)
    add_cyclic_electron_flow(model)
    add_violaxanthin_epoxidase(model, chl_lumen=chl_lumen)
    add_zeaxanthin_epoxidase(model)
    add_fnr(
        model,
        chl_stroma=chl_stroma,
        stroma_unit="mM",
    )
    add_ndh(model)
    add_photosystems(model, chl_lumen=chl_lumen, mehler=mehler)

    add_proton_leak(model, chl_stroma=chl_stroma, chl_lumen=chl_lumen)
    add_ptox(model, chl_lumen=chl_lumen)
    add_state_transitions(model)

    ## CBB
    add_rubisco(
        model,
        chl_stroma=chl_stroma,
        variant="witzel",
        enzyme_factor=n.e_active(),
        e0=0.16 * 3.5,
    )
    add_phosphoglycerate_kinase_poolman(model, chl_stroma=chl_stroma)
    add_gadph(model, chl_stroma=chl_stroma)
    add_triose_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_aldolase_dhap_gap(model, chl_stroma=chl_stroma)
    add_aldolase_dhap_e4p(model, chl_stroma=chl_stroma)
    add_fbpase(model, chl_stroma=chl_stroma, enzyme_factor=n.e_active())
    add_transketolase_x5p_e4p_f6p_gap(model, chl_stroma=chl_stroma)
    add_transketolase_x5p_r5p_s7p_gap(model, chl_stroma=chl_stroma)
    add_sbpase(model, chl_stroma=chl_stroma, enzyme_factor=n.e_active())
    add_ribose_5_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_ribulose_5_phosphate_3_epimerase(model, chl_stroma=chl_stroma)
    add_phosphoribulokinase(
        model,
        chl_stroma=chl_stroma,
        enzyme_factor=n.e_active(),
    )
    add_glucose_6_phosphate_isomerase(model, chl_stroma=chl_stroma)
    add_phosphoglucomutase(model, chl_stroma=chl_stroma)
    add_triose_phosphate_exporters(model, chl_stroma=chl_stroma)
    add_g1p_efflux(
        model,
        chl_stroma=chl_stroma,
        enzyme_factor=n.e_active(),
    )

    ## Valero
    # add_ascorbate_moiety(model)
    # add_glutathion_moiety(model)
    # add_ferredoxin_reductase(model)
    # add_3asc(model)
    # add_ascorbate_peroxidase(model)
    # add_glutathion_reductase(model)
    # add_mda_reductase(model)
    # add_dha_reductase(model)

    ## Yokota
    add_phosphoglycolate_phosphatase(
        model=model,
        irreversible=False,
        kcat=292.0 / 3600,
        e0=f_scale_yokota,
    )
    add_glycolate_oxidase(
        model=model,
        chl_stroma=chl_stroma,
        include_o2=True,
        kcat=100.0 / 3600,
        e0=f_scale_yokota * 20,
    )
    add_glycine_transaminase_yokota(
        model=model,
        kcat=143.0 / 3600,
        e0=f_scale_yokota,
    )
    add_glycine_decarboxylase_irreversible(
        model=model,
        nadph_hack=True,
        kcat=100.0 / 3600,
        e0=f_scale_yokota * 5,
        enzyme_factor=n.e_active(),
    )
    add_serine_glyoxylate_transaminase(
        model=model,
        kcat=159.0 / 3600,
        e0=f_scale_yokota,
    )
    add_glycerate_dehydrogenase(
        model=model,
        irreversible=False,
        nadph_hack=True,
        kcat=398.0 / 3600,
        e0=f_scale_yokota,
    )
    add_glycerate_kinase(
        model,
        irreversible=True,
        kcat=5.71579 / 3600,
        e0=f_scale_yokota * 10,
    )
    add_catalase(
        model=model,
        kcat=760500.0 / 3600,
        e0=f_scale_yokota,
    )
    if not static_glu:
        add_nitrogen_metabolism(model)

    # Misc
    add_atp_consumption(model, compartment=chl_stroma, k_val=0.2)
    add_nadph_consumption(model, compartment=chl_stroma, k_val=0.2)
    add_readouts(
        model,
        pq=True,
        fd=True,
        pc=True,
        nadph=True,
        atp=True,
        fluorescence=True,
    )

    return model


def get_y0_vanaalst2023(
    chl_lumen: str = "_lumen",
    *,
    static_co2: bool = True,
    static_nh4: bool = True,
    static_glu: bool = True,
) -> dict[str, float]:
    d = {
        n.pga(): 0.25115945472752155,
        n.bpga(): 0.00026174996017073353,
        n.gap(): 0.00474592159960952,
        n.dhap(): 0.10441026189281974,
        n.fbp(): 0.0035182108117367546,
        n.f6p(): 0.2824917886977682,
        n.g6p(): 0.6497311139358104,
        n.g1p(): 0.037684404606535576,
        n.sbp(): 0.006766411118705844,
        n.s7p(): 0.2119056479551733,
        n.e4p(): 0.0049850789674749695,
        n.x5p(): 0.022590901135337817,
        n.r5p(): 0.03783975884339411,
        n.rubp(): 3.275301654481358,
        n.ru5p(): 0.015135903442328416,
        n.atp(): 1.9653826315616623,
        n.fd_ox(): 3.720137630906563,
        n.h(chl_lumen): 0.002594937687115436,
        n.lhc(): 0.7872501502901426,
        n.nadph(): 0.5594446928084835,
        n.pc_ox(): 1.830325450641911,
        n.pq_ox(): 10.47810012761292,
        n.psbs_de(): 0.9396914553791271,
        n.vx(): 0.8979896438342755,
        n.tr_ox(): 0.9337843790364645,
        n.e_inactive(): 3.6097690248474366,
        n.mda(): 0.0003684677739829048,
        n.h2o2(): 0.0001728652479704914,
        n.dha(): 3.375718985573548e-05,
        n.glutathion_ox(): 1.6387483534653317e-05,
        n.glycine(): 4.747847550003459,
        n.glycolate(): 0.047478475499450765,
        n.glyoxylate(): 0.5480183370803743,
        n.hydroxypyruvate(): 0.007050820771024324,
        n.serine(): 2.0151082531362006,
        n.pgo(): 1.2187262473121726e-06,
        n.glycerate(): 0.00038314541212499146,
    }
    if not static_glu:
        d |= {n.glutamate(): 2.0}
    if not static_co2:
        d |= {n.co2(): 0.012}
    if not static_nh4:
        d |= {n.nh4(): 1}
    return d
