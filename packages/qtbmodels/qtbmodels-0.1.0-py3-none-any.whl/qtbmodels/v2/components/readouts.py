from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import div


def _rate_fluorescence(
    Q: float,
    B0: float,
    B2: float,
    ps2cs: float,
    k2: float,
    kF: float,
    kH: float,
) -> float:
    return ps2cs * kF * B0 / (kF + k2 + kH * Q) + ps2cs * kF * B2 / (
        kF + kH * Q
    )


def add_readouts(
    model: Model,
    *,
    pq: bool = False,
    fd: bool = False,
    pc: bool = False,
    nadph: bool = False,
    atp: bool = False,
    fluorescence: bool = False,
) -> Model:
    if pq:
        model.add_readout(
            name="PQ_ox/tot",
            function=div,
            args=[n.pq_red(), "PQ_total"],
        )
    if fd:
        model.add_readout(
            name="Fd_ox/tot",
            function=div,
            args=[n.fd_red(), "Fd_total"],
        )
    if pc:
        model.add_readout(
            name="PC_ox/tot",
            function=div,
            args=[n.pc_red(), "PC_total"],
        )
    if nadph:
        model.add_readout(
            name="NADPH/tot",
            function=div,
            args=[n.nadph(), "NADP*_total"],
        )
    if atp:
        model.add_readout(
            name="ATP/tot",
            function=div,
            args=[n.atp(), "A*P_total"],
        )
    if fluorescence:
        model.add_readout(
            name=n.fluorescence(),
            function=_rate_fluorescence,
            args=[
                n.quencher(),
                n.b0(),
                n.b2(),
                n.ps2cs(),
                "k2",
                "kF",
                "kH",
            ],
        )
    return model
