"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

from conf_ini_g.interface.storage.parameter import INI_UNIT_SEPARATOR


def ValueUnitAndComment(
    value_w_unit_w_comment: str,
    comment_marker: str,
    /,
) -> tuple[str, str | None, str | None]:
    """"""
    value_w_unit, comment = _Pieces(value_w_unit_w_comment, comment_marker)
    if (comment is not None) and (comment.__len__() == 0):
        comment = None

    value_as_str, unit = _Pieces(value_w_unit, INI_UNIT_SEPARATOR, from_left=False)
    # if unit.__len__() == 0, do not make it None so that an invalid unit error is noticed later on

    return value_as_str, unit, comment


def _Pieces(
    combined: str, separator: str, /, *, from_left: bool = True
) -> tuple[str, str | None]:
    """"""
    if from_left:
        where_separator = combined.find(separator)
    else:
        where_separator = combined.rfind(separator)

    if where_separator != -1:
        left = combined[:where_separator].strip()
        right = combined[(where_separator + separator.__len__()) :].strip()
    else:
        left = combined
        right = None

    return left, right


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
