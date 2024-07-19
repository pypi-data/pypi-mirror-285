"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h
from pathlib import Path as pl_path_t

from pyvispr.constant.flow.value import (
    VALUE_FOR_EACH_DONE,
    VALUE_NOT_SET,
    value_for_each_done_t,
    value_not_set_t,
)
from pyvispr.runtime.persistence import PERSISTENCE
from str_to_obj.api.catalog import path_purpose_e, path_t, path_type_e


def pyVisprForEach(
    elements: path_t.NewAnnotatedType(path_type_e.folder, path_purpose_e.input) | tuple,
    /,
    *,
    pattern: str = "*",
    current_in_idx: int | value_for_each_done_t | value_not_set_t | None = None,
    pyvispr_name: str | None = None,
) -> tuple[h.Any, int | value_for_each_done_t]:
    """
    _interactive: elements, pattern
    _outputs: next_in, next_in_idx
    Sends each element sequentially through the next_in output (next_in stands for the
    next element to be sent in the loop body).
    If elements is a path to a folder, the actual elements will be the files it
    contains, in alphabetic order.
    Note: this node works in conjunction with pyVisprIdentity; next_in_idx should be
    linked with the input of pyVisprIdentity, and the output of pyVisprIdentity should
    be linked to current_in_idx.
    """
    PERSISTENCE.Initialize(pyvispr_name, None)

    if PERSISTENCE[pyvispr_name] is None:
        if isinstance(elements, pl_path_t):
            if not elements.is_dir():
                raise NotADirectoryError(
                    f"Path {elements}: Not a folder, or cannot be read as such."
                )
            PERSISTENCE[pyvispr_name] = sorted(elements.glob(pattern))
        else:
            PERSISTENCE[pyvispr_name] = elements
        current_in_idx = 0

    if isinstance(current_in_idx, value_for_each_done_t):
        PERSISTENCE[pyvispr_name] = None
        return VALUE_NOT_SET, VALUE_NOT_SET

    if current_in_idx < PERSISTENCE[pyvispr_name].__len__():
        return PERSISTENCE[pyvispr_name][current_in_idx], current_in_idx + 1

    return VALUE_NOT_SET, VALUE_FOR_EACH_DONE


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
