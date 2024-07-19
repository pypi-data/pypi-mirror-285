"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h
from io import BytesIO as bytes_io_t
from io import StringIO as string_io_t
from pathlib import Path as path_t

from json_any.constant.compression import (
    STANDARD_COMPRESSOR_EXTENSIONS,
    STANDARD_COMPRESSOR_MODULES,
    de_compressor_h,
)
from json_any.extension.type import builders_h, descriptors_h
from json_any.json_to_object import ObjectFromJsonString
from json_any.object_to_json import JsonStringOf
from json_any.task.compression import CompressedVersion, DecompressedVersion

_DEFAULT_DE_COMPRESSOR = "Please use default (de)compressor"


def StoreAsJSON(
    instance: h.Any,
    path: str | path_t | bytes_io_t | string_io_t,
    /,
    *args,
    descriptors: descriptors_h = None,
    compressor: str | de_compressor_h | None = _DEFAULT_DE_COMPRESSOR,
    should_continue_on_error: bool = False,
    should_add_standard_extension: bool = True,
    should_overwrite_path: bool = False,
    indent: int | str | None = None,
    **kwargs,
) -> path_t | h.Sequence[str] | None:
    """"""
    if isinstance(path, str):
        path = path_t(path)

    if isinstance(path, path_t):
        extensions = path.suffixes
        if compressor == _DEFAULT_DE_COMPRESSOR:
            if extensions.__len__() > 0:
                compressor = _De_CompressorFromExtension(extensions)
            else:
                compressor = STANDARD_COMPRESSOR_MODULES[0]
                if should_add_standard_extension:
                    path = path.with_suffix(STANDARD_COMPRESSOR_EXTENSIONS[compressor])
        elif isinstance(compressor, str):
            if extensions.__len__() > 0:
                _CheckDeCompressorAndStdExtensionMatching(
                    compressor, "compressor", extensions
                )
            elif should_add_standard_extension and (
                compressor in STANDARD_COMPRESSOR_EXTENSIONS
            ):
                # If compressor not in STANDARD_COMPRESSOR_EXTENSIONS, the error will be
                # handled when actually compressing.
                path = path.with_suffix(STANDARD_COMPRESSOR_EXTENSIONS[compressor])
    elif compressor == _DEFAULT_DE_COMPRESSOR:
        compressor = STANDARD_COMPRESSOR_MODULES[0]

    if (
        isinstance(path, path_t)
        and path.exists()
        and not (path.is_file() and should_overwrite_path)
    ):
        message = f"{path}: Path exists and is not a file or should not be overwritten."
        if should_continue_on_error:
            return (message,)
        raise ValueError(message)
    if (isinstance(path, bytes_io_t) and (compressor is None)) or (
        isinstance(path, string_io_t) and (compressor is not None)
    ):
        raise ValueError(
            f"T.{type(path).__name__}, C.{compressor}: Path-like type T and "
            f"compression C mismatch. Expected={bytes_io_t} with compression, "
            f"or {string_io_t} without compression."
        )

    jsoned, history = JsonStringOf(instance, descriptors=descriptors, indent=indent)
    if history is None:
        if compressor is None:
            content = jsoned
            mode = "w"
        else:
            content = CompressedVersion(jsoned, *args, compressor=compressor, **kwargs)
            mode = "wb"
        if isinstance(path, path_t):
            with open(path, mode=mode) as json_accessor:
                json_accessor.write(content)
            return path
        else:
            path.write(content)
    elif should_continue_on_error:
        return history
    else:
        raise RuntimeError("\n".join(history))


def LoadFromJSON(
    path: str | path_t | bytes_io_t | string_io_t,
    /,
    *args,
    builders: builders_h = None,
    decompressor: str | de_compressor_h | None = _DEFAULT_DE_COMPRESSOR,
    should_continue_on_error: bool = False,
    **kwargs,
) -> h.Any:
    """"""
    if isinstance(path, str):
        path = path_t(path)

    if isinstance(path, path_t):
        extensions = path.suffixes
        if decompressor == _DEFAULT_DE_COMPRESSOR:
            if extensions.__len__() > 0:
                decompressor = _De_CompressorFromExtension(extensions)
            else:
                decompressor = STANDARD_COMPRESSOR_MODULES[0]
        elif isinstance(decompressor, str) and (extensions.__len__() > 0):
            _CheckDeCompressorAndStdExtensionMatching(
                decompressor, "decompressor", extensions
            )

        if decompressor is None:
            mode = "r"
        else:
            mode = "rb"
        with open(path, mode=mode) as json_accessor:
            content = json_accessor.read()
    else:
        content = path.read()
        if decompressor == _DEFAULT_DE_COMPRESSOR:
            decompressor = STANDARD_COMPRESSOR_MODULES[0]

    if decompressor is None:
        jsoned = content
    else:
        jsoned = DecompressedVersion(
            content,
            *args,
            decompressor=decompressor,
            **kwargs,
        )

    return ObjectFromJsonString(
        jsoned,
        builders=builders,
        should_continue_on_error=should_continue_on_error,
    )


def _De_CompressorFromExtension(
    extensions: h.Sequence[str], /
) -> str | None | h.NoReturn:
    """"""
    full_extension = "".join(extensions)
    for (
        std_compressor,
        std_full_extension,
    ) in STANDARD_COMPRESSOR_EXTENSIONS.items():
        if full_extension.lower() == std_full_extension:
            return std_compressor

    expected = " or ".join(STANDARD_COMPRESSOR_EXTENSIONS.values())
    raise ValueError(
        f"{full_extension}: Not a valid extension for automatic (de)compressor "
        f"selection. Expected={expected}."
    )


def _CheckDeCompressorAndStdExtensionMatching(
    de_compressor: str, actual: str, extensions: h.Sequence[str], /
) -> None | h.NoReturn:
    """"""
    if de_compressor not in STANDARD_COMPRESSOR_MODULES:
        raise ValueError(f"{de_compressor}: Unhandled (de)compression module.")

    full_extension = "".join(extensions)
    if full_extension.lower() == STANDARD_COMPRESSOR_EXTENSIONS[de_compressor]:
        return

    first_as_capital = actual[0].upper()
    expected = " or ".join(
        f"{first_as_capital}.{_key}+E.{_vle}"
        for _key, _vle in STANDARD_COMPRESSOR_EXTENSIONS.items()
    )
    raise ValueError(
        f"{first_as_capital}.{de_compressor}, E.{full_extension}: {actual.capitalize()} "
        f"{first_as_capital} and extension E do not match. Expected={expected}."
    )


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
