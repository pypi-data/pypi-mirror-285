"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import textwrap as text
import typing as h

from conf_ini_g.extension.python import SpecificationPath
from conf_ini_g.interface.storage.parameter import INI_UNIT_SEPARATOR
from conf_ini_g.interface.storage.section import INI_UNIT_SECTION
from conf_ini_g.phase.specification.parameter.main import parameter_t
from conf_ini_g.phase.specification.parameter.unit import unit_t
from conf_ini_g.phase.specification.parameter.value import MISSING_REQUIRED_VALUE
from conf_ini_g.phase.specification.section.controller import controller_t
from conf_ini_g.phase.specification.section.generic import section_t
from conf_ini_g.phase.specification.section.specific import (
    any_section_h,
    controlled_section_t,
    free_section_t,
    parameters_t,
)
from conf_ini_g.phase.specification.section.unit import IsUnitSection
from logger_36 import LOGGER
from rich.text import Text as text_t
from str_to_obj import ObjectFromStr
from str_to_obj.api.catalog import callable_t, choices_t
from str_to_obj.api.type import ANY_TYPE, type_t
from str_to_obj.interface.console import TypeAsRichStr
from str_to_obj.type.hint import any_hint_h


@d.dataclass(slots=True, repr=False, eq=False)
class config_t(list[any_section_h]):
    sections: d.InitVar[h.Sequence[section_t]]
    path: str = None

    relative_to_home: d.InitVar[bool] = True

    def __post_init__(
        self, sections: h.Sequence[section_t], relative_to_home: bool
    ) -> None:
        """
        Raising exceptions is adapted here since execution cannot proceed without a
        valid specification.
        """
        specific = []
        for section in sections:
            as_dict = dict(
                (_elm.name, getattr(section, _elm.name)) for _elm in d.fields(section)
            )
            if section.controller is None:
                del as_dict["controller"]
                del as_dict["alternatives"]
                section = free_section_t(**as_dict)
            else:
                section = controlled_section_t(**as_dict)
            specific.append(section)

        self.extend(specific)
        self.path = SpecificationPath(sections, relative_to_home=relative_to_home)

        for section in specific:
            if isinstance(section, free_section_t):
                continue

            controller = section.controller
            if self.GetController(controller).type is ANY_TYPE:
                choices = choices_t.NewAnnotatedType(section.controlling_values)
                self.GetController(controller).type = type_t.NewForHint(choices)

        _SignalIssues(self)
        LOGGER.CommitIssues(1)

    def AddUnitSection(self) -> None:
        """"""
        section = free_section_t(
            name=INI_UNIT_SECTION,
            definition="Unit definitions",
            description=f"Units can be used in any other section "
            f"to specify a parameter value as follows: "
            f"numerical_value{INI_UNIT_SEPARATOR}unit, e.g., 1.5'mm.",
            basic=True,
            optional=True,
            category=INI_UNIT_SECTION,
            is_growable=True,
        )
        self.append(section)

    def AddPluginParameter(
        self,
        section: str | any_section_h,
        name: str,
        /,
        *,
        definition: str = "Programmatic plugin parameter",
        description: str = "This parameter is not part of the specification. "
        'It was added programmatically in a "plugin" way.',
        basic: bool = True,
        stripe: any_hint_h | type_t = None,
        default: h.Any = MISSING_REQUIRED_VALUE,
        controlling_value: str = None,
    ) -> None:
        """
        See definition and description above.
        """
        if isinstance(section, str):
            section = self[section]

        parameter = parameter_t(
            name=name,
            definition=definition,
            description=description,
            basic=basic,
            type=stripe,
            default=default,
        )
        self._AddParameter(
            section, parameter, controlling_value, config_t.AddPluginParameter.__name__
        )

    def AddRuntimeParameter(
        self,
        section: str | any_section_h,
        name: str,
        value: str | float,
        /,
        *,
        controlling_value: str = None,
    ) -> parameter_t:
        """
        See definition and description below.
        The existence of such a method is justified by the fact that the parameter
        created can be a "normal" parameter or a unit depending on the section.

        value: float if unit.

        /!\\ Cannot deal with str values with units.
        """
        if isinstance(section, str):
            section = self[section]

        if IsUnitSection(section.name):
            parameter_or_unit_t = unit_t
            basic = True
            converted = value
            stripe = None  # Correctly set by the constructor.
        else:
            parameter_or_unit_t = parameter_t
            basic = section.basic
            converted, _ = ObjectFromStr(value)
            stripe = type(converted)
        definition = "Programmatic runtime parameter"
        description = (
            "This parameter is not part of the specification. "
            "It was added programmatically because it was found in the INI document, "
            "or passed as a command-line argument."
        )
        parameter = parameter_or_unit_t(
            name=name,
            definition=definition,
            description=description,
            basic=basic,
            type=stripe,
            default=converted,  # Just a trick to prevent error if basic is False.
        )
        self._AddParameter(
            section, parameter, controlling_value, config_t.AddRuntimeParameter.__name__
        )

        return parameter

    def _AddParameter(
        self,
        section: any_section_h,
        parameter: parameter_t,
        controlling_value: str,
        caller: str,
        /,
    ) -> None:
        """"""
        if not section.is_growable:
            raise RuntimeError(
                f"{section.name}.{parameter.name}: "
                f"Attempt to add an unspecified parameter to a section accepting none."
            )

        if isinstance(section, free_section_t):
            section.append(parameter)
            return

        controller = section.controller
        if controlling_value is None:
            raise ValueError(
                f"{caller}: A Controlling value must be passed for parameter "
                f"{section.name}.{parameter.name}."
            )

        if controller.primary_value is None:
            # controller_t is immutable, so it must be re-created.
            section.controller = controller_t(
                section=controller.section,
                parameter=controller.parameter,
                primary_value=controlling_value,
            )
            controller = section.controller
            section[controlling_value] = parameters_t((parameter,))
            should_update_controller_choices = True
        elif controlling_value in section:
            section[controlling_value].append(parameter)
            should_update_controller_choices = False
        else:
            section[controlling_value] = parameters_t((parameter,))
            should_update_controller_choices = True

        if should_update_controller_choices:
            nnts = self.GetController(controller).type.annotations
            if nnts.__len__() > 0:
                first_annotation = nnts[0]
            else:
                first_annotation = None
            if (first_annotation is None) or isinstance(first_annotation, choices_t):
                choices = choices_t.NewAnnotatedType(section.controlling_values)
                new_type = type_t.NewForHint(choices)
            else:  # Must be callable_t.
                callable_ = callable_t.NewAnnotatedType(
                    kind=first_annotation.kind,
                    catalog=section.controlling_values,
                    allow_external=first_annotation.allow_external,
                )
                new_type = type_t.NewForHint(callable_)
            self.GetController(controller).type = new_type

    @property
    def section_names(self) -> h.Sequence[str]:
        """"""
        return tuple(_sct.name for _sct in self)

    def GetController(self, controller: controller_t, /) -> parameter_t:
        """"""
        return self[controller.section][controller.parameter]

    def __contains__(self, key: str, /) -> bool:
        """"""
        return any(_elm.name == key for _elm in self)

    def __getitem__(self, key: str, /) -> any_section_h:
        """"""
        for section in self:
            if section.name == key:
                return section

        raise KeyError(f"{key}: Not a section of config.")

    def AsDict(self) -> dict[str, dict[str, h.Any]]:
        """"""
        return {_sct.name: _sct.AsDict() for _sct in self}

    def __str__(self) -> str:
        """"""
        return text_t.from_markup(self.__rich__()).plain

    def __rich__(self) -> str:
        """"""
        output = [
            TypeAsRichStr(self),
            f"    [blue]path[/]={self.path}" f"[yellow]:{type(self.path).__name__}[/]",
        ]

        for section in self:
            output.append(text.indent(section.__rich__(), "    "))

        return "\n".join(output)


