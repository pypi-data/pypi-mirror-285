from typing import Callable

from modelbase.ode import Model

from qtbmodels import names as n


def _rate_orthophosphate_cbb(
    phosphate_total: float,
    pga: float,
    bpga: float,
    gap: float,
    dhap: float,
    fbp: float,
    f6p: float,
    g6p: float,
    g1p: float,
    sbp: float,
    s7p: float,
    e4p: float,
    x5p: float,
    r5p: float,
    rubp: float,
    ru5p: float,
    atp: float,
) -> float:
    return phosphate_total - (
        pga
        + 2 * bpga
        + gap
        + dhap
        + 2 * fbp
        + f6p
        + g6p
        + g1p
        + 2 * sbp
        + s7p
        + e4p
        + x5p
        + r5p
        + 2 * rubp
        + ru5p
        + atp
    )


def _rate_orthophosphate_cbb_pr(
    phosphate_total: float,
    pga: float,
    bpga: float,
    gap: float,
    dhap: float,
    fbp: float,
    f6p: float,
    g6p: float,
    g1p: float,
    sbp: float,
    s7p: float,
    e4p: float,
    x5p: float,
    r5p: float,
    rubp: float,
    ru5p: float,
    atp: float,
    pgo: float,
) -> float:
    return phosphate_total - (
        pga
        + 2 * bpga
        + gap
        + dhap
        + 2 * fbp
        + f6p
        + g6p
        + g1p
        + 2 * sbp
        + s7p
        + e4p
        + x5p
        + r5p
        + 2 * rubp
        + ru5p
        + atp
        + pgo
    )


def add_orthophosphate_moiety(
    model: Model,
    *,
    chl_stroma: str,
    total: float = 15.0,
) -> Model:
    model.add_parameter("Phosphate_total", total)

    args = [
        "Phosphate_total",
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
        n.atp(chl_stroma),
    ]

    function: Callable[..., float]
    if n.pgo() in model._ids:  # noqa: SLF001
        args.append(n.pgo())
        function = _rate_orthophosphate_cbb_pr

    else:
        function = _rate_orthophosphate_cbb

    model.add_derived_compound(
        name=n.pi(chl_stroma),
        function=function,
        args=args,
    )

    return model
