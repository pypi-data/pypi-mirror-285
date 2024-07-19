"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import types as t
import typing as h
from array import array as py_array_t
from datetime import date as date_t
from datetime import datetime as date_time_t
from datetime import time as time_t
from datetime import timedelta as time_delta_t
from datetime import timezone as time_zone_t
from decimal import Decimal as decimal_t
from enum import Enum as enum_t
from fractions import Fraction as fraction_t
from io import BytesIO as io_bytes_t
from io import StringIO as io_string_t
from pathlib import PurePath as path_t
from uuid import UUID as uuid_t

from json_any.catalog.module import grph, nmpy, pnds, pypl, sprs, xrry
from json_any.constant.json import MODULE_TYPE_SEPARATOR
from json_any.constant.module import (
    NETWORKX_CLASSES,
    NUMPY_ARRAY_CLASSES,
    PANDAS_CLASSES,
    SCIPY_ARRAY_CLASSES,
    XARRAY_CLASSES,
)
from json_any.constant.type import (
    BUILTIN_BYTES_CONTAINERS,
    BUILTIN_BYTES_CONTAINERS_NAMES,
    BUILTIN_CONTAINERS,
    BUILTIN_CONTAINERS_NAMES,
    JSON_TYPE,
)

named_tuple_t = h.NamedTuple


def ContainerWithName(name: str, /) -> type:
    """"""
    if name in BUILTIN_BYTES_CONTAINERS_NAMES:
        return BUILTIN_BYTES_CONTAINERS[BUILTIN_BYTES_CONTAINERS_NAMES.index(name)]
    else:
        return BUILTIN_CONTAINERS[BUILTIN_CONTAINERS_NAMES.index(name)]


def TypeIsInModule(json_type: str, module: t.ModuleType | None, /) -> bool:
    """"""
    if module is None:
        return False

    module_name = module.__name__
    return json_type.startswith(module_name) and (
        json_type[module_name.__len__()] in (".", MODULE_TYPE_SEPARATOR)
    )


def TypeNameOf(json_type: str, /) -> str:
    """"""
    return json_type[(json_type.rindex(MODULE_TYPE_SEPARATOR) + 1) :]


def _AddJsonTypes(types: h.Sequence[type], /) -> None:
    """"""

    for type_ in types:
        JSON_TYPE[type_] = f"{type_.__module__}{MODULE_TYPE_SEPARATOR}{type_.__name__}"


_AddJsonTypes(
    (
        date_t,
        date_time_t,
        decimal_t,
        enum_t,
        fraction_t,
        io_bytes_t,
        io_string_t,
        named_tuple_t,
        py_array_t,
        time_delta_t,
        time_t,
        time_zone_t,
        uuid_t,
    )
)

if pypl is not None:
    figure_t = pypl.Figure
    # Unfortunately, figure_t.__module__ is reported as "matplotlib.figure" instead of
    # the expected "matplotlib.pyplot".
    JSON_TYPE[figure_t] = f"{pypl.__name__}{MODULE_TYPE_SEPARATOR}{figure_t.__name__}"
if grph is not None:
    _AddJsonTypes(NETWORKX_CLASSES)
if nmpy is not None:
    np_array_t = nmpy.ndarray
    _AddJsonTypes(NUMPY_ARRAY_CLASSES)
if pnds is not None:
    _AddJsonTypes(PANDAS_CLASSES)
if sprs is not None:
    _AddJsonTypes(SCIPY_ARRAY_CLASSES)
if xrry is not None:
    _AddJsonTypes(XARRAY_CLASSES)

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
