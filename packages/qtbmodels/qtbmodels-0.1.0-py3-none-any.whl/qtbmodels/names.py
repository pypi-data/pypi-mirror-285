# from dataclasses import dataclass, field


# @dataclass
# class Name:
#     py_long: str
#     tex_key: str
#     tex_long: str
#     tex_abbrv: str = ""
#     compartment: str = ""
#     tissue: str = ""
#     description: str = ""

#     def __post_init__(self) -> None:
#         if not self.tex_abbrv:
#             self.tex_abbrv = self.tex_key.upper()

#     def __call__(self) -> str:
#         return f"{self.py_long}{self.compartment}{self.tissue}"
from __future__ import annotations


def loc(name: str, compartment: str, tissue: str) -> str:
    return f"{name}{compartment}{tissue}"


def _default() -> str:
    raise NotImplementedError


###############################################################################
# Parameters / Variables
###############################################################################


def energy(compartment: str = "", tissue: str = "") -> str:
    """dummy variable for energy state"""
    return loc("energy", compartment, tissue)


def a0(compartment: str = "", tissue: str = "") -> str:
    """Photosystem II reaction center 0"""
    return loc("A0", compartment, tissue)


def a1(compartment: str = "", tissue: str = "") -> str:
    """Photosystem II reaction center 1"""
    return loc("A1", compartment, tissue)


def a2(compartment: str = "", tissue: str = "") -> str:
    """Photosystem II reaction center 2"""
    return loc("A2", compartment, tissue)


def b0(compartment: str = "", tissue: str = "") -> str:
    return loc("B0", compartment, tissue)


def b1(compartment: str = "", tissue: str = "") -> str:
    return loc("B1", compartment, tissue)


def b2(compartment: str = "", tissue: str = "") -> str:
    return loc("B2", compartment, tissue)


def b3(compartment: str = "", tissue: str = "") -> str:
    return loc("B3", compartment, tissue)


def ps2cs(compartment: str = "", tissue: str = "") -> str:
    return loc("PSII_cross_section", compartment, tissue)


def atp(compartment: str = "", tissue: str = "") -> str:
    return loc("ATP", compartment, tissue)


def adp(compartment: str = "", tissue: str = "") -> str:
    return loc("ADP", compartment, tissue)


def amp(compartment: str = "", tissue: str = "") -> str:
    return loc("AMP", compartment, tissue)


def nadph(compartment: str = "", tissue: str = "") -> str:
    return loc("NADPH", compartment, tissue)


def nadp(compartment: str = "", tissue: str = "") -> str:
    return loc("NADP", compartment, tissue)


def nadh(compartment: str = "", tissue: str = "") -> str:
    return loc("NADH", compartment, tissue)


def nad(compartment: str = "", tissue: str = "") -> str:
    return loc("NAD", compartment, tissue)


def h(compartment: str = "", tissue: str = "") -> str:
    return loc("protons", compartment, tissue)


def ph(compartment: str = "", tissue: str = "") -> str:
    return loc("pH", compartment, tissue)


def pq_ox(compartment: str = "", tissue: str = "") -> str:
    return loc("Plastoquinone (oxidised)", compartment, tissue)


def pq_red(compartment: str = "", tissue: str = "") -> str:
    return loc("Plastoquinone (reduced)", compartment, tissue)


def pc_ox(compartment: str = "", tissue: str = "") -> str:
    return loc("Plastocyanine (oxidised)", compartment, tissue)


def pc_red(compartment: str = "", tissue: str = "") -> str:
    return loc("Plastocyanine (reduced)", compartment, tissue)


def fd_ox(compartment: str = "", tissue: str = "") -> str:
    return loc("Ferredoxine (oxidised)", compartment, tissue)


def fd_red(compartment: str = "", tissue: str = "") -> str:
    return loc("Ferredoxine (reduced)", compartment, tissue)


def lhc(compartment: str = "", tissue: str = "") -> str:
    return loc("Light-harvesting complex", compartment, tissue)


def lhcp(compartment: str = "", tissue: str = "") -> str:
    return loc("Light-harvesting complex (protonated)", compartment, tissue)


