"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2021
SEE COPYRIGHT NOTICE BELOW
"""

import ast as bstr
import inspect as nspt
import sys as sstm
from pathlib import Path as path_t


def SpecificationPath(element: object, /, *, relative_to_home: bool = True) -> str:
    """"""
    try:
        found = [nspt.getfile(element)]
    except TypeError:
        found = []
    if found.__len__() == 0:
        for module in sstm.modules.copy().values():
            for attribute in dir(module):
                # It can happen that "attribute" ends up not being an attribute of
                # "module", for example with "single" in scipy.linalg.matfuncs. Hence,
                # the default value in getattr. The getattr call can even fail, for
                # example with "Viewer" in napari. Hence the try-expect.
                try:
                    value = getattr(module, attribute, None)
                except:
                    value = None
                if (value is not None) and (value is element):
                    code = nspt.getsource(module)
                    tree = bstr.parse(code)
                    is_imported = False
                    for node in bstr.walk(tree):
                        if isinstance(node, bstr.ImportFrom):
                            for alias in node.names:
                                if (
                                    (alias.asname is None) and (alias.name == attribute)
                                ) or (
                                    (alias.asname is not None)
                                    and (alias.asname == attribute)
                                ):
                                    is_imported = True
                                    break
                    if not is_imported:
                        path = module.__file__
                        if relative_to_home:
                            path = str(
                                path_t(path)
                                .resolve(strict=True)
                                .relative_to(path_t.home().resolve(strict=True))
                            )
                        found.append(path)

    if (n_found := found.__len__()) == 0:
        output = "Unidentified specification file"
    elif n_found == 1:
        output = found[0]
    else:
        alternatives = ", ".join(found)
        output = f"Alternatives: {alternatives}"

    return output


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
