"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h

from conf_ini_g.interface.storage.parameter import INI_COMMENT_MARKER
from conf_ini_g.interface.storage.section import INI_UNIT_SECTION
from conf_ini_g.phase.specification.config.main import config_t as specification_t
from conf_ini_g.phase.specification.section.specific import (
    controlled_section_t,
    free_section_t,
)
from conf_ini_g.phase.typed.parameter.main import TypedValue
from conf_ini_g.phase.typed.parameter.unit import ConvertedValue
from conf_ini_g.phase.typed.section.units import InitialUnits, UpdateUnits
from conf_ini_g.phase.untyped.config import ini_config_h
from conf_ini_g.phase.untyped.parameter import ValueUnitAndComment
from str_to_obj import INVALID_VALUE

# With interpreted values, and possibly units.
typed_config_h = dict[str, dict[str, h.Any]]


def TypedFromUntyped(
    ini: ini_config_h,
    cmd_line: ini_config_h | None,
    specification: specification_t,
    /,
) -> tuple[
    typed_config_h,
    dict[tuple[str, str], tuple[str, float]],
    dict[tuple[str, str], str],
    list[str],
]:
    """
    Units are not consumed, but returned.
    """
    output = {}
    output_units = {}
    output_comments = {}

    if cmd_line is None:
        configs = (ini,)
    else:
        configs = (ini, cmd_line)
    issues = []
    units = InitialUnits(specification)
    for config in configs:
        for sct_name, parameters in config.items():
            if sct_name not in output:
                output[sct_name] = {}

            if (section_is_units := (sct_name == INI_UNIT_SECTION)) and (
                INI_UNIT_SECTION not in specification
            ):
                specification.AddUnitSection()
            section_spec = specification[sct_name]
            for prm_name, value in parameters.items():
                if section_is_units:
                    value, local_issues = UpdateUnits(units, prm_name, value)
                    if local_issues.__len__() > 0:
                        issues.extend(local_issues)
                        continue
                if isinstance(section_spec, free_section_t) and (
                    prm_name not in section_spec
                ):
                    parameter_spec = specification.AddRuntimeParameter(
                        sct_name, prm_name, value
                    )
                    value = parameter_spec.default
                output[sct_name][prm_name] = value

    # Everything being set, default parameters of controlled sections can be added.
    for config in configs:
        for sct_name, parameters in config.items():
            section_spec = specification[sct_name]
            for prm_name, value in parameters.items():
                if isinstance(section_spec, controlled_section_t):
                    controller = section_spec.controller
                    controlling_value = output[controller.section][controller.parameter]
                    if prm_name not in section_spec[controlling_value]:
                        parameter_spec = specification.AddRuntimeParameter(
                            sct_name,
                            prm_name,
                            value,
                            controlling_value=controlling_value,
                        )
                        output[sct_name][prm_name] = parameter_spec.default

    for section in specification:
        if section.name not in output:
            output[section.name] = {}

        if isinstance(section, free_section_t):
            parameters = section
        else:
            controller = section.controller
            controlling_value = output[controller.section][controller.parameter]
            parameters = section.ActiveParameters(controlling_value)

        output_section = output[section.name]
        for parameter in parameters:
            if parameter.optional and (parameter.name not in output_section):
                output[section.name][parameter.name] = parameter.default

    for sct_name, parameters in output.items():
        if sct_name == INI_UNIT_SECTION:
            continue

        section_spec = specification[sct_name]
        for prm_name, value in parameters.items():
            if isinstance(value, str):
                value, unit, comment = ValueUnitAndComment(value, INI_COMMENT_MARKER)
                if not ((unit is None) or (unit in units)):
                    issues.append(f"/{sct_name}.{prm_name}/ Unknown unit: {unit}.")
                    continue

                if isinstance(section_spec, free_section_t):
                    parameter_spec = section_spec[prm_name]
                else:
                    controller = section_spec.controller
                    controlling_value = output[controller.section][controller.parameter]
                    parameter_spec = section_spec[controlling_value][prm_name]

                value, current_issues = TypedValue(value, parameter_spec.type)
                if current_issues.__len__() > 0:
                    issues.extend(
                        f"/{sct_name}.{prm_name}/ {_iss}" for _iss in current_issues
                    )
                    continue
                output[sct_name][prm_name] = value
                if unit is not None:
                    output_units[(sct_name, prm_name)] = (unit, units[unit])
                if comment is not None:
                    output_comments[(sct_name, prm_name)] = comment

    return output, output_units, output_comments, issues


def WithConsumedUnits(
    config: typed_config_h, units: dict[tuple[str, str], tuple[str, float]], /
) -> tuple[typed_config_h, list[str]]:
    """"""
    output = {_key: dict(_vle) for _key, _vle in config.items()}
    issues = []

    for sct_name, parameters in output.items():
        for prm_name, value in parameters.items():
            unit = units.get((sct_name, prm_name), None)
            if unit is not None:
                converted, unconverted = ConvertedValue(
                    output[sct_name][prm_name], unit[1]
                )
                if unconverted.__len__() > 0:
                    converted = INVALID_VALUE
                    unconverted = ", ".join(unconverted)
                    issues.append(
                        f"{unconverted}: Value(s) do(es) not support unit conversion."
                    )

                output[sct_name][prm_name] = converted

    return output, issues


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