def psbs_de(compartment: str = "", tissue: str = "") -> str:
    """Deprotonated Psbs"""
    return loc("PsbS (de-protonated)", compartment, tissue)


def psbs_pr(compartment: str = "", tissue: str = "") -> str:
    """Protonated Psbs"""
    return loc("PsbS (protonated)", compartment, tissue)


def vx(compartment: str = "", tissue: str = "") -> str:
    return loc("Violaxanthin", compartment, tissue)


def zx(compartment: str = "", tissue: str = "") -> str:
    return loc("Zeaxanthin", compartment, tissue)


def tr_ox(compartment: str = "", tissue: str = "") -> str:
    return loc("Thioredoxin (oxidised)", compartment, tissue)


def tr_red(compartment: str = "", tissue: str = "") -> str:
    return loc("Thioredoxin (reduced)", compartment, tissue)


def pi(compartment: str = "", tissue: str = "") -> str:
    return loc("Orthophosphate", compartment, tissue)


def ppi(compartment: str = "", tissue: str = "") -> str:
    return loc("Diphosphate", compartment, tissue)


def co2(compartment: str = "", tissue: str = "") -> str:
    return loc("CO2 (dissolved)", compartment, tissue)


def co2_atmosphere(compartment: str = "", tissue: str = "") -> str:
    return loc("CO2 (atmosphere)", compartment, tissue)


def hco3(compartment: str = "", tissue: str = "") -> str:
    return loc("HCO3", compartment, tissue)


def o2(compartment: str = "", tissue: str = "") -> str:
    return loc("O2 (dissolved)", compartment, tissue)


def o2_atmosphere(compartment: str = "", tissue: str = "") -> str:
    return loc("O2 (atmosphere)", compartment, tissue)


def h2o2(compartment: str = "", tissue: str = "") -> str:
    return loc("H2O2", compartment, tissue)


def pga(compartment: str = "", tissue: str = "") -> str:
    return loc("3PGA", compartment, tissue)


def pga2(compartment: str = "", tissue: str = "") -> str:
    return loc("2PGA", compartment, tissue)


def pgo(compartment: str = "", tissue: str = "") -> str:
    return loc("PGO", compartment, tissue)


def bpga(compartment: str = "", tissue: str = "") -> str:
    return loc("BPGA", compartment, tissue)


def gap(compartment: str = "", tissue: str = "") -> str:
    return loc("GAP", compartment, tissue)


def dhap(compartment: str = "", tissue: str = "") -> str:
    return loc("DHAP", compartment, tissue)


def fbp(compartment: str = "", tissue: str = "") -> str:
    return loc("FBP", compartment, tissue)


def f6p(compartment: str = "", tissue: str = "") -> str:
    return loc("F6P", compartment, tissue)


def g6p(compartment: str = "", tissue: str = "") -> str:
    return loc("G6P", compartment, tissue)


def g1p(compartment: str = "", tissue: str = "") -> str:
    return loc("G1P", compartment, tissue)


def sbp(compartment: str = "", tissue: str = "") -> str:
    return loc("SBP", compartment, tissue)


def s7p(compartment: str = "", tissue: str = "") -> str:
    return loc("S7P", compartment, tissue)


def erythrose(compartment: str = "", tissue: str = "") -> str:
    """Erythrose"""
    return loc("erythrose", compartment, tissue)


def e4p(compartment: str = "", tissue: str = "") -> str:
    """Erythrose-4-phosphate"""
    return loc("E4P", compartment, tissue)


def erythrulose(compartment: str = "", tissue: str = "") -> str:
    return loc("erythrulose", compartment, tissue)


def erythrulose_1p(compartment: str = "", tissue: str = "") -> str:
    return loc("erythrulose_1p", compartment, tissue)


def erythrulose_4p(compartment: str = "", tissue: str = "") -> str:
    return loc("erythrulose_4p", compartment, tissue)


def xylulose(compartment: str = "", tissue: str = "") -> str:
    """Xylulose"""
    return loc("xylulose", compartment, tissue)


def x5p(compartment: str = "", tissue: str = "") -> str:
    """Xylulose-5-phosphate"""
    return loc("X5P", compartment, tissue)


