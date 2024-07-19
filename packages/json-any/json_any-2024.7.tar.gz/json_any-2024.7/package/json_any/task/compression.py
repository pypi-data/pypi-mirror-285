"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2022
SEE COPYRIGHT NOTICE BELOW
"""

from json_any.constant.compression import (
    STANDARD_COMPRESSOR,
    STANDARD_COMPRESSOR_MODULES,
    STANDARD_DECOMPRESSOR,
    de_compressor_h,
)
from json_any.extension.module import ElementInModule


def CompressedVersion(
    jsoned: str,
    /,
    *args,
    compressor: str | de_compressor_h = STANDARD_COMPRESSOR_MODULES[0],
    **kwargs,
) -> bytes:
    """"""
    if isinstance(compressor, str):
        if compressor in STANDARD_COMPRESSOR_MODULES:
            Compressed, _ = ElementInModule(STANDARD_COMPRESSOR, compressor)
            if Compressed is None:
                raise ImportError(
                    f"{compressor}: Module not importable, "
                    f'or has no "{STANDARD_COMPRESSOR}" function.'
                )
        else:
            raise ValueError(f"{compressor}: Unhandled compression module.")
    else:
        Compressed = compressor

    return Compressed(jsoned.encode(), *args, **kwargs)


def DecompressedVersion(
    compressed: bytes,
    /,
    *args,
    decompressor: str | de_compressor_h = STANDARD_COMPRESSOR_MODULES[0],
    **kwargs,
) -> str:
    """"""
    if isinstance(decompressor, str):
        if decompressor in STANDARD_COMPRESSOR_MODULES:
            Decompressed, _ = ElementInModule(STANDARD_DECOMPRESSOR, decompressor)
            if Decompressed is None:
                raise ImportError(
                    f"{decompressor}: Module not importable, "
                    f'or has no "{STANDARD_DECOMPRESSOR}" function.'
                )
        else:
            raise ValueError(f"{decompressor}: Unhandled compression module.")
    else:
        Decompressed = decompressor

    output = Decompressed(compressed, *args, **kwargs)
    return output.decode()


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
