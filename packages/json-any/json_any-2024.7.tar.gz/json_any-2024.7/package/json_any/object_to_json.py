"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import importlib as imlb
import json
import sys as sstm
import typing as h

from json_any.catalog.module import grph
from json_any.catalog.type import (
    date_t,
    date_time_t,
    decimal_t,
    enum_t,
    fraction_t,
    io_bytes_t,
    io_string_t,
    named_tuple_t,
    path_t,
    py_array_t,
    time_delta_t,
    time_t,
    time_zone_t,
    uuid_t,
)
from json_any.constant.json import (
    CUSTOM_PREFIX,
    DATACLASS_PREFIX,
    DESCRIPTION_FOR_JSON,
    JSONING_ERROR_MARKER,
    STANDARD_PREFIX,
    TYPE_PREFIX,
    UNHANDLED_PREFIX,
)
from json_any.constant.module import (
    JSON_TYPE_NUMPY_SCALAR,
    MATPLOTLIB_CLASSES,
    NETWORKX_CLASSES,
    NUMPY_ARRAY_CLASSES,
    PANDAS_CLASSES,
    SCIPY_ARRAY_CLASSES,
    XARRAY_CLASSES,
)
from json_any.constant.type import (
    BUILTIN_BYTES_CONTAINERS,
    BUILTIN_CONTAINERS,
    JSON_TYPE,
    JSON_TYPE_PREFIX_PATHLIB,
)
from json_any.extension.numpy import (
    AsMostConciseRepresentation,
    AsScalarRepresentation,
    IsNumpyScalar,
)
from json_any.extension.type import (
    IsFullyDataclassBased,
    IsNamedTuple,
    QualifiedType,
    description_h,
    descriptors_h,
)

_HISTORY_INDENTATION = 4 * " "


# TODO: JSON alternatives:
#     https://pymongo.readthedocs.io/en/stable/api/bson/index.html
#     https://ubjson.org/libraries/
#     https://en.wikipedia.org/wiki/CBOR
#     https://pypi.org/project/newsmile/    https://github.com/FasterXML/smile-format-specification
def JsonStringOf(
    instance: h.Any,
    /,
    *,
    descriptors: descriptors_h = None,
    indent: int | str | None = None,
) -> tuple[str, h.Sequence[str] | None]:
    """"""
    history = []
    jsonable = _JsonableVersionOf(
        instance, history, "", highest_level_call=True, descriptors=descriptors
    )
    if all(not _elm.startswith(JSONING_ERROR_MARKER) for _elm in history):
        history = None

    return json.dumps(jsonable, indent=indent), history


