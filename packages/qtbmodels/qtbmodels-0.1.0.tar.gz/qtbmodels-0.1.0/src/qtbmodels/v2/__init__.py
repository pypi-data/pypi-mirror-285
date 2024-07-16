from __future__ import annotations

__all__ = [
    "get_ebeling2024",
    "get_matuszynska2016npq",
    "get_matuszynska2019",
    "get_poolman2000",
    "get_poolman2000",
    "get_saadat2021",
    "get_yokota1985",
    "get_vanaalst2023",
    "get_y0_matuszynska2016npq",
    "get_y0_matuszynska2019",
    "get_y0_poolman2000",
    "get_y0_saadat2021",
    "get_y0_yokota1985",
    "get_y0_vanaalst2023",
    "Simulator",
]

import math
from dataclasses import dataclass
from typing import Any, TypeVar, cast, overload

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from modelbase.ode import Model, Simulator, _Simulate
from tqdm.auto import tqdm

from qtbmodels import names as n

from .models import (
    get_ebeling2024,
    get_matuszynska2016npq,
    get_matuszynska2019,
    get_poolman2000,
    get_saadat2021,
    get_vanaalst2023,
    get_y0_matuszynska2016npq,
    get_y0_matuszynska2019,
    get_y0_poolman2000,
    get_y0_saadat2021,
    get_y0_vanaalst2023,
    get_y0_yokota1985,
    get_yokota1985,
)

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")


def unwrap(x: T | None) -> T:
    if x is None:
        raise ValueError
    return x


def unwrap2(x: tuple[T1 | None, T2 | None]) -> tuple[T1, T2]:
    x1, x2 = x
    if x1 is None:
        raise ValueError
    if x2 is None:
        raise ValueError
    return (x1, x2)


@overload
def carbon_yield(v: dict[str, float]) -> float:
    ...


@overload
def carbon_yield(v: pd.DataFrame) -> pd.Series:
    ...


@overload
def carbon_yield(v: pd.Series) -> float:  # type: ignore
    ...


def carbon_yield(
    v: dict[str, float] | pd.Series | pd.DataFrame,
) -> pd.Series | float:
    return (
        v[n.ex_pga()] * 3
        + v[n.ex_gap()] * 3
        + v[n.ex_dhap()] * 3
        + v[n.ex_g1p()] * 6
    )


@dataclass
class PamPhase:
    pfd_background: float
    n_pulses: int
    pfd_pulse: float = 5000
    t_pulse: float | None = 0.8
    t_between: float = 90


def create_pam_input(phases: list[PamPhase]) -> pd.DataFrame:
    t_start: float = 0
    data = {}
    for phase in phases:
        t_between = phase.t_between
        t_phase = t_between * phase.n_pulses
        t_end = t_start + t_phase
        for t in np.arange(t_start, t_end, t_between):
            if (t_pulse := phase.t_pulse) is not None:
                data[t + t_pulse] = {n.pfd(): phase.pfd_pulse}
            data[t + phase.t_between] = {n.pfd(): phase.pfd_background}
        t_start = t_end
    return pd.DataFrame(data).T


def adapt_to_pfd(
    model: Model, pfd: float, y0: dict[str, float]
) -> dict[str, float]:
    return unwrap(
        Simulator(model)
        .initialise(y0)
        .update_parameter(n.pfd(), pfd)
        .simulate_to_steady_state_and()
        .get_new_y0()
    )


def run_pam_experiment(
    model: Model,
    y0: dict[str, float],
    experiment: pd.DataFrame,
    initial_pfd: float,
    integrator_kwargs: dict[str, Any] | None = None,
) -> _Simulate:
    s = Simulator(model)
    s.initialise(adapt_to_pfd(model, initial_pfd, y0))
    t_end: float
    for t_end, data in tqdm(  # type: ignore
        experiment.iterrows(), total=len(experiment), desc="Simulation"
    ):  # type: ignore
        s.update_parameters({n.pfd(): data[n.pfd()]})
        if integrator_kwargs is None:
            integrator_kwargs = {}
        _, y = unwrap2(s.simulate(t_end, **integrator_kwargs))
        if y is None:
            msg = f"Simulation failed at t < {t_end}, pfd={data['pfd']}"
            raise ValueError(msg)
    return s


def normalise(x: np.ndarray) -> np.ndarray:
    return (x - np.min(x)) / (np.max(x) - np.min(x))  # type: ignore


def shade_light(
    ax: Axes,
    lights: np.ndarray,
    times: list[tuple[float, float]],
    edgecolor: str | None = None,
) -> None:
    for pfd, (t_start, t_end) in zip(lights, times):
        ax.axvspan(
            t_start,
            t_end,
            facecolor=(pfd, pfd, pfd, 0.25),
            edgecolor=edgecolor,
        )


def add_pulse_markers(
    ax: Axes,
    lights: np.ndarray,
    times: list[tuple[float, float]],
) -> None:
    def center(x: tuple[float, float]) -> float:
        return x[0] + (x[1] - x[0]) / 2

    t_pulses = np.array(
        [center(times[idx]) for idx in np.where(lights == np.max(lights))[0]]
    )
    ax.plot(
        t_pulses,
        np.full_like(t_pulses, 1.05),
        linestyle="None",
        marker=7,
        color="black",
    )


def extract_pam_info(
    s: _Simulate,
) -> tuple[pd.Series, np.ndarray, list[tuple[Any, Any]]]:
    res: pd.DataFrame = unwrap(s.get_full_results_df())
    times = [(i[0], i[-1]) for i in s.time]
    lights = np.array([i[n.pfd()] for i in s.simulation_parameters])
    fluorescence = res[n.fluorescence()]
    return fluorescence, lights, times


def plot_pam_experiment(
    s: _Simulate,
    ax: Axes | None = None,
) -> None:
    fluorescence, lights, times = extract_pam_info(s)
    if ax is None:
        _, ax = plt.subplots()
        ax = cast(Axes, ax)
    (fluorescence / fluorescence.max()).plot(
        ax=ax,
        xlabel="time / s",
        ylabel="Fluorescence normalised to Fm",
    )
    shade_light(ax, normalise(np.log(lights)), times)
    add_pulse_markers(ax, lights, times)


def fvfm(m: Model, y0: dict[str, float], pfd_dark: float = 50) -> float:
    s = Simulator(m)
    s.initialise(y0)
    s.update_parameter(n.pfd(), pfd_dark)
    s.simulate_to_steady_state()
    if (c := s.get_full_results_df()) is None:
        raise ValueError
    f0: float = c[n.fluorescence()].iloc[-1]
    pam, *_ = extract_pam_info(
        run_pam_experiment(
            m,
            y0,
            create_pam_input(
                [
                    PamPhase(
                        pfd_background=pfd_dark,
                        n_pulses=1,
                        pfd_pulse=5000,
                        t_pulse=0.8,
                        t_between=90,
                    ),
                ]
            ),
            initial_pfd=pfd_dark,
        )
    )
    fm: float = pam.max()
    fv: float = fm - f0
    return fv / fm


def grid_layout(
    nrows: int,
    ncols: int = 2,
    colwidth: int = 4,
    rowheight: int = 4,
    *,
    sharex: bool = True,
    sharey: bool = False,
) -> tuple[plt.Figure, np.ndarray]:  # type: ignore
    nrows = math.ceil(nrows / ncols)
    fig, axs = plt.subplots(
        nrows,
        ncols,
        figsize=(colwidth * ncols, rowheight * nrows),
        sharex=sharex,
        sharey=sharey,
        layout="constrained",
    )
    return fig, axs
