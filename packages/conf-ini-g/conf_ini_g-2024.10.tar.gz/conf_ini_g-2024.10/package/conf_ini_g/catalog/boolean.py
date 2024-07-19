"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h

from babelwidget.main import backend_t
from babelwidget.main import base_h as library_wgt_h
from babelwidget.main import radio_choice_h as radio_choice_wgt_h
from conf_ini_g.interface.window.parameter.value import value_wgt_a
from str_to_obj.api.catalog import boolean_t
from str_to_obj.api.type import type_t


@d.dataclass(repr=False, eq=False)
class boolean_wgt_t(value_wgt_a):
    library_wgt: library_wgt_h
    true_btn: radio_choice_wgt_h | None = d.field(init=False, default=None)
    false_btn: radio_choice_wgt_h | None = d.field(init=False, default=None)

    @classmethod
    def NewForSpecification(
        cls,
        stripe: type_t | boolean_t | None,
        backend: backend_t,
        /,
    ) -> h.Self:
        """"""
        if stripe is None:
            annotation = None
        elif isinstance(stripe, type_t):
            annotation = stripe.FirstAnnotationWithType(boolean_t)
        else:
            annotation = stripe
        if annotation is None:
            labels = ("True", "False")
        else:
            labels = getattr(annotation.mode, "value", None)

        true_btn = backend.radio_choice_t(labels[0])
        false_btn = backend.radio_choice_t(labels[1])

        output = cls(true_btn, "released", backend, library_wgt=backend.base_t())
        output.true_btn = true_btn
        output.false_btn = false_btn

        layout = backend.hbox_lyt_t()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(true_btn)
        layout.addWidget(false_btn)
        output.library_wgt.setLayout(layout)

        return output

    def Assign(self, value: bool, _: h.Any, /) -> None:
        """"""
        self.true_btn.setChecked(value)
        self.false_btn.setChecked(not value)

    def Text(self) -> str:
        """"""
        return str(self.true_btn.isChecked())


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
