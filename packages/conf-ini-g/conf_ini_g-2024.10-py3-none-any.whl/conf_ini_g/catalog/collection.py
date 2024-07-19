"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h

from babelwidget.main import backend_t
from babelwidget.main import base_h as library_wgt_h
from babelwidget.main import dropdown_choice_h as dropdown_choice_wgt_h
from babelwidget.main import text_line_h as text_line_wgt_h
from conf_ini_g.interface.window.parameter.value import value_wgt_a
from str_to_obj.api.catalog import collection_t
from str_to_obj.api.type import type_t

VALUE_FOR_NONE = ()

_DELIMITERS_TYPES = (tuple, list, set)
_DELIMITERS_VALUES = ("()", "[]", "{}")
_DELIMITERS = dict(zip(_DELIMITERS_TYPES, _DELIMITERS_VALUES))


@d.dataclass(repr=False, eq=False)
class collection_wgt_t(value_wgt_a):
    """
    Cannot use slots (weak reference issue).
    """

    ENTRY_ANY: h.ClassVar[str] = "any"
    ENTRIES: h.ClassVar[tuple[str, ...]] = ("1", "2", "3", "4", "5", "6", ENTRY_ANY)

    library_wgt: library_wgt_h
    delimiters: h.Literal["()", "[]", "{}"] = d.field(
        init=False, default=_DELIMITERS[tuple]
    )
    length_selector: dropdown_choice_wgt_h = d.field(init=False, default=None)
    components: tuple[text_line_wgt_h, ...] = d.field(init=False, default=None)

    @classmethod
    def NewForSpecification(
        cls,
        stripe: type_t | collection_t | None,
        backend: backend_t,
        /,
    ) -> h.Self:
        """
        If stripe does not contain the necessary details, a simple free-text input
        widget is used. If the value is not coherent with the details (which should not
        happen if stripe contains the necessary details and the value has been
        validated), a choice with the length of the value is added, with an exclamation
        point.
        """
        components, length_selector = cls._SetUpComponents(stripe, backend)
        output = cls(components, "textChanged", backend, library_wgt=backend.base_t())
        length_selector.SetFunction(output._AccountForLengthSwitch)
        output.components = components
        output.length_selector = length_selector

        layout = backend.hbox_lyt_t()
        layout.setContentsMargins(0, 0, 0, 0)
        if output.length_selector is not None:
            layout.addWidget(output.length_selector)
        for component in output.components:
            layout.addWidget(component)
        output.library_wgt.setLayout(layout)

        return output

    def _AccountForLengthSwitch(self, new_index: int, /) -> None:
        """"""
        new_length = self.length_selector.ItemAt(new_index)
        if new_length == self.__class__.ENTRY_ANY:
            new_length = 1
        elif new_length.endswith("!"):
            new_length = int(new_length[:-1])
        else:
            new_length = int(new_length)
        _AdjustComponentVisibility(self.components, new_length)

    @classmethod
    def _SetUpComponents(
        cls, stripe: type_t | collection_t | None, backend: backend_t, /
    ) -> tuple[tuple[text_line_wgt_h, ...], dropdown_choice_wgt_h | None]:
        """"""
        if stripe is None:
            annotation = None
        elif isinstance(stripe, type_t):
            annotation = stripe.FirstAnnotationWithType(collection_t)
            if annotation is None:
                annotation = collection_t.NewForType(stripe)
        else:
            annotation = stripe

        if (annotation is None) or (
            (lengths := annotation.lengths) == collection_t.ANY_LENGTH
        ):
            entries = cls.ENTRIES
            max_entry = int(cls.ENTRIES[-2])
        else:
            entries = tuple(map(str, lengths))
            max_entry = lengths[-1]

        if max_entry is None:
            components = (backend.text_line_t(parent=None),)
        else:
            components = tuple(
                backend.text_line_t(parent=None) for _ in range(max_entry)
            )

        if entries.__len__() > 1:
            _AdjustComponentVisibility(components, 1)

            length_selector = backend.dropdown_choice_t()
            for entry in entries:
                length_selector.addItem(entry)
            length_selector.setCurrentText(cls.ENTRY_ANY)
        else:
            length_selector = None

        return components, length_selector

    def Assign(
        self, value: tuple | None, stripe: type_t | collection_t | None, /
    ) -> None:
        """"""
        if value is None:
            value = VALUE_FOR_NONE
        length = value.__len__()

        delimiters = _DELIMITERS.get(type(value), None)
        if delimiters is None:
            raise TypeError(f"{type(value).__name__}: Unhandled sequence type.")
        self.delimiters = delimiters

        if (n_components := self.components.__len__()) == 1:
            value_as_str = str(value)[1:-1] if length > 0 else ""
            if length == 1:
                value_as_str = value_as_str[:-1]
            self.components[0].setText(value_as_str)
        elif length > n_components:
            if (self.length_selector is not None) and (
                self.length_selector.itemText(self.length_selector.count() - 1)
                == collection_t.ANY_LENGTH
            ):
                value_as_str = str(value)[1:-1] if length > 0 else ""
                self.components[0].setText(value_as_str)
                self.length_selector.setCurrentText(collection_t.ANY_LENGTH)
            else:
                raise ValueError(
                    f"Value {value} has too many elements "
                    f"for widget with at most {n_components} component(s)."
                )
        else:
            for widget, element in zip(self.components[:length], value):
                widget.setText(str(element))
            _AdjustComponentVisibility(self.components, length)
            if self.length_selector is not None:
                self.length_selector.setCurrentText(str(length))

    def Text(self) -> str:
        """"""
        contents = []
        for component in self.components:
            # Do not use "visible" here since setting visible does not really set the
            # property until it is actually shown. The documentation explains about
            # ancestors being visible or not, but it was not clear that the property is
            # apparently not effective immediately.
            if not component.isEnabled():
                break
            component_as_str = component.Text()
            if component_as_str == "":
                break
            contents.append(component_as_str)

        if contents.__len__() == 0:
            return self.delimiters
        elif contents.__len__() == 1:
            if self.delimiters[0] == "(":
                return f"({contents[0]},)"
            else:
                return f"[{contents[0]}]"
        else:
            return self.delimiters[0] + ", ".join(contents) + self.delimiters[1]


def _AdjustComponentVisibility(
    components: h.Sequence[text_line_wgt_h], length: int, /
) -> None:
    """"""
    for c_idx, component in enumerate(components):
        if c_idx < length:
            component.setVisible(True)
            component.setEnabled(True)
        else:
            component.setVisible(False)
            component.setEnabled(False)


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
