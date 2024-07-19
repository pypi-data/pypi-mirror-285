"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import configparser as cfpr
import sys as sstm

from conf_ini_g.extension.path import ValidateOutputPath, any_path_h, path_t
from conf_ini_g.interface.storage.parameter import (
    INI_COMMENT_MARKER,
    INI_VALUE_ASSIGNMENT,
)
from conf_ini_g.phase.generic.config import AsStr, any_dict_config_h
from conf_ini_g.phase.specification.parameter.main import parameter_t
from conf_ini_g.phase.specification.section.generic import section_t
from conf_ini_g.phase.specification.section.unit import IsUnitSection
from conf_ini_g.phase.untyped.config import ini_config_h
from str_to_obj import ObjectFromStr

_SECTIONS = "SECTIONS"


def DraftSpecificationFromINIDocument(path: any_path_h, /) -> str | None:
    """"""
    ini_config = INIConfig(path)
    if ini_config is None:
        return None

    sections = []
    for section_name, parameters in ini_config.items():
        # possibly_fuzzy=True: in case the raw config is not valid in that respect
        if IsUnitSection(section_name, possibly_fuzzy=True):
            continue

        parameters_as_lst = []
        for parameter_name, value_as_str in parameters.items():
            value, _ = ObjectFromStr(value_as_str)
            parameter = (
                f"{parameter_t.__name__}(\n"
                f'                name="{parameter_name}",\n'
                f"                type={type(value).__name__},\n"
                f"            )"
            )
            parameters_as_lst.append(parameter)

        parameters_as_str = ",\n            ".join(parameters_as_lst)
        section = (
            f"    {section_t.__name__}(\n"
            f'        name="{section_name}",\n'
            f"        parameters=[\n"
            f"            {parameters_as_str}\n"
            f"        ]\n"
            f"    )"
        )
        sections.append(section)

    imports = (
        f"# To use this specification file:\n"
        f"#     1. import the object {_SECTIONS}\n"
        f"#     2. instantiate a conf_ini_g.specification.config.config_t from it\n"
        f"from conf_ini_g.specification.parameter.main "
        f"import {parameter_t.__name__}\n"
        f"from conf_ini_g.specification.section.main import {section_t.__name__}\n"
    )

    return imports + f"\n{_SECTIONS} = (\n" + ",\n".join(sections) + ",\n)\n"


def INIConfig(ini_path: any_path_h | None, /) -> ini_config_h:
    """"""
    if ini_path is None:
        ini_config = {}
    else:
        ini_config = cfpr.ConfigParser(
            delimiters=INI_VALUE_ASSIGNMENT,
            comment_prefixes=INI_COMMENT_MARKER,
            empty_lines_in_values=False,
            interpolation=None,
        )
        ini_config.optionxform = lambda option: option
        # Returns DEFAULT <Section: DEFAULT> if path does not exist or is a folder.
        ini_config.read(ini_path, encoding=sstm.getfilesystemencoding())

    output = {
        section: {parameter: value for parameter, value in parameters.items()}
        for section, parameters in ini_config.items()
        if section != cfpr.DEFAULTSECT
    }

    return output


def SaveConfigToINIDocument(
    config: any_dict_config_h,
    path: any_path_h,
    /,
    *,
    should_overwrite: bool = False,
    should_raise_on_error: bool = False,
) -> list[str]:
    """"""
    path = path_t(path)
    issues = ValidateOutputPath(
        path,
        should_overwrite=should_overwrite,
        should_raise_on_error=should_raise_on_error,
    )
    if issues.__len__() > 0:
        return issues

    encoding = sstm.getfilesystemencoding()

    with path.open("w", encoding=encoding) as ini_writer:
        print(AsStr(config), file=ini_writer)
        print(f"", file=ini_writer)

    return []


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
