"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

from json_any.catalog.module import grph, nmpy, pnds, pypl, sprs, xrry
from json_any.constant.json import MODULE_TYPE_SEPARATOR

# Note: When there is a single class of interest in a module, the purpose of a *_CLASSES
# tuple is to have an homogeneous dealing of all modules.

if pypl is None:
    MATPLOTLIB_CLASSES = ()
else:
    MATPLOTLIB_CLASSES = (pypl.Figure,)

if grph is None:
    NETWORKX_CLASSES = ()
else:
    NETWORKX_CLASSES = (grph.Graph, grph.DiGraph, grph.MultiGraph, grph.MultiDiGraph)

if nmpy is None:
    JSON_TYPE_NUMPY_SCALAR = ""
    NUMPY_ARRAY_CLASSES = ()
else:
    JSON_TYPE_NUMPY_SCALAR = f"{nmpy.__name__}{MODULE_TYPE_SEPARATOR}SCALAR"
    NUMPY_ARRAY_CLASSES = (nmpy.ndarray,)

if pnds is None:
    PANDAS_CLASSES = ()
else:
    PANDAS_CLASSES = (pnds.Series, pnds.DataFrame)

if sprs is None:
    SCIPY_ARRAY_CLASSES = ()
else:
    SCIPY_ARRAY_CLASSES = (
        sprs.bsr_array,
        sprs.coo_array,
        sprs.csc_array,
        sprs.csr_array,
        sprs.dia_array,
        sprs.dok_array,
        sprs.lil_array,
    )

if xrry is None:
    XARRAY_CLASSES = ()
else:
    XARRAY_CLASSES = (xrry.DataArray, xrry.Dataset)

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