def _JsonableVersionOf(
    instance: h.Any,
    history: list[str],
    history_level: str,
    /,
    *,
    highest_level_call: bool = False,
    descriptors: descriptors_h = None,
) -> description_h:
    """"""
    instance_type = type(instance)
    json_type = JSON_TYPE.get(instance_type, None)
    qualified_type = QualifiedType(instance_type)

    if descriptors is None:
        descriptors = {}
    if qualified_type in descriptors:
        DescriptionForJSON = descriptors[qualified_type]
    elif highest_level_call and ("" in descriptors):
        # Empty key "" is equivalent to QualifiedType(instance) when instance is
        # the object passed to "JsonStringOf". It allows to avoid to have to call
        # QualifiedType in the first place.
        DescriptionForJSON = descriptors[""]
    else:
        DescriptionForJSON = getattr(instance_type, DESCRIPTION_FOR_JSON, None)
    if DescriptionForJSON is not None:
        json_type = f"{CUSTOM_PREFIX}{qualified_type}"
        history.append(history_level + json_type)
        jsonable = _JsonableVersionOf(
            DescriptionForJSON(instance),
            history,
            history_level + _HISTORY_INDENTATION,
            descriptors=descriptors,
        )
    elif d.is_dataclass(instance):
        if IsFullyDataclassBased(instance_type):
            json_type = f"{DATACLASS_PREFIX}{qualified_type}"
            # Do not use d.asdict(instance) since it recurses into dataclass
            # instances which, if they extend a "container" class like list or dict,
            # might lose information.
            description = {
                _fld.name: getattr(instance, _fld.name) for _fld in d.fields(instance)
            }
            history.append(f"{history_level}{json_type}[{description.__len__()}]")
            jsonable = _JsonableVersionOf(
                description,
                history,
                history_level + _HISTORY_INDENTATION,
                descriptors=descriptors,
            )
        else:
            json_type = f"{UNHANDLED_PREFIX}{DATACLASS_PREFIX}{qualified_type}"
            jsonable = None
            history.append(
                f"{JSONING_ERROR_MARKER}{history_level}"
                f"{instance_type.__name__}: Dataclass with inheritance "
                f'without a "{DESCRIPTION_FOR_JSON}" method. Using None.'
            )
    elif instance_type in BUILTIN_BYTES_CONTAINERS:
        # bytes.hex was initially used in place of bytes.decode.
        json_type = instance_type.__name__
        jsonable = instance.decode(encoding="iso-8859-1")
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type is complex:
        json_type = complex.__name__
        jsonable = (instance.real, instance.imag)
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type is slice:
        json_type = slice.__name__
        jsonable = (instance.start, instance.stop, instance.step)
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type is uuid_t:
        jsonable = instance.int
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type is date_t:
        jsonable = (instance.year, instance.month, instance.day)
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type is time_delta_t:
        jsonable = (instance.days, instance.seconds, instance.microseconds)
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type is decimal_t:
        jsonable = instance.as_tuple()
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type is fraction_t:
        jsonable = (instance.numerator, instance.denominator)
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type is py_array_t:
        jsonable = (instance.tolist(), instance.typecode)
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type is io_bytes_t:
        # Buffer is assumed to be open (i.e. no instance.closed check).
        jsonable = instance.getvalue().decode(encoding="iso-8859-1")
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type is io_string_t:
        # Buffer is assumed to be open (i.e. no instance.closed check).
        jsonable = instance.getvalue()
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif issubclass(instance_type, path_t):
        json_type = f"{JSON_TYPE_PREFIX_PATHLIB}{instance_type.__name__}"
        jsonable = str(instance)
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type in SCIPY_ARRAY_CLASSES:
        jsonable = AsMostConciseRepresentation(instance.toarray())
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type in NUMPY_ARRAY_CLASSES:
        jsonable = AsMostConciseRepresentation(instance)
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type in XARRAY_CLASSES:
        jsonable = instance.to_dict()
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type in PANDAS_CLASSES:
        if (columns := getattr(instance, "columns", None)) is None:
            column_names = None
        else:
            column_names = columns.names
        jsonable = _JsonableVersionOf(
            (instance.to_dict(), instance.index.names, column_names),
            history,
            history_level + _HISTORY_INDENTATION,
            descriptors=descriptors,
        )
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif IsNumpyScalar(instance_type):
        json_type = JSON_TYPE_NUMPY_SCALAR
        description = AsScalarRepresentation(instance, instance_type)
        jsonable = (instance.dtype.char, description)
        history.append(f"{history_level}{json_type}:{jsonable}")
    elif instance_type in MATPLOTLIB_CLASSES:
        fake_file = io_bytes_t()
        instance.canvas.draw()
        instance.savefig(
            fake_file,
            bbox_inches="tight",
            pad_inches=0.0,
            transparent=True,
            dpi=200.0,
            format="png",
        )
        jsonable = fake_file.getvalue().decode(encoding="iso-8859-1")
        fake_file.close()
        history.append(history_level + json_type)
    elif instance_type is date_time_t:
        history.append(history_level + json_type)
        jsonable = _JsonableVersionOf(
            (instance.date(), instance.timetz()),
            history,
            history_level + _HISTORY_INDENTATION,
        )
    elif instance_type is time_t:
        history.append(history_level + json_type)
        jsonable = (
            instance.hour,
            instance.minute,
            instance.second,
            instance.microsecond,
            _JsonableVersionOf(
                instance.tzinfo, history, history_level + _HISTORY_INDENTATION
            ),
            instance.fold,
        )
    elif instance_type is time_zone_t:
        history.append(history_level + json_type)
        jsonable = _JsonableVersionOf(
            (instance.utcoffset(None), instance.tzname(None)),
            history,
            history_level + _HISTORY_INDENTATION,
        )
    elif issubclass(instance_type, enum_t):
        json_type = f"{JSON_TYPE[enum_t]}{qualified_type}"
        history.append(history_level + json_type)
        jsonable = _JsonableVersionOf(
            instance.value,
            history,
            history_level + _HISTORY_INDENTATION,
            descriptors=descriptors,
        )
    elif IsNamedTuple(instance):
        json_type = f"{JSON_TYPE[named_tuple_t]}{qualified_type}"
        description = tuple(instance)
        history.append(f"{history_level}{json_type}[{description.__len__()}]")
        jsonable = _JsonableVersionOf(
            description,
            history,
            history_level + _HISTORY_INDENTATION,
            descriptors=descriptors,
        )
    elif instance_type in BUILTIN_CONTAINERS:
        json_type = instance_type.__name__
        history.append(f"{history_level}{json_type}[{instance.__len__()}]")
        jsonable = [
            _JsonableVersionOf(
                _elm,
                history,
                history_level + _HISTORY_INDENTATION,
                descriptors=descriptors,
            )
            for _elm in instance
        ]
    elif instance_type is dict:
        # json does not accept non-str dictionary keys, hence the json.dumps.
        json_type = dict.__name__
        history.append(f"{history_level}{json_type}[{instance.__len__()}]")
        jsonable = {
            json.dumps(
                _JsonableVersionOf(
                    _key,
                    history,
                    history_level + _HISTORY_INDENTATION,
                    descriptors=descriptors,
                )
            ): _JsonableVersionOf(
                _vle,
                history,
                history_level + _HISTORY_INDENTATION,
                descriptors=descriptors,
            )
            for _key, _vle in instance.items()
        }
    elif instance_type in NETWORKX_CLASSES:
        edges = grph.to_dict_of_dicts(instance)
        # /!\ Node attributes are added to the edges dictionary! This must be taken into account when deJSONing. Note
        # that several attempts to avoid this have been made, including one relying on repr(node), which is based on
        # hash(node). Since the hash function gives different results across Python sessions, this could not work.
        for node, attributes in instance.nodes(data=True):
            edges[node] = (attributes, edges[node])
        history.append(history_level + json_type)
        jsonable = _JsonableVersionOf(
            edges,
            history,
            history_level + _HISTORY_INDENTATION,
            descriptors=descriptors,
        )
    elif instance_type is type:
        json_type = type.__name__
        jsonable = None

        module = instance.__module__
        imported = sstm.modules.get(module, None)
        if imported is None:
            imported = imlb.import_module(module)
        for name in dir(imported):
            if name[0] == "_":
                continue
            if getattr(imported, name) is instance:
                json_type = f"{TYPE_PREFIX}{module}"
                jsonable = name
        if jsonable is None:
            history.append(
                f"{JSONING_ERROR_MARKER}{history_level}"
                f"{json_type}/{instance}: "
                f"UnJSONable type/instance. Using None."
            )
        else:
            history.append(f"{history_level}{json_type}:{jsonable}")
    else:
        try:
            _ = json.dumps(instance)
            json_type = f"{STANDARD_PREFIX}{instance_type.__name__}"
            jsonable = instance
            history.append(f"{history_level}{json_type}:{jsonable}")
        except TypeError:
            json_type = f"{UNHANDLED_PREFIX}{instance_type.__name__}"
            jsonable = None
            history.append(
                f"{JSONING_ERROR_MARKER}{history_level}"
                f"{json_type[UNHANDLED_PREFIX.__len__():]}: "
                f"UnJSONable type. Using None."
            )

    return json_type, jsonable


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