def ribose(compartment: str = "", tissue: str = "") -> str:
    """Ribose"""
    return loc("ribose", compartment, tissue)


def r1p(compartment: str = "", tissue: str = "") -> str:
    """Ribose-1-phosphate"""
    return loc("R1P", compartment, tissue)


def r5p(compartment: str = "", tissue: str = "") -> str:
    """Ribose-5-phosphate"""
    return loc("R5P", compartment, tissue)


def rubp(compartment: str = "", tissue: str = "") -> str:
    """Ribulose-1,5-bisphosphate"""
    return loc("RUBP", compartment, tissue)


def ru5p(compartment: str = "", tissue: str = "") -> str:
    return loc("RU5P", compartment, tissue)


def starch(compartment: str = "", tissue: str = "") -> str:
    return loc("starch", compartment, tissue)


def mda(compartment: str = "", tissue: str = "") -> str:
    return loc("MDA", compartment, tissue)


def dha(compartment: str = "", tissue: str = "") -> str:
    return loc("DHA", compartment, tissue)


def ascorbate(compartment: str = "", tissue: str = "") -> str:
    return loc("ascorbate", compartment, tissue)


def glutathion_red(compartment: str = "", tissue: str = "") -> str:
    """Glutathion (reduced) / GSH"""
    return loc("GSH", compartment, tissue)


def glutathion_ox(compartment: str = "", tissue: str = "") -> str:
    """Glutathion (oxidised) / GSSG"""
    return loc("GSSG", compartment, tissue)


def glycine(compartment: str = "", tissue: str = "") -> str:
    return loc("glycine", compartment, tissue)


def glyoxylate(compartment: str = "", tissue: str = "") -> str:
    return loc("glyoxylate", compartment, tissue)


def glycolate(compartment: str = "", tissue: str = "") -> str:
    return loc("glycolate", compartment, tissue)


def glycerate(compartment: str = "", tissue: str = "") -> str:
    return loc("glycerate", compartment, tissue)


def pyruvate(compartment: str = "", tissue: str = "") -> str:
    return loc("pyruvate", compartment, tissue)


def hydroxypyruvate(compartment: str = "", tissue: str = "") -> str:
    return loc("hydroxypyruvate", compartment, tissue)


def serine(compartment: str = "", tissue: str = "") -> str:
    return loc("serine", compartment, tissue)


def pfd(compartment: str = "", tissue: str = "") -> str:
    """Photosynthetic Photon Flux Density"""
    return loc("PPFD", compartment, tissue)


def quencher(compartment: str = "", tissue: str = "") -> str:
    return loc("Q", compartment, tissue)


def fluorescence(compartment: str = "", tissue: str = "") -> str:
    return loc("Fluo", compartment, tissue)


def e_active(compartment: str = "", tissue: str = "") -> str:
    return loc("E_active", compartment, tissue)


def e_inactive(compartment: str = "", tissue: str = "") -> str:
    return loc("E_inactive", compartment, tissue)


def oxoglutarate(compartment: str = "", tissue: str = "") -> str:
    return loc("2-oxoglutarate", compartment, tissue)


def glutamate(compartment: str = "", tissue: str = "") -> str:
    return loc("GLU", compartment, tissue)


def glutamine(compartment: str = "", tissue: str = "") -> str:
    return loc("GLN", compartment, tissue)


def nh4(compartment: str = "", tissue: str = "") -> str:
    return loc("NH4", compartment, tissue)


def acetoacetate(compartment: str = "", tissue: str = "") -> str:
    """aka: ketobutyrate"""
    return loc("acetoacetate", compartment, tissue)


def coa(compartment: str = "", tissue: str = "") -> str:
    return loc("CoA", compartment, tissue)


def acetyl_coa(compartment: str = "", tissue: str = "") -> str:
    return loc("acetyl-CoA", compartment, tissue)


def acetoacetyl_coa(compartment: str = "", tissue: str = "") -> str:
    return loc("acetoacetyl-CoA", compartment, tissue)


def malonyl_coa(compartment: str = "", tissue: str = "") -> str:
    return loc("malonyl-CoA", compartment, tissue)


def formyl_coa(compartment: str = "", tissue: str = "") -> str:
    return loc("formyl-CoA", compartment, tissue)


