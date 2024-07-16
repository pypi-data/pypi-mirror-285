"""name

EC FIXME

Equilibrator
"""

from modelbase.ode import Model

from qtbmodels import names as n
from qtbmodels.shared import (
    mass_action_1s,
    mass_action_2s,
    michaelis_menten_1s,
)

from ._utils import filter_stoichiometry


def add_cbb_pfd_speedup(model: Model) -> Model:
    model.add_parameters(
        {
            "Km_fcbb": 150.0,
            "Vmax_fcbb": 6.0,
        }
    )
    model.add_derived_parameter(
        "fCBB",
        michaelis_menten_1s,
        [n.pfd(), "Vmax_fcbb", "Km_fcbb"],
    )
    return model


def add_fd_tr_reductase2021(model: Model) -> Model:
    """Equilibrator
    Thioredoxin(ox)(aq) + 2 ferredoxin(red)(aq) ⇌ Thioredoxin(red)(aq) + 2 ferredoxin(ox)(aq)
    Keq = 4.9e3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    enzyme_name = "fd_tr_reductase"
    model.add_parameter(k := n.k(enzyme_name), 1)

    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=mass_action_2s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.tr_ox(): -1,
                n.fd_red(): -1,
                #
                n.tr_red(): 1,
                n.fd_ox(): 1,
            },
        ),
        args=[n.tr_ox(), n.fd_red(), k],
    )
    return model


def add_fd_tr_reductase(model: Model) -> Model:
    """Equilibrator
    Thioredoxin(ox)(aq) + 2 ferredoxin(red)(aq) ⇌ Thioredoxin(red)(aq) + 2 ferredoxin(ox)(aq)
    Keq = 4.9e3 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    enzyme_name = "fd_tr_reductase"
    model.add_parameter(k := n.k(enzyme_name), 1)

    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=mass_action_2s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.tr_ox(): -1,
                n.fd_red(): -2,
                #
                n.tr_red(): 1,
                n.fd_ox(): 2,
            },
        ),
        args=[n.tr_ox(), n.fd_red(), k],
    )
    return model


def add_nadph_tr_reductase(model: Model) -> Model:
    """Equilibrator
    Thioredoxin(ox)(aq) + NADPH(aq) ⇌ Thioredoxin(red)(aq) + NADP(aq)
    Keq = 2e1 (@ pH = 7.5, pMg = 3.0, Ionic strength = 0.25)
    """
    enzyme_name = "nadph_tr_reductase"
    model.add_parameter(k := n.k(enzyme_name), 1)

    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=mass_action_2s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.tr_ox(): -1,
                n.nadph(): -1,
                #
                n.tr_red(): 1,
                n.nadp(): 1,
            },
        ),
        args=[n.tr_ox(), n.nadph(), k],
    )
    return model


def add_tr_e_activation(model: Model) -> Model:
    enzyme_name = "E_activation"
    model.add_parameter(k := "k_e_cbb_activation", 1)
    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=mass_action_2s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.e_inactive(): -1,
                n.tr_red(): -1,
                n.e_active(): 1,
                n.tr_ox(): 1,
            },
        ),
        args=[
            n.e_inactive(),
            n.tr_red(),
            k,
        ],
    )
    return model


def add_tr_e_activation2021(model: Model) -> Model:
    enzyme_name = "E_activation"
    model.add_parameter(k := "k_e_cbb_activation", 1)
    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=mass_action_2s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.e_inactive(): -5,
                n.tr_red(): -5,
                n.e_active(): 5,
                n.tr_ox(): 5,
            },
        ),
        args=[
            n.e_inactive(),
            n.tr_red(),
            k,
        ],
    )
    return model


def add_e_relaxation(model: Model) -> Model:
    enzyme_name = "E_inactivation"
    model.add_parameter(k := "k_e_cbb_relaxation", 0.1)
    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=mass_action_1s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.e_active(): -1,
                n.e_inactive(): 1,
            },
        ),
        args=[
            n.e_active(),
            k,
        ],
    )
    return model


def add_e_relaxation2021(model: Model) -> Model:
    enzyme_name = "E_inactivation"
    model.add_parameter(k := "k_e_cbb_relaxation", 0.1)
    model.add_reaction_from_args(
        rate_name=enzyme_name,
        function=mass_action_1s,
        stoichiometry=filter_stoichiometry(
            model,
            {
                n.e_active(): -5,
                n.e_inactive(): 5,
            },
        ),
        args=[
            n.e_active(),
            k,
        ],
    )
    return model


def add_thioredoxin_regulation(model: Model) -> Model:
    add_fd_tr_reductase(model)
    add_tr_e_activation(model)
    add_e_relaxation(model)
    return model


def add_thioredoxin_regulation2021(model: Model) -> Model:
    add_fd_tr_reductase2021(model)
    add_tr_e_activation2021(model)
    add_e_relaxation2021(model)
    return model


def add_thioredoxin_regulation_from_nadph(model: Model) -> Model:
    add_nadph_tr_reductase(model)
    add_tr_e_activation(model)
    add_e_relaxation(model)
    return model
