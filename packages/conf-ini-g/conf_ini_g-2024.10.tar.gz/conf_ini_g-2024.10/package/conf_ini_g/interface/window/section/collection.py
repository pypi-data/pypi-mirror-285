"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h

from babelwidget.main import backend_t, scroll_container_h
from babelwidget.main import tabs_h as tabs_wgt_h
from conf_ini_g.interface.window.section.main import (
    any_section_h,
    controlled_section_t,
    free_section_t,
)
from conf_ini_g.phase.specification.config.main import config_t as config_spec_t
from conf_ini_g.phase.specification.section.specific import (
    controlled_section_t as controlled_section_spec_t,
)
from conf_ini_g.phase.specification.section.specific import (
    free_section_t as free_section_spec_t,
)


def SectionsAndCategories(
    specification: config_spec_t,
    category_selector: scroll_container_h | tabs_wgt_h | None,
    backend: backend_t,
    /,
) -> tuple[
    list[any_section_h],
    h.Sequence[tuple[controlled_section_t, controlled_section_spec_t]],
    scroll_container_h | tabs_wgt_h,
]:
    """"""
    sections = []
    controlled_sections = []
    categories = {}

    # --- Sections and categories
    for section_spec in specification:
        if isinstance(section_spec, free_section_spec_t):
            section = free_section_t.NewForSpecification(section_spec, backend)
        else:
            section = controlled_section_t.NewForSpecification(
                section_spec,
                section_spec.controller,
                backend,
            )
            if section is not None:
                controlled_sections.append((section, section_spec))
        if section is None:
            continue

        sections.append(section)

        if (category := section_spec.category) not in categories:
            contents = backend.base_t()
            scroll_area = backend.scroll_container_t.NewForWidget(contents)
            layout = backend.vbox_lyt_t()
            contents.setLayout(layout)
            categories[category] = (layout, scroll_area)

        layout = categories[category][0]
        layout.addWidget(section.library_wgt)

    # --- Section dispatch into categories
    missing_category_selector = category_selector is None
    if categories.__len__() > 1:
        if missing_category_selector:
            category_selector = backend.tabs_t()
        for category, (_, scroll_area) in categories.items():
            category_selector.addTab(scroll_area, category)
    elif missing_category_selector:
        category = tuple(categories.keys())[0]
        category_selector = categories[category][1]

    return sections, controlled_sections, category_selector


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
