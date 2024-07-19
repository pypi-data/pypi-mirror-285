"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import itertools as ittl
import textwrap as text
import typing as h

from conf_ini_g.extension.string import AlignedOnSeparator
from conf_ini_g.phase.specification.base import base_t
from conf_ini_g.phase.specification.parameter.main import parameter_t
from conf_ini_g.phase.specification.section.controller import controller_t
from str_to_obj.interface.console import TypeAsRichStr


@d.dataclass(repr=False, eq=False)
class _section_t(base_t):
    """
    Default values only help complying with the constraint: no mandatory attributes
    after the default ones in base_t. In practice, they are mandatory.
    """

    category: str = ""
    optional: bool = False
    is_growable: bool = False

    def __rich_intro__(self) -> list[str]:
        """"""
        return [
            TypeAsRichStr(self),
            *text.indent(super().__rich__(), "    ").splitlines(),
            f"    [blue]Category[/]@=@{self.category}",
            f"    [blue]Optional[/]@=@{self.optional}",
            f"    [blue]Growable[/]@=@{self.is_growable}",
        ]

    @staticmethod
    def __rich_final__(elements: list[str], /) -> str:
        """"""
        elements = AlignedOnSeparator(elements, "@=@", " = ")
        return "\n".join(elements)


@d.dataclass(init=False, repr=False, eq=False)
class parameters_t(list[parameter_t]):
    def __contains__(self, key: str, /) -> bool:
        """"""
        return any(_elm.name == key for _elm in self)

    def __getitem__(self, key: str, /) -> parameter_t:
        """"""
        for parameter in self:
            if parameter.name == key:
                return parameter

        raise KeyError(f"{key}: Not a valid parameter.")


@d.dataclass(slots=True, repr=False, eq=False)
class free_section_t(_section_t, parameters_t):
    parameters: d.InitVar[list[parameter_t] | None] = None

    def __post_init__(self, parameters: list[parameter_t] | None) -> None:
        """"""
        if parameters is not None:
            self.extend(parameters)

    @property
    def all_parameters(self) -> parameters_t:
        """"""
        return self

    def ActiveParameters(self, _: str, /) -> parameters_t:
        """"""
        return self

    def AsDict(self) -> dict[str, h.Any]:
        """"""
        return {_prm.name: _prm.default for _prm in self if _prm.optional}

    def __rich__(self) -> str:
        """"""
        output = self.__rich_intro__()
        output.extend(text.indent(_prm.__rich__(), "    ") for _prm in self)
        return self.__rich_final__(output)


@d.dataclass(slots=True, repr=False, eq=False)
class controlled_section_t(_section_t, dict[str, parameters_t]):
    """
    Default value only help complying with the constraint: no mandatory attributes
    after the default ones in base_t. In practice, it is mandatory.
    """

    controller: controller_t = None
    parameters: d.InitVar[list[parameter_t] | None] = None
    alternatives: d.InitVar[dict[str, list[parameter_t]] | None] = None

    def __post_init__(
        self,
        parameters: list[parameter_t] | None,
        alternatives: dict[str, list[parameter_t]] | None,
    ) -> None:
        """"""
        if parameters is None:
            return

        self[self.controller.primary_value] = parameters_t(parameters)
        for key, value in alternatives.items():
            self[key] = parameters_t(value)

    @property
    def controlling_values(self) -> tuple[str, ...]:
        """"""
        return tuple(self.keys())

    @property
    def all_parameters(self) -> parameters_t:
        """"""
        return parameters_t(ittl.chain(*self.values()))

    def ActiveParameters(self, controlling_value: str, /) -> parameters_t:
        """"""
        if self.__len__() > 0:
            return self[controlling_value]

        # Despite being a controlled section, there can be no alternatives if the
        # section was specified empty. In a GUI context, the section would have
        # been populated programmatically. In a CLI context, it is not.
        return parameters_t()

    def AsDict(self) -> dict[str, h.Any]:
        """"""
        output = {}

        for value, parameters in self.items():
            output.update(
                {
                    (value, _prm.name): _prm.default
                    for _prm in parameters
                    if _prm.optional
                }
            )

        return output

    def __rich__(self) -> str:
        """"""
        output = [
            *self.__rich_intro__(),
            f"    [blue]Controller[/]@=@{self.controller}",
            "    Alternatives:",
        ]

        for ctl_name, parameters in self.items():
            output.append(f"        {ctl_name}")
            for parameter in parameters:
                output.append(text.indent(parameter.__rich__(), "            "))

        return self.__rich_final__(output)


any_section_h = free_section_t | controlled_section_t

"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.

This software is being developed by Eric Debreuve, a CNRS employee and
member of team Morpheme.
Team Morpheme is a joint team between Inria, CNRS, and UniCA.
It is hosted by the Centre Inria d'Université Côte d'Azur, Laboratory
I3S, and Laboratory iBV.

CNRS: https://www.cnrs.fr/index.php/en
Inria: https://www.inria.fr/en/
UniCA: https://univ-cotedazur.eu/
Centre Inria d'Université Côte d'Azur: https://www.inria.fr/en/centre/sophia/
I3S: https://www.i3s.unice.fr/en/
iBV: http://ibv.unice.fr/
Team Morpheme: https://team.inria.fr/morpheme/
"""
