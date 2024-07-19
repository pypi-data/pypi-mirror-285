"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import ast as prsr
import dataclasses as d
import typing as h
from enum import Enum as enum_t
from inspect import Parameter as parameter_t

from pyvispr.constant.flow.node import NO_ANNOTATION, NO_INTAKE_NAME
from pyvispr.constant.flow.value import VALUE_NOT_SET, value_not_set_t
from str_to_obj.api.type import type_t


class assignment_e(enum_t):
    """
    full: link + interactive, user input.
    """

    link = 0
    full = 1


class _assign_when_updating_t:
    pass


_ASSIGN_WHEN_UPDATING = _assign_when_updating_t()


@d.dataclass(slots=True, repr=False, eq=False)
class intake_t:
    type: type_t | _assign_when_updating_t = _ASSIGN_WHEN_UPDATING
    default_value: h.Any = VALUE_NOT_SET
    assignment: assignment_e = assignment_e.link

    @property
    def has_default(self) -> bool:
        """"""
        return not isinstance(self.default_value, value_not_set_t)

    def UpdateFromSignature(self, intake: parameter_t, annotation: h.Any, /) -> bool:
        """"""
        # intake.annotation cannot be used because of the mess w/ __future__.annotations
        if annotation == NO_ANNOTATION:
            annotation = h.Any
            requires_completion = True
        else:
            # annotation = intake.annotation
            requires_completion = False

        self.type = type_t.NewForHint(annotation)
        if self.default_value is _ASSIGN_WHEN_UPDATING:
            self.default_value = intake.default

        return requires_completion


def IntakesFromAST(
    function: prsr.FunctionDef, ii_names: str | None, should_make_all_full: bool, /
) -> tuple[dict[str, intake_t], bool]:
    """
    /!\\ This function does not deal with all signature contexts:
    Nodes are installed having only positional-only and/or keywords-only arguments.
    There is no need to consider ast_intakes.args and ast_intakes.defaults. Additionally,
    there cannot be *args or **kwargs since they are replaced with single
    positional-only and keywords-only parameters, resp., at installation.
    """
    intakes = {}
    requires_completion = False

    if (ii_names is None) or (ii_names.__len__() == 0):
        ii_names = ()
    else:
        ii_names = ii_names.split(", ")
        should_make_all_full = False

    ast_intakes = function.args
    for ast_intakes_per_type, default in (
        (ast_intakes.posonlyargs, VALUE_NOT_SET),
        (ast_intakes.kwonlyargs, _ASSIGN_WHEN_UPDATING),
    ):
        for ast_intake in ast_intakes_per_type:
            name = ast_intake.arg
            if name.startswith(NO_INTAKE_NAME):
                requires_completion = True

            if should_make_all_full or (name in ii_names):
                assignment = assignment_e.full
            else:
                assignment = assignment_e.link

            intakes[name] = intake_t(
                assignment=assignment,
                default_value=default,
            )

    return intakes, requires_completion


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