def tartronyl_coa(compartment: str = "", tissue: str = "") -> str:
    return loc("tartronyl-CoA", compartment, tissue)


def succinyl_coa(compartment: str = "", tissue: str = "") -> str:
    return loc("succinyl-CoA", compartment, tissue)


def glycolyl_coa(compartment: str = "", tissue: str = "") -> str:
    return loc("glycolyl-CoA", compartment, tissue)


def malonate_s_aldehyde(compartment: str = "", tissue: str = "") -> str:
    return loc("malonate-s-aldehyde", compartment, tissue)


def succinate(compartment: str = "", tissue: str = "") -> str:
    return loc("succinate", compartment, tissue)


def formate(compartment: str = "", tissue: str = "") -> str:
    return loc("formate", compartment, tissue)


def thf(compartment: str = "", tissue: str = "") -> str:
    return loc("THF", compartment, tissue)


def formyl_thf(compartment: str = "", tissue: str = "") -> str:
    return loc("10-formyl-THF", compartment, tissue)


def methylene_thf(compartment: str = "", tissue: str = "") -> str:
    return loc("methylene-THF", compartment, tissue)


def methenyl_thf(compartment: str = "", tissue: str = "") -> str:
    return loc("methenyl-THF", compartment, tissue)


def aspartate(compartment: str = "", tissue: str = "") -> str:
    return loc("aspartate", compartment, tissue)


def hydroxyaspartate(compartment: str = "", tissue: str = "") -> str:
    return loc("hydroxyaspartate", compartment, tissue)


def iminoaspartate(compartment: str = "", tissue: str = "") -> str:
    return loc("iminoaspartate", compartment, tissue)


def oxalate(compartment: str = "", tissue: str = "") -> str:
    # synonyms: ethanedoic acid, oxalic acid
    return loc("oxalate", compartment, tissue)


def oxaloacetate(compartment: str = "", tissue: str = "") -> str:
    return loc("oxaloacetate", compartment, tissue)


def malate(compartment: str = "", tissue: str = "") -> str:
    return loc("malate", compartment, tissue)


def pep(compartment: str = "", tissue: str = "") -> str:
    """Phosphoenolpyruvat"""
    return loc("PEP", compartment, tissue)


def tartronate_semialdehyde(compartment: str = "", tissue: str = "") -> str:
    return loc("tartronate_semialdehyde", compartment, tissue)


def arabinose_5_phosphate(compartment: str = "", tissue: str = "") -> str:
    return loc("A5P", compartment, tissue)


def glycolaldehyde(compartment: str = "", tissue: str = "") -> str:
    return loc("glycolaldehyde", compartment, tissue)


def alanine(compartment: str = "", tissue: str = "") -> str:
    return loc("alanine", compartment, tissue)


def arginine(compartment: str = "", tissue: str = "") -> str:
    return loc("arginine", compartment, tissue)


def asparagine(compartment: str = "", tissue: str = "") -> str:
    return loc("asparagine", compartment, tissue)


def cysteine(compartment: str = "", tissue: str = "") -> str:
    return loc("cysteine", compartment, tissue)


def histidine(compartment: str = "", tissue: str = "") -> str:
    return loc("histidine", compartment, tissue)


def isoleucine(compartment: str = "", tissue: str = "") -> str:
    return loc("isoleucine", compartment, tissue)


def leucine(compartment: str = "", tissue: str = "") -> str:
    return loc("leucine", compartment, tissue)


def lysine(compartment: str = "", tissue: str = "") -> str:
    return loc("lysine", compartment, tissue)


def methionine(compartment: str = "", tissue: str = "") -> str:
    return loc("methionine", compartment, tissue)


def phenylalanine(compartment: str = "", tissue: str = "") -> str:
    return loc("phenylalanine", compartment, tissue)


def proline(compartment: str = "", tissue: str = "") -> str:
    return loc("proline", compartment, tissue)


def threonine(compartment: str = "", tissue: str = "") -> str:
    return loc("threonine", compartment, tissue)


def tryptophan(compartment: str = "", tissue: str = "") -> str:
    return loc("tryptophan", compartment, tissue)


