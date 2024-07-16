from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modelbase.ode import Model


def rename_parameter(m: Model, old_name: str, new_name: str) -> None:
    """This does not update any references to this parameter!"""
    value = m.parameters[old_name]
    m.remove_parameter(old_name)
    m.add_parameter(new_name, value)


def unused_parameters(self: Model) -> set[str]:
    args = set()
    for der_par in self.derived_parameters.values():
        args.update(der_par["parameters"])

    for module in self.algebraic_modules.values():
        args.update(module.args)

    for rate in self.rates.values():
        args.update(rate.args)

    for stoich_dict in self.derived_stoichiometries.values():
        for der_stoich in stoich_dict.values():
            args.update(der_stoich.args)

    return set(self.parameters).difference(args)


def unused_derived_parameters(self: Model) -> set[str]:
    args = set()
    for der_par in self.derived_parameters.values():
        args.update(der_par["parameters"])

    for module in self.algebraic_modules.values():
        args.update(module.args)

    for rate in self.rates.values():
        args.update(rate.args)

    for stoich_dict in self.derived_stoichiometries.values():
        for der_stoich in stoich_dict.values():
            args.update(der_stoich.args)

    return set(self.derived_parameters).difference(args)


def unused_compounds(self: Model) -> set[str]:
    used = set(self.stoichiometries_by_compounds)
    return set(self.compounds).difference(used)


def unused_derived_compounds(self: Model) -> set[str]:
    args = set()
    for module in self.algebraic_modules.values():
        args.update(module.args)

    for rate in self.rates.values():
        args.update(rate.args)

    return set(self.derived_compounds).difference(args)


def unused_ids(self: Model) -> set[str]:
    args = set()
    for der_par in self.derived_parameters.values():
        args.update(der_par["parameters"])

    for module in self.algebraic_modules.values():
        args.update(module.args)

    for rate in self.rates.values():
        args.update(rate.args)

    for stoich_dict in self.derived_stoichiometries.values():
        for der_stoich in stoich_dict.values():
            args.update(der_stoich.args)

    for readout in self.readouts.values():
        args.update(readout.args)

    return set(self._ids).difference(args)
