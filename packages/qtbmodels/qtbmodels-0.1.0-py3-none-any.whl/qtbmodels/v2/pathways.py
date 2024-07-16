from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from qtbmodels import names as n
from qtbmodels.v2.enzymes.aldolase_dhap_e4p_sbp import add_aldolase_dhap_e4p

from .components import add_orthophosphate_moiety
from .enzymes import (
    add_aldolase_dhap_gap,
    add_fbpase,
    add_g1p_efflux,
    add_gadph,
    add_glucose_6_phosphate_isomerase,
    add_phosphoglucomutase,
    add_phosphoglycerate_kinase_poolman,
    add_phosphoribulokinase,
    add_ribose_5_phosphate_isomerase,
    add_ribulose_5_phosphate_3_epimerase,
    add_rubisco,
    add_sbpase,
    add_transketolase_x5p_e4p_f6p_gap,
    add_transketolase_x5p_r5p_s7p_gap,
    add_triose_phosphate_exporters,
    add_triose_phosphate_isomerase,
)

if TYPE_CHECKING:
    from modelbase.ode import Model


def require(model: Model, components: list[str]) -> None:
    """Usage
    -----

    def add_cbb(model: Model):
        require(model, ["ATP", "ADP", "NADPH", "NADP"])
        ...
    """
    if diff := set(components).difference(model._ids):  # noqa: SLF001
        msg = f"Missing components: {sorted(diff)}"
        raise ValueError(msg)


def add_cbb(
    model: Model,
    *,
    chl_stroma: str,
    total_orthophosphate: float,
    rubisco_variant: Literal["poolman", "witzel"],
) -> Model:
    require(
        model,
        [
            n.atp(chl_stroma),
            n.adp(chl_stroma),
            n.nadph(chl_stroma),
            n.nadp(chl_stroma),
            n.h(chl_stroma),
            n.co2(chl_stroma),
        ],
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
    add_orthophosphate_moiety(
        model,
        chl_stroma=chl_stroma,
        total=total_orthophosphate,
    )

    # Reactions
    add_rubisco(
        model,
        chl_stroma=chl_stroma,
        variant=rubisco_variant,
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
    return model
