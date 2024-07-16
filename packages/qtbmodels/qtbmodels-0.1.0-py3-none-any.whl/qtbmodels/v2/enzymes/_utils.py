from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from qtbmodels import names as n
from qtbmodels.shared import proportional

if TYPE_CHECKING:
    from modelbase.ode import Model


def add_parameter_if_missing(model: Model, name: str, value: float) -> None:
    if name not in model.parameters:
        model.add_parameter(name, value)


class EnzymeNames(NamedTuple):
    vmax: str
    kcat: str
    e0: str


class RedoxPair(NamedTuple):
    red: str
    ox: str


def filter_stoichiometry(
    model: Model,
    stoichiometry: dict[str, float],
    optional: dict[str, float] | None = None,
) -> dict[str, float]:
    """Only use components that are actually compounds in the model"""
    new: dict[str, float] = {}
    for k, v in stoichiometry.items():
        if k in model.compounds:
            new[k] = v
        elif k not in model._ids:  # noqa: SLF001
            msg = f"Missing component {k}"
            raise KeyError(msg)

    optional = {} if optional is None else optional
    for k, v in optional.items():
        if k in model.compounds:
            new[k] = v
    return new


def static_vmax(
    model: Model,
    *,
    enzyme_name: str,
    kcat: float,
    e0: float,
) -> EnzymeNames:
    vmax_name = n.vmax(enzyme_name)
    kcat_name = n.kcat(enzyme_name)
    e0_name = n.e0(enzyme_name)

    model.add_parameter(kcat_name, kcat)
    model.add_parameter(e0_name, e0)

    model.add_derived_parameter(
        vmax_name,
        proportional,
        [kcat_name, e0_name],
    )
    return EnzymeNames(vmax_name, kcat_name, e0_name)


def dynamic_vmax(
    model: Model,
    *,
    enzyme_name: str,
    kcat: float,
    enzyme_factor: str,
    e0: float,
) -> EnzymeNames:
    # FIXME: should sometimes be derived compounds, sometimes parameter
    # Check the condition for this

    vmax_name = n.vmax(enzyme_name)
    kcat_name = n.kcat(enzyme_name)
    e0_name = n.e0(enzyme_name)
    e_name = n.e(enzyme_name)

    model.add_parameter(kcat_name, kcat)
    if e0_name not in model.parameters:
        model.add_parameter(e0_name, e0)

    model.add_derived_compound(
        name=e_name,
        function=proportional,
        args=[enzyme_factor, e0_name],
    )

    model.add_derived_compound(
        name=vmax_name,
        function=proportional,
        args=[kcat_name, e_name],
    )
    return EnzymeNames(vmax_name, kcat_name, e_name)


def static_vmax_multiple(
    model: Model,
    *,
    enzyme_name: str,
    reaction_names: list[str],
    kcats: list[float],
    e0: float = 1.0,
) -> dict[str, EnzymeNames]:
    e0_name = n.e0(enzyme_name)
    model.add_parameter(e0_name, e0)

    enzyme_names = {}
    for reaction_name, kcat in zip(reaction_names, kcats):
        vmax_name = n.vmax(reaction_name)
        kcat_name = n.kcat(reaction_name)
        model.add_parameter(kcat_name, kcat)
        model.add_derived_parameter(
            vmax_name,
            proportional,
            [kcat_name, e0_name],
        )
        enzyme_names[reaction_name] = EnzymeNames(
            vmax_name, kcat_name, e0_name
        )
    return enzyme_names


def dynamic_vmax_multiple(
    model: Model,
    *,
    enzyme_name: str,
    reaction_names: list[str],
    kcats: list[float],
    e_factor: str,
    e0: float = 1.0,
) -> dict[str, EnzymeNames]:
    # FIXME: should sometimes be derived compounds, sometimes parameter
    # Check the condition for this
    e0_name = n.e0(enzyme_name)
    e_name = n.e(enzyme_name)
    model.add_parameter(e0_name, e0)

    model.add_derived_compound(
        name=e_name,
        function=proportional,
        args=[e_factor, e0_name],
    )

    enzyme_names = {}
    for reaction_name, kcat in zip(reaction_names, kcats):
        vmax_name = n.vmax(reaction_name)
        kcat_name = n.kcat(reaction_name)
        model.add_parameter(kcat_name, kcat)
        model.add_derived_compound(
            name=vmax_name,
            function=proportional,
            args=[kcat_name, e_name],
        )
        enzyme_names[reaction_name] = EnzymeNames(
            vmax_name, kcat_name, e0_name
        )
    return enzyme_names


def build_vmax(
    model: Model,
    *,
    enzyme_name: str,
    kcat: float,
    enzyme_factor: str | None,
    e0: float,
) -> EnzymeNames:
    if enzyme_factor is None:
        return static_vmax(
            model,
            enzyme_name=enzyme_name,
            kcat=kcat,
            e0=e0,
        )
    return dynamic_vmax(
        model,
        enzyme_name=enzyme_name,
        kcat=kcat,
        enzyme_factor=enzyme_factor,
        e0=e0,
    )


def build_vmax_multiple(
    model: Model,
    *,
    enzyme_name: str,
    reaction_names: list[str],
    kcats: list[float],
    enzyme_factor: str | None,
    e0: float,
) -> dict[str, EnzymeNames]:
    if enzyme_factor is None:
        return static_vmax_multiple(
            model,
            enzyme_name=enzyme_name,
            reaction_names=reaction_names,
            kcats=kcats,
            e0=e0,
        )
    return dynamic_vmax_multiple(
        model,
        enzyme_name=enzyme_name,
        reaction_names=reaction_names,
        kcats=kcats,
        e_factor=enzyme_factor,
        e0=e0,
    )


# def choose_rate_function(fn_name: str) -> Callable[..., float]:
#     # return getattr(importlib.import_module("qtbmodels.shared"), fn_name)
#     return globals()[fn_name]  # type: ignore