def _SignalIssues(self: config_t, /) -> None:
    """"""
    with LOGGER.AddedContextLevel(f'Specification "{self.path}"'):
        if self.__len__() == 0:
            LOGGER.StageIssue(f"Empty specification")
            return

        names = self.section_names
        if names.__len__() > set(names).__len__():
            LOGGER.StageIssue("Repeated section names")

        for section in self:
            if isinstance(section, controlled_section_t):
                controller = section.controller
                if controller.section not in self:
                    LOGGER.StageIssue(
                        f"Unspecified parameter "
                        f'"{controller.section}.{controller.parameter}" declared as '
                        f'controller of section "{section.name}"'
                    )
                else:
                    controller_section = self[controller.section]
                    if isinstance(controller_section, controlled_section_t):
                        LOGGER.StageIssue(
                            f'Section "{controller.section}" of parameter '
                            f'"{controller.parameter}", which controls section '
                            f'"{section.name}", is itself controlled'
                        )
                    if controller.parameter not in controller_section:
                        LOGGER.StageIssue(
                            f"Unspecified parameter "
                            f'"{controller.section}.{controller.parameter}" declared '
                            f'as controller of section "{section.name}"'
                        )
                    else:
                        controller_section: free_section_t
                        controller_parameter = controller_section[controller.parameter]
                        if controller_parameter.optional:
                            LOGGER.StageIssue(
                                f"Optional parameter "
                                f'"{controller.section}.{controller.parameter}" '
                                f'declared as controller of section "{section.name}"'
                            )


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
