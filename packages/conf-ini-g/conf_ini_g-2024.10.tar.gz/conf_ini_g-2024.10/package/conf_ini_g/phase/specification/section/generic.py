"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d

from conf_ini_g.phase.specification.base import base_t
from conf_ini_g.phase.specification.parameter.main import parameter_t
from conf_ini_g.phase.specification.section.controller import controller_t
from logger_36 import LOGGER


@d.dataclass(repr=False, eq=False)
class section_t(base_t):
    category: str = "Main"
    optional: bool = False
    is_growable: bool = False  # True by default if no parameters are specified.
    parameters: list[parameter_t] | None = None
    controller: controller_t = None
    alternatives: dict[str, list[parameter_t]] = None

    def __post_init__(self) -> None:
        """"""
        if self.parameters is None:
            self.is_growable = True

        _SignalIssues(self)

    @property
    def controlling_values(self) -> tuple[str, ...]:
        """
        Call only on controlled sections.
        """
        if self.controller.primary_value is None:
            # The controlling values are not mentioned in the specification. They will
            # be set programmatically later on.
            return ()

        if self.alternatives is None:
            # The controlling values are not mentioned in the specification. They are
            # being set programmatically.
            return (self.controller.primary_value,)

        return (self.controller.primary_value,) + tuple(self.alternatives.keys())


def _SignalIssues(self) -> None:
    """"""
    with LOGGER.AddedContextLevel(
        f'Specification of {type(self).__name__} "{self.name}"'
    ):
        if self.parameters is not None:
            valid_name_sets = [tuple(_prm.name for _prm in self.parameters)]
            if self.alternatives is not None:
                for parameters in self.alternatives.values():
                    valid_name_sets.append(tuple(_prm.name for _prm in parameters))
            for valid_name_set in valid_name_sets:
                if valid_name_set.__len__() > set(valid_name_set).__len__():
                    LOGGER.StageIssue(
                        "Repeated parameter names (possibly in alternatives)"
                    )

        basic = self.basic
        optional = self.optional

        if not (basic or optional):
            LOGGER.StageIssue("Section is not basic but not optional")

        if (
            (self.controller is None)
            and (not optional)
            and ((self.parameters is None) or (self.parameters.__len__() == 0))
        ):
            LOGGER.StageIssue("Empty mandatory section")

        if self.parameters is not None:
            n_parameters = 0
            n_basic_prms = 0
            for parameter in self.parameters:
                n_parameters += 1
                if parameter.basic:
                    n_basic_prms += 1

                if parameter.basic and not basic:
                    LOGGER.StageIssue(
                        f'Basic parameter "{parameter.name}" in advanced section'
                    )
                if optional and not parameter.optional:
                    LOGGER.StageIssue(
                        f'Mandatory parameter "{parameter.name}" in optional section'
                    )

            if (n_parameters == 0) and not self.is_growable:
                LOGGER.StageIssue("Empty section not accepting runtime parameters")
            if basic and (n_parameters > 0) and (n_basic_prms == 0):
                LOGGER.StageIssue("Basic section without any basic parameters")

        if self.controller is None:
            if self.alternatives is not None:
                LOGGER.StageIssue("Uncontrolled section with alternatives")
        else:
            if self.controller.section == self.name:
                LOGGER.StageIssue("Section controlled by itself")
            controlling_values = self.controlling_values
            if controlling_values.__len__() > set(controlling_values).__len__():
                LOGGER.StageIssue(
                    "Controlled section with duplicated controlling values"
                )
            if self.parameters is not None:
                for parameter in self.parameters:
                    if not parameter.optional:
                        LOGGER.StageIssue(
                            f'Mandatory parameter "{parameter.name}" in '
                            f"controlled section"
                        )

            if self.controller.primary_value is None:
                if self.alternatives is not None:
                    LOGGER.StageIssue("Controlled section without primary value")
                # else: This will be set programmatically later on.
            elif self.alternatives is None:
                LOGGER.StageIssue("Controlled section without alternatives")


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
