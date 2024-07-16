from __future__ import annotations

from typing import TYPE_CHECKING

from qtbmodels import names as n

from ._utils import build_vmax_multiple

if TYPE_CHECKING:
    from modelbase.ode import Model


def _rate_translocator(
    pi: float,
    pga: float,
    gap: float,
    dhap: float,
    k_pxt: float,
    p_ext: float,
    k_pi: float,
    k_pga: float,
    k_gap: float,
    k_dhap: float,
) -> float:
    return 1 + (1 + k_pxt / p_ext) * (
        pi / k_pi + pga / k_pga + gap / k_gap + dhap / k_dhap
    )


def _rate_out(
    s1: float,
    n_total: float,
    vmax_efflux: float,
    k_efflux: float,
) -> float:
    return vmax_efflux * s1 / (n_total * k_efflux)


def add_triose_phosphate_exporters(
    model: Model,
    *,
    chl_stroma: str,
    enzyme_factor: str | None = None,
    e0: float = 1.0,
) -> Model:
    n_translocator = "N_translocator"
    pga_name = n.ex_pga()
    gap_name = n.ex_gap()
    dhap_name = n.ex_dhap()

    model.add_parameter("K_pga", 0.25)
    model.add_parameter("K_gap", 0.075)
    model.add_parameter("K_dhap", 0.077)
    model.add_parameter("external_orthophosphate", 0.5)
    model.add_parameter("K_pxt", 0.74)
    model.add_parameter("K_pi", 0.63)

    enzymes = build_vmax_multiple(
        model,
        enzyme_name="EX_triose_phosphates",
        reaction_names=[pga_name, gap_name, dhap_name],
        kcats=[0.25 * 8, 0.25 * 8, 0.25 * 8],
        enzyme_factor=enzyme_factor,
        e0=e0,
    )

    model.add_derived_compound(
        name=n_translocator,
        function=_rate_translocator,
        args=[
            n.pi(chl_stroma),
            n.pga(chl_stroma),
            n.gap(chl_stroma),
            n.dhap(chl_stroma),
            "K_pxt",
            "external_orthophosphate",
            "K_pi",
            "K_pga",
            "K_gap",
            "K_dhap",
        ],
    )

    enzyme_name = pga_name
    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=_rate_out,
        stoichiometry={
            n.pga(chl_stroma): -1,
        },
        args=[
            n.pga(chl_stroma),
            n_translocator,
            enzymes[pga_name].vmax,
            "K_pga",
        ],
    )

    enzyme_name = gap_name
    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=_rate_out,
        stoichiometry={
            n.gap(chl_stroma): -1,
        },
        args=[
            n.gap(chl_stroma),
            n_translocator,
            enzymes[gap_name].vmax,
            "K_gap",
        ],
    )

    enzyme_name = dhap_name
    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=_rate_out,
        stoichiometry={
            n.dhap(chl_stroma): -1,
        },
        args=[
            n.dhap(chl_stroma),
            n_translocator,
            enzymes[dhap_name].vmax,
            "K_dhap",
        ],
    )
    return model
