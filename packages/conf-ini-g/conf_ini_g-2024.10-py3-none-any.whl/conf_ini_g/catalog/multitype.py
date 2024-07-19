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
from babelwidget.main import stack_h as stack_wgt_h
from conf_ini_g.catalog.directory import ValueWidgetTypeForType
from str_to_obj.api.type import hint_t


@d.dataclass(repr=False, eq=False)
class multitype_wgt_t:
    hints: h.Sequence[hint_t]
    library_wgt: stack_wgt_h
    type_selection_wgt: dropdown_choice_wgt_h
    values: tuple[library_wgt_h, ...] | None = d.field(init=False, default=None)

    @classmethod
    def NewForHints(
        cls,
        hints: h.Sequence[hint_t],
        controller: dropdown_choice_wgt_h,
        backend: backend_t,
        /,
    ) -> h.Self:
        """"""
        value_stack = backend.stack_t()
        controller.SetFunction(value_stack.setCurrentIndex)

        output = cls(
            hints=hints, library_wgt=value_stack, type_selection_wgt=controller
        )

        values = []
        for t_idx, hint in enumerate(hints):
            widget_type = ValueWidgetTypeForType(hint)
            value_wgt = widget_type.NewForSpecification(
                hint,
                backend,
            )
            values.append(value_wgt)
            value_stack.addWidget(value_wgt.library_wgt)
        output.values = tuple(values)

        value_stack.setSizePolicy(backend.SIZE_EXPANDING, backend.SIZE_FIXED)

        return output

    def Assign(self, value: h.Any, stripe: h.Any, /) -> None:
        """"""
        type_idx = 0
        for t_idx, hint in enumerate(self.hints):
            if isinstance(value, hint.type):
                type_idx = t_idx
        self.type_selection_wgt.setCurrentIndex(type_idx)
        self.values[type_idx].Assign(value, stripe)

    def Text(self) -> str:
        """"""
        return self.values[self.type_selection_wgt.currentIndex()].Text()


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