def tyrosine(compartment: str = "", tissue: str = "") -> str:
    return loc("tyrosine", compartment, tissue)


def valine(compartment: str = "", tissue: str = "") -> str:
    return loc("valine", compartment, tissue)


###############################################################################
# Parameter fns
###############################################################################


def e0(enzyme: str) -> str:
    return f"E0_{enzyme}"


def e(enzyme: str) -> str:
    return f"E_{enzyme}"


def kcat(enzyme: str) -> str:
    return f"kcat_{enzyme}"


def vmax(enzyme: str) -> str:
    return f"vmax_{enzyme}"


def keq(enzyme: str) -> str:
    return f"keq_{enzyme}"


def k(enzyme: str) -> str:
    return f"k_{enzyme}"


def km(enzyme: str, substrate: str | None = None) -> str:
    if substrate is None:
        return f"km_{enzyme}"
    return f"km_{enzyme}_{substrate}"


def kms(enzyme: str) -> str:
    return km(enzyme, "s")


def kmp(enzyme: str) -> str:
    return km(enzyme, "p")


def ki(enzyme: str, substrate: str | None = None) -> str:
    if substrate is None:
        return f"ki_{enzyme}"
    return f"ki_{enzyme}_{substrate}"


def ka(enzyme: str, substrate: str | None = None) -> str:
    if substrate is None:
        return f"ki_{enzyme}"
    return f"ki_{enzyme}_{substrate}"


###############################################################################
# Moieties
###############################################################################


def total_adenosines(compartment: str = "", tissue: str = "") -> str:
    return loc("A*P", compartment, tissue)


def total_nadp(compartment: str = "", tissue: str = "") -> str:
    return loc("NADP*", compartment, tissue)


def total_nad(compartment: str = "", tissue: str = "") -> str:
    return loc("NAD*", compartment, tissue)


###############################################################################
# Reactions / Enzymes
###############################################################################


def aspartate_aminotransferase(compartment: str = "", tissue: str = "") -> str:
    return loc("aspartate_aminotransferase", compartment, tissue)


def aspartate_oxidoreductase(compartment: str = "", tissue: str = "") -> str:
    return loc("aspartate_oxidoreductase", compartment, tissue)


def oxidative_phosphorylation(compartment: str = "", tissue: str = "") -> str:
    return loc("oxidative_phosphorylation", compartment, tissue)


def oxalate_oxidase(compartment: str = "", tissue: str = "") -> str:
    return loc("oxalate_oxidase", compartment, tissue)


