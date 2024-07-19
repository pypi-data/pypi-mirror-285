"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h

from pyvispr.catalog.factory._expression_evaluator import (
    ExpressionEvaluationError,
    ExpressionValue,
)


def pyVisprExpressionEvaluator(
    in0: h.Any,
    expression: str,
    /,
    *,
    in1: h.Any = None,
    in2: h.Any = None,
    in3: h.Any = None,
    in4: h.Any = None,
    in5: h.Any = None,
    in6: h.Any = None,
    in7: h.Any = None,
    in8: h.Any = None,
    in9: h.Any = None,
) -> h.Any:
    """
    _interactive: expression
    _outputs: result
    Tries to evaluate the expression using in0 through in9 as placeholders for inputs.
    Please refer to the NumExpr and Sympy packages for the allowed syntaxes of the
    expression.
    NumExpr: https://numexpr.readthedocs.io/en/latest/
    Sympy: https://www.sympy.org/en/index.html
    """
    intakes = {
        "in0": in0,
        "in1": in1,
        "in2": in2,
        "in3": in3,
        "in4": in4,
        "in5": in5,
        "in6": in6,
        "in7": in7,
        "in8": in8,
        "in9": in9,
    }

    value, exceptions = ExpressionValue(expression, intakes)
    if exceptions is None:
        return value

    raise ExpressionEvaluationError(
        f"Expression cannot be evaluated: {expression}\n"
        f"Numexpr says:\n{exceptions[0]}\n"
        f"Sympy says:\n{exceptions[1]}"
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
