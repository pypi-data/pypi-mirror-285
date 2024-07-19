"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h

from pyvispr.config.appearance.color import LINK_BRUSH_ARROW, LINK_PEN_FULL
from pyvispr.config.appearance.geometry import LINK_MIN_HORIZONTAL_SHIFT
from pyvispr.config.constant import APPEARANCE_SECTION, LINK_SMOOTH
from pyvispr.extension.qt.imports import qtcr, qtgi, qtwg
from pyvispr.flow.functional.link import socket_pairs_h
from pyvispr.flow.visual.node import node_t
from pyvispr.runtime.config import APP_CONFIG


@d.dataclass(slots=True, repr=False, eq=False)
class link_t(qtwg.QGraphicsPathItem):
    """
    Note: Using QGraphicsItemGroup as a base class in order to group the path and the
    arrow together somehow "hides" the path from mouse events: when clicked, the scene
    items are the group (not of interest) and the path (of interest), but as a path item
    instead of a link_t.
    """

    source: node_t
    target: node_t
    arrow: qtwg.QGraphicsPolygonItem | None = None

    def __post_init__(self) -> None:
        """"""
        qtwg.QGraphicsPathItem.__init__(self)

        if self.source.right_to_left:
            factor = -1
        else:
            factor = 1

        arrow = qtgi.QPolygonF()
        arrow.append(qtcr.QPointF(factor * 10, 0))
        arrow.append(qtcr.QPointF(0, 10))
        arrow.append(qtcr.QPointF(0, -10))
        arrow.append(qtcr.QPointF(factor * 10, 0))
        arrow = qtwg.QGraphicsPolygonItem(arrow)
        arrow.setPen(LINK_PEN_FULL)
        arrow.setBrush(LINK_BRUSH_ARROW)
        arrow.setZValue(1)
        self.arrow = arrow

    @classmethod
    def New(
        cls,
        source: node_t,
        source_point: qtcr.QPointF | None,
        target: node_t,
        target_point: qtcr.QPointF | None,
        /,
    ) -> h.Self:
        """"""
        output = cls(
            source=source,
            target=target,
        )
        output.SetPath(source_point, target_point, is_creation=True)
        output.setZValue(1)

        return output

    def SetPath(
        self,
        source_point: qtcr.QPointF,
        target_point: qtcr.QPointF,
        /,
        *,
        is_creation: bool = False,
    ) -> None:
        """"""
        if is_creation:
            translation = source_point
        else:
            translation = source_point - qtcr.QPointF(self.path().elementAt(0))
        polygon = self.arrow.polygon()
        polygon.translate(translation)
        self.arrow.setPolygon(polygon)

        # if self.source.right_to_left:
        #     link_min_horizontal_shift_src = LINK_MIN_HORIZONTAL_SHIFT
        # else:
        #     link_min_horizontal_shift_src = - LINK_MIN_HORIZONTAL_SHIFT
        # if self.target.right_to_left:
        #     link_min_horizontal_shift_tgt = - LINK_MIN_HORIZONTAL_SHIFT
        # else:
        #     link_min_horizontal_shift_tgt = LINK_MIN_HORIZONTAL_SHIFT

        path = qtgi.QPainterPath(source_point)
        if APP_CONFIG[APPEARANCE_SECTION][LINK_SMOOTH]:
            tangent = qtcr.QPointF(LINK_MIN_HORIZONTAL_SHIFT, 0.0)
            if self.source.right_to_left:
                factor_src = -1
            else:
                factor_src = 1
            if self.target.right_to_left:
                factor_tgt = -1
            else:
                factor_tgt = 1
            path.lineTo(source_point + 0.5 * factor_src * tangent)
            path.cubicTo(
                source_point + factor_src * tangent,
                target_point - factor_tgt * tangent,
                target_point - 0.5 * factor_tgt * tangent,
            )
        elif self.source.right_to_left == self.target.right_to_left:
            source_x, target_x = source_point.x(), target_point.x()
            middle_x = 0.5 * (source_x + target_x)
            if middle_x < source_x + LINK_MIN_HORIZONTAL_SHIFT:
                source_y, target_y = source_point.y(), target_point.y()
                middle_y = 0.5 * (source_y + target_y)
                path.lineTo(source_x + LINK_MIN_HORIZONTAL_SHIFT, source_y)
                path.lineTo(source_x + LINK_MIN_HORIZONTAL_SHIFT, middle_y)
                path.lineTo(target_x - LINK_MIN_HORIZONTAL_SHIFT, middle_y)
                path.lineTo(target_x - LINK_MIN_HORIZONTAL_SHIFT, target_y)
            else:
                path.lineTo(middle_x, source_point.y())
                path.lineTo(middle_x, target_point.y())
        else:
            source_x, target_x = source_point.x(), target_point.x()
            if self.source.right_to_left:
                extreme_x = min(source_x, target_x) - LINK_MIN_HORIZONTAL_SHIFT
            else:
                extreme_x = max(source_x, target_x) + LINK_MIN_HORIZONTAL_SHIFT
            path.lineTo(extreme_x, source_point.y())
            path.lineTo(extreme_x, target_point.y())
        path.lineTo(target_point)
        self.setPath(path)

    def UpdateTooltip(self, socket_pairs: socket_pairs_h, /) -> None:
        """"""
        socket_pairs = (f"{_elm[0]} -> {_elm[1]}" for _elm in socket_pairs)
        self.setToolTip("\n".join(socket_pairs))

    def __str__(self) -> str:
        """"""
        return f"{self.source.label.toPlainText()} => {self.target.label.toPlainText()}"


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
