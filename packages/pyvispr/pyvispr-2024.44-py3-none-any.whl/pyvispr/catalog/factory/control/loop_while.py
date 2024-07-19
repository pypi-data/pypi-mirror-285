"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h

from logger_36.instance.loggers import LOGGERS
from pyvispr.catalog.factory._expression_evaluator import (
    ExpressionEvaluationError,
    ExpressionValue,
)
from pyvispr.constant.flow.value import VALUE_LOOP_DONE, VALUE_NOT_SET
from pyvispr.runtime.persistence import PERSISTENCE

# Entries must be initialized to 1 since this node is run for the first time when the
# loop body has been already run once.
_INITIAL_PAST_ITERATION = 1


def pyVisprLoopWhile(
    current: h.Any,
    condition: str,
    /,
    *,
    n_max_iterations: int = 1000,
    pyvispr_name: str | None = None,
) -> tuple[h.Any, h.Any]:
    """
    _interactive: condition, n_max_iterations
    _outputs: final, next_
    _right_to_left:
    Sends the current input through the next_ output if the condition is true, or
    through the final output otherwise. The next_ output should be linked with the next_
    input of the pyVisprLoopStart node.
    In the condition, use "c" to refer to the "current" input.
    Note: Because this node is placed at the end of the loop body, the body runs at
    least once.
    Note: next_ is used in place of next to match loop_start node input.
    """
    PERSISTENCE.Initialize(pyvispr_name, _INITIAL_PAST_ITERATION)

    if PERSISTENCE[pyvispr_name] < n_max_iterations:
        PERSISTENCE[pyvispr_name] += 1

        value, exceptions = ExpressionValue(condition, {"c": current})
        if exceptions is None:
            if value:
                return VALUE_NOT_SET, current
            return current, VALUE_LOOP_DONE

        raise ExpressionEvaluationError(
            f"Condition cannot be evaluated: {condition}\n"
            f"Numexpr says:\n{exceptions[0]}\n"
            f"Sympy says:\n{exceptions[1]}"
        )

    LOGGERS.active.warning(
        f'While loop "{pyvispr_name}" exceeded max number {n_max_iterations} of '
        f"iterations. Exiting with true condition."
    )
    PERSISTENCE[pyvispr_name] = _INITIAL_PAST_ITERATION
    return current, VALUE_LOOP_DONE


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
