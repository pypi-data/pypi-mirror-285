from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modelbase.ode import Model


def add_vmax(model: Model, name: str, kcat: float, e0: float = 1.0) -> str:
    kcat_name = f"kcat_{name}"
    enzyme_name = f"E0_{name}"
    vmax_name = f"Vmax_{name}"
    model.add_parameter(kcat_name, kcat)
    model.add_parameter(enzyme_name, e0)
    model.add_derived_parameter(
        vmax_name, proportional, [kcat_name, enzyme_name]
    )
    return vmax_name


###############################################################################
# General-purpose functions
###############################################################################


def value(x: float) -> float:
    return x


def neg(x: float) -> float:
    return -x


def div(x: float, y: float) -> float:
    return x / y


def neg_div(x: float, y: float) -> float:
    return -x / y


def twice(x: float) -> float:
    return x * 2


def proportional(x: float, y: float) -> float:
    return x * y


def diffusion(inside: float, outside: float, k: float) -> float:
    return k * (outside - inside)


###############################################################################
# Common algebraic modules
###############################################################################


def moiety_1(concentration: float, total: float) -> float:
    return total - concentration


def moiety_2(x1: float, x2: float, total: float) -> float:
    return total - x1 - x2


###############################################################################
# Common rate laws
###############################################################################


def mass_action_1s(s1: float, k_fwd: float) -> float:
    return k_fwd * s1


def mass_action_2s(s1: float, s2: float, k_fwd: float) -> float:
    return k_fwd * s1 * s2


def mass_action_3s(s1: float, s2: float, s3: float, k_fwd: float) -> float:
    return k_fwd * s1 * s2 * s3


def mass_action_4s(
    s1: float, s2: float, s3: float, s4: float, k_fwd: float
) -> float:
    return k_fwd * s1 * s2 * s3 * s4


def reversible_mass_action_keq_1s_1p(
    s1: float, p1: float, kf: float, keq: float
) -> float:
    return kf * (s1 - p1 / keq)


def reversible_mass_action_keq_1s_2p(
    s1: float, p1: float, p2: float, kf: float, keq: float
) -> float:
    return kf * (s1 - p1 * p2 / keq)


def reversible_mass_action_keq_1s_3p(
    s1: float, p1: float, p2: float, p3: float, kf: float, keq: float
) -> float:
    return kf * (s1 - p1 * p2 * p3 / keq)


def reversible_mass_action_keq_2s_1p(
    s1: float, s2: float, p1: float, kf: float, keq: float
) -> float:
    return kf * (s1 * s2 - p1 / keq)


def reversible_mass_action_keq_2s_2p(
    s1: float, s2: float, p1: float, p2: float, kf: float, keq: float
) -> float:
    return kf * (s1 * s2 - p1 * p2 / keq)


def reversible_mass_action_keq_2s_3p(
    s1: float,
    s2: float,
    p1: float,
    p2: float,
    p3: float,
    kf: float,
    keq: float,
) -> float:
    return kf * (s1 * s2 - p1 * p2 * p3 / keq)


def reversible_mass_action_keq_3s_1p(
    s1: float, s2: float, s3: float, p1: float, kf: float, keq: float
) -> float:
    return kf * (s1 * s2 * s3 - p1 / keq)


def reversible_mass_action_keq_3s_2p(
    s1: float,
    s2: float,
    s3: float,
    p1: float,
    p2: float,
    kf: float,
    keq: float,
) -> float:
    return kf * (s1 * s2 * s3 - p1 * p2 / keq)


def reversible_mass_action_keq_3s_3p(
    s1: float,
    s2: float,
    s3: float,
    p1: float,
    p2: float,
    p3: float,
    kf: float,
    keq: float,
) -> float:
    return kf * (s1 * s2 * s3 - p1 * p2 * p3 / keq)


def reversible_mass_action_keq_3s_4p(
    s1: float,
    s2: float,
    s3: float,
    p1: float,
    p2: float,
    p3: float,
    p4: float,
    kf: float,
    keq: float,
) -> float:
    return kf * (s1 * s2 * s3 - p1 * p2 * p3 * p4 / keq)


def michaelis_menten_1s(
    s: float,
    vmax: float,
    km: float,
) -> float:
    return vmax * s / (km + s)


def michaelis_menten_2s(
    s1: float,
    s2: float,
    vmax: float,
    km: float,
) -> float:
    return vmax * s1 * s2 / (s1 * s2 + km * s1 + km * s2)


def michaelis_menten_2s_2km(
    s1: float,
    s2: float,
    vmax: float,
    km_s1: float,
    km_s2: float,
) -> float:
    return vmax * s1 * s2 / (s1 * s2 + km_s1 * s1 + km_s2 * s2)


def michaelis_menten_3s(
    s1: float,
    s2: float,
    s3: float,
    vmax: float,
    km: float,
) -> float:
    return (
        vmax
        * s1
        * s2
        * s3
        / (s1 * s2 * s3 + km * s2 * s3 + km * s1 * s3 + km * s1 * s2)
    )


def michaelis_menten_1s_1i(
    s: float,
    i: float,
    vmax: float,
    km: float,
    ki: float,
) -> float:
    return vmax * s / (s + km * (1 + i / ki))