def glycolaldehyde_dehydrogenase(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("glycolaldehyde_dehydrogenase", compartment, tissue)


def a5p_aldolase(compartment: str = "", tissue: str = "") -> str:
    return loc("a5p_aldolase", compartment, tissue)


def a5p_isomerase(compartment: str = "", tissue: str = "") -> str:
    return loc("a5p_isomerase", compartment, tissue)


def r1p_aldolase(compartment: str = "", tissue: str = "") -> str:
    return loc("r1p_aldolase", compartment, tissue)


def r1p_kinase(compartment: str = "", tissue: str = "") -> str:
    return loc("r1p_kinase", compartment, tissue)


def transaldolase_f6p_gad_gap_xyl(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("transaldolase_f6p_gad_gap_xyl", compartment, tissue)


def transketolase_gad_s7p_r5p_eru(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("transketolase_gad_s7p_r5p_eru", compartment, tissue)


def transketolase_f6p_gad_gap_xylulose(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("transketolase_f6p_gad_gap_xylulose", compartment, tissue)


def enolase(compartment: str = "", tissue: str = "") -> str:
    return loc("enolase", compartment, tissue)


def erythrulose_kinase(compartment: str = "", tissue: str = "") -> str:
    return loc("erythrulose_kinase", compartment, tissue)


def e4p_epimerase(compartment: str = "", tissue: str = "") -> str:
    return loc("e4p_epimerase", compartment, tissue)


def e4p_isomerase(compartment: str = "", tissue: str = "") -> str:
    return loc("e4p_isomerase", compartment, tissue)


def xylulose_kinase(compartment: str = "", tissue: str = "") -> str:
    return loc("xylulose_kinase", compartment, tissue)


def acetoacetate_coa_ligase(compartment: str = "", tissue: str = "") -> str:
    return loc("acetoacetate_coa_ligase", compartment, tissue)


def acetyl_coa_acetyltransfer(compartment: str = "", tissue: str = "") -> str:
    return loc("acetyl_coa_acetyltransfer", compartment, tissue)


def acetyl_coa_carboxyltransfer(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("acetyl_coa_carboxyltransfer", compartment, tissue)


def aldolase_dhap_gap(compartment: str = "", tissue: str = "") -> str:
    return loc("aldolase_dhap_gap", compartment, tissue)


def aldolase_dhap_e4p(compartment: str = "", tissue: str = "") -> str:
    return loc("aldolase_dhap_e4p", compartment, tissue)


def ascorbate_peroxidase(compartment: str = "", tissue: str = "") -> str:
    return loc("ascorbate_peroxidase", compartment, tissue)


def atp_synthase(compartment: str = "", tissue: str = "") -> str:
    return loc("atp_synthase", compartment, tissue)


def b6f(compartment: str = "", tissue: str = "") -> str:
    return loc("b6f", compartment, tissue)


def bkace(compartment: str = "", tissue: str = "") -> str:
    return loc("bkace", compartment, tissue)


def carbonic_anhydrase(compartment: str = "", tissue: str = "") -> str:
    return loc("carbonic_anhydrase", compartment, tissue)


def catalase(compartment: str = "", tissue: str = "") -> str:
    return loc("catalase", compartment, tissue)


def cyclic_electron_flow(compartment: str = "", tissue: str = "") -> str:
    return loc("cyclic_electron_flow", compartment, tissue)


def co2_dissolving(compartment: str = "", tissue: str = "") -> str:
    return loc("co2_dissolving", compartment, tissue)


def coa_transf_a(compartment: str = "", tissue: str = "") -> str:
    return loc("coa_transf_a", compartment, tissue)


def coa_transf_b(compartment: str = "", tissue: str = "") -> str:
    return loc("coa_transf_b", compartment, tissue)


def dehydroascorbate_reductase(compartment: str = "", tissue: str = "") -> str:
    return loc("dehydroascorbate_reductase", compartment, tissue)


def ex_atp(compartment: str = "", tissue: str = "") -> str:
    return loc("ex_atp", compartment, tissue)


def ex_nadph(compartment: str = "", tissue: str = "") -> str:
    return loc("ex_nadph", compartment, tissue)


def ex_g1p(compartment: str = "", tissue: str = "") -> str:
    return loc("ex_g1p", compartment, tissue)


def ex_pga(compartment: str = "", tissue: str = "") -> str:
    return loc("ex_pga", compartment, tissue)


def ex_gap(compartment: str = "", tissue: str = "") -> str:
    return loc("ex_gap", compartment, tissue)


def ex_dhap(compartment: str = "", tissue: str = "") -> str:
    return loc("ex_dhap", compartment, tissue)


def fbpase(compartment: str = "", tissue: str = "") -> str:
    return loc("fbpase", compartment, tissue)


def ferredoxin_reductase(compartment: str = "", tissue: str = "") -> str:
    return loc("ferredoxin_reductase", compartment, tissue)


def fnr(compartment: str = "", tissue: str = "") -> str:
    return loc("fnr", compartment, tissue)


def formate_dehydrogenase(compartment: str = "", tissue: str = "") -> str:
    return loc("formate_dehydrogenase", compartment, tissue)


def formate_thf_ligase(compartment: str = "", tissue: str = "") -> str:
    return loc("formate_thf_ligase", compartment, tissue)


def g6pi(compartment: str = "", tissue: str = "") -> str:
    return loc("g6pi", compartment, tissue)


def gadph(compartment: str = "", tissue: str = "") -> str:
    return loc("gadph", compartment, tissue)


def glutathion_reductase(compartment: str = "", tissue: str = "") -> str:
    return loc("glutathion_reductase", compartment, tissue)


def glycerate_dehydrogenase(compartment: str = "", tissue: str = "") -> str:
    return loc("glycerate_dehydrogenase", compartment, tissue)


def glycerate_kinase(compartment: str = "", tissue: str = "") -> str:
    return loc("glycerate_kinase", compartment, tissue)


def glycine_decarboxylase(compartment: str = "", tissue: str = "") -> str:
    return loc("glycine_decarboxylase", compartment, tissue)


def glycine_hydroxymethyltransferase(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("glycine_hydroxymethyltransferase", compartment, tissue)


def glycine_transaminase(compartment: str = "", tissue: str = "") -> str:
    return loc("glycine_transaminase", compartment, tissue)


def glycolate_dehydrogenase(compartment: str = "", tissue: str = "") -> str:
    return loc("glycolate_dehydrogenase", compartment, tissue)


def glycolate_oxidase(compartment: str = "", tissue: str = "") -> str:
    return loc("glycolate_oxidase", compartment, tissue)


def glyoxylate_oxidase(compartment: str = "", tissue: str = "") -> str:
    return loc("glyoxylate_oxidase", compartment, tissue)


def glycolyl_coa_carboxylase(compartment: str = "", tissue: str = "") -> str:
    return loc("glycolyl_coa_carboxylase", compartment, tissue)


def glycolyl_coa_synthetase(compartment: str = "", tissue: str = "") -> str:
    return loc("glycolyl_coa_synthetase", compartment, tissue)


def glyoxylate_carboligase(compartment: str = "", tissue: str = "") -> str:
    return loc("glyoxylate_carboligase", compartment, tissue)


def hydroxyaspartate_aldolase(compartment: str = "", tissue: str = "") -> str:
    return loc("hydroxyaspartate_aldolase", compartment, tissue)


def hydroxyaspartate_hydrolase(compartment: str = "", tissue: str = "") -> str:
    return loc("hydroxyaspartate_hydrolase", compartment, tissue)


def lhc_deprotonation(compartment: str = "", tissue: str = "") -> str:
    return loc("lhc_deprotonation", compartment, tissue)


def lhc_protonation(compartment: str = "", tissue: str = "") -> str:
    return loc("lhc_protonation", compartment, tissue)


def lhc_state_transition_12(compartment: str = "", tissue: str = "") -> str:
    return loc("lhc_state_transition_12", compartment, tissue)


def lhc_state_transition_21(compartment: str = "", tissue: str = "") -> str:
    return loc("lhc_state_transition_21", compartment, tissue)


def malate_dehydrogenase(compartment: str = "", tissue: str = "") -> str:
    return loc("malate_dehydrogenase", compartment, tissue)


def malate_synthase(compartment: str = "", tissue: str = "") -> str:
    return loc("malate_synthase", compartment, tissue)


def malic_enzyme(compartment: str = "", tissue: str = "") -> str:
    return loc("malic_enzyme", compartment, tissue)


def malonyl_coa_reductase(compartment: str = "", tissue: str = "") -> str:
    return loc("malonyl_coa_reductase", compartment, tissue)


def mda_reductase1(compartment: str = "", tissue: str = "") -> str:
    # FIXME
    return loc("mda_reductase_1", compartment, tissue)


def mda_reductase2(compartment: str = "", tissue: str = "") -> str:
    # FIXME
    return loc("mda_reductase_2", compartment, tissue)


def mehler(compartment: str = "", tissue: str = "") -> str:
    return loc("mehler", compartment, tissue)


def methylene_thf_dehydrogenase(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("methylene_thf_dehydrogenase", compartment, tissue)


def ndh(compartment: str = "", tissue: str = "") -> str:
    return loc("ndh", compartment, tissue)


def mthfc(compartment: str = "", tissue: str = "") -> str:
    # FIXME: look up proper name of this
    return loc("mthfc", compartment, tissue)


def nitrogen_fixation(compartment: str = "", tissue: str = "") -> str:
    return loc("nitrogen_fixation", compartment, tissue)


def oxaloacetate_formation(compartment: str = "", tissue: str = "") -> str:
    return loc("oxaloacetate_formation", compartment, tissue)


def pep_carboxylase(compartment: str = "", tissue: str = "") -> str:
    return loc("pep_carboxylase", compartment, tissue)


def phosphoglucomutase(compartment: str = "", tissue: str = "") -> str:
    return loc("phosphoglucomutase", compartment, tissue)


def phosphoglycerate_kinase(compartment: str = "", tissue: str = "") -> str:
    return loc("phosphoglycerate_kinase", compartment, tissue)


def phosphoglycerate_mutase(compartment: str = "", tissue: str = "") -> str:
    return loc("phosphoglycerate_mutase", compartment, tissue)


def phosphoglycolate_phosphatase(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("phosphoglycolate_phosphatase", compartment, tissue)


def phosphoribulokinase(compartment: str = "", tissue: str = "") -> str:
    return loc("phosphoribulokinase", compartment, tissue)


def proton_leak(compartment: str = "", tissue: str = "") -> str:
    return loc("proton_leak", compartment, tissue)


def petc(compartment: str = "", tissue: str = "") -> str:
    return loc("PETC", compartment, tissue)


def ps1(compartment: str = "", tissue: str = "") -> str:
    return loc("PSI", compartment, tissue)


def ps2(compartment: str = "", tissue: str = "") -> str:
    return loc("PSII", compartment, tissue)


def ptox(compartment: str = "", tissue: str = "") -> str:
    return loc("PTOX", compartment, tissue)


def pyruvate_dehydrogenase(compartment: str = "", tissue: str = "") -> str:
    return loc("pyruvate_dehydrogenase", compartment, tissue)


def pyruvate_phosphate_dikinase(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("pyruvate_phosphate_dikinase", compartment, tissue)


def ribulose_phosphate_epimerase(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("ribulose_phosphate_epimerase", compartment, tissue)


def ribose_phosphate_isomerase(compartment: str = "", tissue: str = "") -> str:
    return loc("ribose_phosphate_isomerase", compartment, tissue)


def rubisco(compartment: str = "", tissue: str = "") -> str:
    return loc("rubisco", compartment, tissue)


def rubisco_carboxylase(compartment: str = "", tissue: str = "") -> str:
    return loc("rubisco_carboxylase", compartment, tissue)


def rubisco_oxygenase(compartment: str = "", tissue: str = "") -> str:
    return loc("rubisco_oxygenase", compartment, tissue)


def sbpase(compartment: str = "", tissue: str = "") -> str:
    return loc("SBPase", compartment, tissue)


def serine_glyoxylate_transaminase(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("serine_glyoxylate_transaminase", compartment, tissue)


def succinyl_coa_synthetase(compartment: str = "", tissue: str = "") -> str:
    return loc("succinyl_coa_synthetase", compartment, tissue)


def tartronate_semialdehyde_reductase(
    compartment: str = "", tissue: str = ""
) -> str:
    return loc("tartronate_semialdehyde_reductase", compartment, tissue)


def tartronyl_coa_reductase(compartment: str = "", tissue: str = "") -> str:
    return loc("tartronyl_coa_reductase", compartment, tissue)


def thioesterase(compartment: str = "", tissue: str = "") -> str:
    return loc("thioesterase", compartment, tissue)


def transketolase_gap_f6p(compartment: str = "", tissue: str = "") -> str:
    return loc("transketolase_gap_f6p", compartment, tissue)


def transketolase_gap_s7p(compartment: str = "", tissue: str = "") -> str:
    return loc("transketolase_gap_s7p", compartment, tissue)


def triose_phosphate_isomerase(compartment: str = "", tissue: str = "") -> str:
    return loc("triose_phosphate_isomerase", compartment, tissue)


def violaxanthin_deepoxidase(compartment: str = "", tissue: str = "") -> str:
    return loc("violaxanthin_deepoxidase", compartment, tissue)


def zeaxanthin_epoxidase(compartment: str = "", tissue: str = "") -> str:
    return loc("zeaxanthin_epoxidase", compartment, tissue)


def gogat(compartment: str = "", tissue: str = "") -> str:
    return loc("gogat", compartment, tissue)


def glutamine_synthase(compartment: str = "", tissue: str = "") -> str:
    return loc("glutamine_synthase", compartment, tissue)


def glutamate_dehydrogenase(compartment: str = "", tissue: str = "") -> str:
    return loc("glutamate_dehydrogenase", compartment, tissue)
