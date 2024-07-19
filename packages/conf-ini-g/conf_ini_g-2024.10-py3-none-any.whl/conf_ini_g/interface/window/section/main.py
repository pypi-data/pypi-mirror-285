"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import itertools as ittl
import typing as h

from babelwidget.main import backend_t, grid_lyt_h
from babelwidget.main import group_h as group_wgt_h
from babelwidget.main import label_h as label_wgt_h
from babelwidget.main import stack_h as stack_wgt_h
from conf_ini_g.interface.storage.section import INI_UNIT_SECTION
from conf_ini_g.interface.window.generic import FormattedName
from conf_ini_g.interface.window.parameter.main import parameter_t, parameters_t
from conf_ini_g.phase.specification.parameter.main import (
    parameter_t as parameter_spec_t,
)
from conf_ini_g.phase.specification.section.controller import controller_t
from conf_ini_g.phase.specification.section.specific import (
    any_section_h as any_section_spec_h,
)
from conf_ini_g.phase.specification.section.specific import (
    controlled_section_t as controlled_section_spec_t,
)
from conf_ini_g.phase.specification.section.specific import (
    free_section_t as free_section_spec_t,
)


@d.dataclass(repr=False, eq=False)
class _section_t:  # Cannot be abstracted.
    HEADER_NAMES: h.ClassVar[tuple[str]] = (
        "Parameter",
        "Type(s)",
        "Value",
        "Unit",
    )
    HEADER_STYLE: h.ClassVar[str] = "background-color: darkgray; padding-left: 5px;"

    spec_name: str
    formatted_name: str
    library_wgt: group_wgt_h

    @classmethod
    def NewWithName(
        cls, name: str, backend: backend_t, /, *, controller: controller_t = None
    ) -> h.Self:
        """"""
        if controller is None:
            controller = ""
        else:
            controller = (
                f" ⮜ {FormattedName(controller.section, ' ')}."
                f"{FormattedName(controller.parameter, ' ')}"
            )
        formatted_name = FormattedName(name, " ") + controller

        output = cls(
            spec_name=name, formatted_name=formatted_name, library_wgt=backend.group_t()
        )
        output.library_wgt.setTitle(formatted_name)

        return output

    @classmethod
    def Headers(cls, backend: backend_t, /) -> h.Sequence[label_wgt_h]:
        """"""
        output = []

        for text in cls.HEADER_NAMES:
            header = backend.label_t(f'<font color="blue">{text}</font>')
            header.setStyleSheet(cls.HEADER_STYLE)
            output.append(header)

        return output

    @property
    def active_parameters(self) -> h.Sequence[parameter_t]:
        """"""
        raise NotImplementedError

    def AsINI(self) -> dict[str, str]:
        """"""
        return {_elm.spec_name: _elm.Text() for _elm in self.active_parameters}


@d.dataclass(repr=False, eq=False)
class free_section_t(_section_t, parameters_t):
    @classmethod
    def NewForSpecification(
        cls,
        section_spec: free_section_spec_t,
        backend: backend_t,
        /,
    ) -> h.Self | None:
        """"""
        output = cls.NewWithName(section_spec.name, backend)

        parameters, _, layout = _SectionParameters(
            section_spec, section_spec.name == INI_UNIT_SECTION, backend
        )
        if parameters.__len__() == 0:
            return None

        output.extend(parameters)

        for h_idx, header in enumerate(cls.Headers(backend)):
            layout.addWidget(header, 0, h_idx)
        output.library_wgt.setLayout(layout)

        return output

    @property
    def all_parameters(self) -> parameters_t:
        """"""
        return self

    @property
    def active_parameters(self) -> parameters_t:
        """"""
        return self


@d.dataclass(repr=False, eq=False)
class controlled_section_t(_section_t, dict[str, parameters_t]):
    controlling_values: list[str] = d.field(init=False, default=None)
    page_stack: stack_wgt_h = d.field(init=False, default=None)

    @classmethod
    def NewForSpecification(
        cls,
        section_spec: controlled_section_spec_t,
        controller: controller_t,
        backend: backend_t,
        /,
    ) -> h.Self | None:
        """"""
        output = cls.NewWithName(section_spec.name, backend, controller=controller)

        controlling_values = []
        page_stack = backend.stack_t()
        for controlling_value, parameter_specs in section_spec.items():
            parameters, _, layout = _SectionParameters(parameter_specs, False, backend)
            if parameters.__len__() == 0:
                continue

            controlling_values.append(controlling_value)
            output[controlling_value] = parameters_t(parameters)

            for h_idx, header in enumerate(cls.Headers(backend)):
                layout.addWidget(header, 0, h_idx)
            page = backend.base_t()
            page.setLayout(layout)
            page_stack.addWidget(page)

        if output.__len__() == 0:
            return None

        output.controlling_values = controlling_values
        output.page_stack = page_stack

        # Curiously, the stacked widget cannot be simply declared as child of instance;
        # This must be specified through a layout.
        layout = backend.hbox_lyt_t()
        layout.addWidget(page_stack)
        layout.setContentsMargins(0, 0, 0, 0)
        output.library_wgt.setLayout(layout)

        return output

    @property
    def all_parameters(self) -> parameters_t:
        """"""
        return parameters_t(ittl.chain(*self.values()))

    @property
    def active_parameters(self) -> parameters_t:
        """"""
        return self[self.controlling_values[self.page_stack.currentIndex()]]


any_section_h = free_section_t | controlled_section_t


def _SectionParameters(
    specifications: any_section_spec_h | h.Iterator[parameter_spec_t],
    section_is_unit: bool,
    backend: backend_t,
    /,
) -> tuple[h.Sequence[parameter_t], h.Sequence[str], grid_lyt_h]:
    """"""
    parameters = []
    parameter_names = []

    layout = backend.grid_lyt_t()
    layout.setAlignment(backend.ALIGNED_TOP)
    layout.setColumnStretch(0, 4)
    layout.setColumnStretch(1, 1)
    layout.setColumnStretch(2, 8)
    layout.setColumnStretch(3, 1)
    layout.setContentsMargins(0, 0, 0, 0)

    for row, parameter_spec in enumerate(specifications, start=1):
        parameter = parameter_t.NewForSpecification(parameter_spec, backend)
        parameters.append(parameter)
        parameter_names.append(parameter_spec.name)

        layout.addWidget(parameter.name, row, 0, alignment=backend.ALIGNED_RIGHT)
        layout.addWidget(parameter.type, row, 1)
        layout.addWidget(parameter.value.library_wgt, row, 2, 1, 2 - 1)
        if not (section_is_unit or (parameter.unit is None)):
            layout.addWidget(parameter.unit, row, 3)

    return parameters, parameter_names, layout


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