def michaelis_menten_1s_2i(
    s: float,
    i1: float,
    i2: float,
    vmax: float,
    km: float,
    ki1: float,
    ki2: float,
) -> float:
    return vmax * s / (s + km * (1 + i1 / ki1 + i2 / ki2))


def michaelis_menten_1s_3i(
    s: float,
    i1: float,
    i2: float,
    i3: float,
    vmax: float,
    km: float,
    ki1: float,
    ki2: float,
    ki3: float,
) -> float:
    return vmax * s / (s + km * (1 + i1 / ki1 + i2 / ki2 + i3 / ki3))


def michaelis_menten_1s_4i(
    s: float,
    i1: float,
    i2: float,
    i3: float,
    i4: float,
    vmax: float,
    km: float,
    ki1: float,
    ki2: float,
    ki3: float,
    ki4: float,
) -> float:
    return (
        vmax * s / (s + km * (1 + i1 / ki1 + i2 / ki2 + i3 / ki3 + i4 / ki4))
    )


def reversible_michaelis_menten_1s_1p(
    s1: float,
    p1: float,
    vmax: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return vmax / kms * (1 / (1 + s1 / kms + p1 / kmp)) * (s1 - p1 / keq)


def reversible_michaelis_menten_1s_1p_1i(
    s1: float,
    p1: float,
    i1: float,
    vmax: float,
    kms: float,
    kmp: float,
    ki: float,
    keq: float,
) -> float:
    return (
        vmax
        / kms
        * (1 / (1 + s1 / (kms * (1 + i1 / ki)) + p1 / kmp))
        * (s1 - p1 / keq)
    )


def reversible_michaelis_menten_1s_2p(
    s1: float,
    p1: float,
    p2: float,
    vmax: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return (
        vmax
        / kms
        * (1 / (1 + s1 / kms + p1 * p2 / kmp))
        * (s1 - p1 * p2 / keq)
    )


def reversible_michaelis_menten_2s_1p(
    s1: float,
    s2: float,
    p1: float,
    vmax: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return (
        vmax
        / kms
        * (1 / (1 + s1 * s2 / kms + p1 / kmp))
        * (s1 * s2 - p1 / keq)
    )


def reversible_michaelis_menten_2s_2p(
    s1: float,
    s2: float,
    p1: float,
    p2: float,
    vmax: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return (
        vmax
        / kms
        * (1 / (1 + s1 * s2 / kms + p1 * p2 / kmp))
        * (s1 * s2 - p1 * p2 / keq)
    )


def reversible_michaelis_menten_2s_3p(
    s1: float,
    s2: float,
    p1: float,
    p2: float,
    p3: float,
    vmax: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return (
        vmax
        / kms
        * (1 / (1 + s1 * s2 / kms + p1 * p2 * p3 / kmp))
        * (s1 * s2 - p1 * p2 * p3 / keq)
    )


def reversible_michaelis_menten_2s_4p(
    s1: float,
    s2: float,
    p1: float,
    p2: float,
    p3: float,
    p4: float,
    vmax: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return (
        vmax
        / kms
        * (1 / (1 + s1 * s2 / kms + p1 * p2 * p3 * p4 / kmp))
        * (s1 * s2 - p1 * p2 * p3 * p4 / keq)
    )


def reversible_michaelis_menten_3s_1p(
    s1: float,
    s2: float,
    s3: float,
    p1: float,
    vmax: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return (
        vmax
        / kms
        * (1 / (1 + s1 * s2 * s3 / kms + p1 / kmp))
        * (s1 * s2 * s3 - p1 / keq)
    )


def reversible_michaelis_menten_3s_2p(
    s1: float,
    s2: float,
    s3: float,
    p1: float,
    p2: float,
    vmax: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return (
        vmax
        / kms
        * (1 / (1 + s1 * s2 * s3 / kms + p1 * p2 / kmp))
        * (s1 * s2 * s3 - p1 * p2 / keq)
    )


def reversible_michaelis_menten_3s_3p(
    s1: float,
    s2: float,
    s3: float,
    p1: float,
    p2: float,
    p3: float,
    vmax: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return (
        vmax
        / kms
        * (1 / (1 + s1 * s2 * s3 / kms + p1 * p2 * p3 / kmp))
        * (s1 * s2 * s3 - p1 * p2 * p3 / keq)
    )


def reversible_michaelis_menten_3s_4p(
    s1: float,
    s2: float,
    s3: float,
    p1: float,
    p2: float,
    p3: float,
    p4: float,
    vmax: float,
    kms: float,
    kmp: float,
    keq: float,
) -> float:
    return (
        vmax
        / kms
        * (1 / (1 + s1 * s2 * s3 / kms + p1 * p2 * p3 * p4 / kmp))
        * (s1 * s2 * s3 - p1 * p2 * p3 * p4 / keq)
    )


def ping_pong_bi_bi(
    s1: float, s2: float, vmax: float, km_s1: float, km_s2: float
) -> float:
    return (
        vmax
        * s1
        * s2
        / (1 / (km_s1 * km_s2) + s1 / km_s1 + s2 / km_s2 + s1 * s2)
    )
