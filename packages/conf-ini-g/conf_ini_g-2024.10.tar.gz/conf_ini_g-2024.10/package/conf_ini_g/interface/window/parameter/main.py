"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import types as t
import typing as h

from babelwidget.main import backend_t
from babelwidget.main import base_h as library_wgt_h
from babelwidget.main import dropdown_choice_h as dropdown_choice_wgt_h
from babelwidget.main import label_h as label_wgt_h
from babelwidget.main import text_line_h as text_line_wgt_h
from conf_ini_g.catalog.choices import choices_wgt_t
from conf_ini_g.catalog.directory import ValueWidgetTypeForType
from conf_ini_g.catalog.multitype import multitype_wgt_t
from conf_ini_g.interface.constant import TYPE_LABEL_WIDTH, TYPE_WIDGET_WIDTH
from conf_ini_g.interface.storage.parameter import INI_UNIT_SEPARATOR
from conf_ini_g.interface.window.generic import FormattedName
from conf_ini_g.interface.window.parameter.type import TypeSelector
from conf_ini_g.phase.specification.parameter.main import (
    parameter_t as parameter_spec_t,
)
from str_to_obj.api.type import hint_t, type_t


@d.dataclass(repr=False, eq=False)
class parameter_t:
    """
    In order to leave the section widget put the name, type, and input widgets of each parameter in columns,
    parameter_t is not a container widget. Instead, it just stores its component widgets for later addition to a layout.
    """

    spec_name: str
    name: label_wgt_h = d.field(init=False, default=None)
    type: label_wgt_h | dropdown_choice_wgt_h = d.field(init=False, default=None)
    value: library_wgt_h = d.field(init=False, default=None)
    unit: text_line_wgt_h = d.field(init=False, default=None)
    comment: str = d.field(init=False, default=None)

    @classmethod
    def NewForSpecification(
        cls,
        parameter_spec: parameter_spec_t,
        backend: backend_t,
        /,
    ) -> h.Self:
        """"""
        output = cls(spec_name=parameter_spec.name)

        formatted_name = FormattedName(parameter_spec.name, " ")
        comment = (
            f"{formatted_name}\n{parameter_spec.definition}.\n\n"
            f"{parameter_spec.description}."
        )
        output.name = backend.label_t(formatted_name)
        output.name.setToolTip(comment)
        output.comment = comment

        stripe = parameter_spec.type
        output.type, output.value = TypeAndValueWidgetsForType(stripe, backend)

        output.unit = backend.text_line_t()

        name_style = "padding-right: 2px;"
        if parameter_spec.optional:
            name_style += "color: gray;"
        output.name.setStyleSheet(name_style)
        output.type.setStyleSheet(name_style)

        return output

    def SetVisible(self, visible: bool, /) -> None:
        """"""
        self.name.setVisible(visible)
        self.type.setVisible(visible)
        self.value.library_wgt.setVisible(visible)
        if self.unit is not None:
            self.unit.setVisible(visible)

    def Text(self) -> str:
        """"""
        text = self.value.Text()
        if self.unit is None:
            return text

        unit = self.unit.Text()
        if unit.__len__() > 0:
            return f"{text}{INI_UNIT_SEPARATOR}{unit}"

        return text


def TypeAndValueWidgetsForType(
    stripe: type_t | hint_t, backend: backend_t, /
) -> tuple[type[library_wgt_h], type[library_wgt_h]]:
    """"""
    if (
        isinstance(stripe, hint_t)
        and (stripe.type is t.UnionType)
        and (stripe.literal_s is None)
    ):
        hint_options = stripe.elements
        type_wgt = TypeSelector(hint_options, backend)
        value_wgt = multitype_wgt_t.NewForHints(
            hint_options,
            type_wgt,
            backend,
        )
    else:
        template = stripe.template_as_str
        if (length := template.__len__()) > TYPE_LABEL_WIDTH:
            shortened = "-" + template[(length - TYPE_LABEL_WIDTH + 1) :]
        else:
            shortened = template
        type_wgt = backend.label_t(shortened)
        type_wgt.setToolTip(template)
        if stripe.literal_s is None:
            widget_type = ValueWidgetTypeForType(stripe)
        else:
            widget_type = choices_wgt_t
        value_wgt = widget_type.NewForSpecification(
            stripe,
            backend,
        )

    type_wgt.setFixedWidth(TYPE_WIDGET_WIDTH)

    return type_wgt, value_wgt


@d.dataclass(init=False, repr=False, eq=False)
class parameters_t(list[parameter_t]):
    def __contains__(self, key: str, /) -> bool:
        """"""
        return any(_elm.spec_name == key for _elm in self)

    def __getitem__(self, key: str, /) -> parameter_t:
        """"""
        for parameter in self:
            if parameter.spec_name == key:
                return parameter

        raise KeyError(f"{key}: Not a valid parameter.")


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
