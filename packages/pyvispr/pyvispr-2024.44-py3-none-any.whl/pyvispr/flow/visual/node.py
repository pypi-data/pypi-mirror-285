"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h

from conf_ini_g.interface.window.parameter.main import TypeAndValueWidgetsForType
from pyvispr.config.appearance.color import (
    BUTTON_BRUSH_CONFIG,
    BUTTON_BRUSH_REMOVE,
    BUTTON_BRUSH_STATE_TODO,
    II_WIDGET_BACKGROUND,
    INOUT_BRUSH_INACTIVE,
    NODE_BRUSH_RESTING,
    NODE_BRUSH_SELECTED,
)
from pyvispr.config.appearance.geometry import (
    BUTTON_WIDTH,
    GRID_RESOLUTION_H,
    GRID_RESOLUTION_V,
    NODE_HEIGHT_TOTAL,
    NODE_WIDTH_TOTAL,
)
from pyvispr.constant.flow.node import (
    MSG_NEW_NODE_NAME_REQUESTED,
    MSG_NEW_NODE_POSITION,
)
from pyvispr.constant.flow.value import VALUE_NOT_SET, value_not_set_t
from pyvispr.constant.interface.widget.node import (
    HEIGHT_OF_BOTTOM_BUTTONS,
    HEIGHT_OF_LATERAL_BUTTONS,
    HORIZONTAL_FREE_SPACE,
    NEEDS_RUNNING,
    TOP_OF_BOTTOM_BUTTONS,
    WIDTH_OF_LATERAL_BUTTONS,
)
from pyvispr.exception.node import NotAnInteractiveInputError
from pyvispr.extension.object.field import NON_INIT_FIELD, NonInitField_NONE
from pyvispr.extension.qt.imports import qt_e, qtcr, qtwg
from pyvispr.flow.descriptive.intake import assignment_e
from pyvispr.flow.descriptive.node import node_t as descriptive_t
from pyvispr.flow.functional.node import node_t as functional_t
from pyvispr.flow.visual.value import invalid_ii_value_t
from pyvispr.runtime.backend import SCREEN_BACKEND
from pyvispr.runtime.catalog import NODE_CATALOG
from sio_messenger import MESSENGER
from str_to_obj.api.type import annotation_t, type_t


class ii_widget_p(qtwg.QWidget):
    library_wgt: qtwg.QWidget
    values: tuple[qtwg.QWidget, ...]

    def SetNewValueAcknowledgementFunction(
        self, InvalidateNodeOutputs: h.Callable[[], None] | None, /
    ) -> None: ...

    def Assign(
        self,
        value: h.Any,
        stripe: type_t | annotation_t | None,
    ) -> None: ...

    def Text(self) -> str: ...


_change_e = qtwg.QGraphicsItem.GraphicsItemChange
_flag_e = qtwg.QGraphicsItem.GraphicsItemFlag

_NODE_RECTANGLE = qtcr.QRectF(0, 0, NODE_WIDTH_TOTAL, NODE_HEIGHT_TOTAL)

_IN_BUTTON_RECTANGLE = qtcr.QRectF(
    0, 0, WIDTH_OF_LATERAL_BUTTONS, HEIGHT_OF_LATERAL_BUTTONS
)
_OUT_BUTTON_RECTANGLE = qtcr.QRectF(
    NODE_WIDTH_TOTAL - WIDTH_OF_LATERAL_BUTTONS,
    0,
    WIDTH_OF_LATERAL_BUTTONS,
    HEIGHT_OF_LATERAL_BUTTONS,
)
_CONFIG_BUTTON_WIDTH = int(HORIZONTAL_FREE_SPACE / 2.5)
_CONFIG_BUTTON_RECTANGLE = qtcr.QRectF(
    WIDTH_OF_LATERAL_BUTTONS,
    TOP_OF_BOTTOM_BUTTONS,
    _CONFIG_BUTTON_WIDTH,
    HEIGHT_OF_BOTTOM_BUTTONS,
)
_STATE_BUTTON_RECTANGLE = qtcr.QRectF(
    WIDTH_OF_LATERAL_BUTTONS + _CONFIG_BUTTON_WIDTH,
    TOP_OF_BOTTOM_BUTTONS,
    _CONFIG_BUTTON_WIDTH,
    HEIGHT_OF_BOTTOM_BUTTONS,
)
_REMOVE_BUTTON_RECTANGLE = qtcr.QRectF(
    WIDTH_OF_LATERAL_BUTTONS + 2 * _CONFIG_BUTTON_WIDTH,
    TOP_OF_BOTTOM_BUTTONS,
    HORIZONTAL_FREE_SPACE - 2 * _CONFIG_BUTTON_WIDTH,
    HEIGHT_OF_BOTTOM_BUTTONS,
)


@d.dataclass(slots=True, repr=False, eq=False)
class node_t(qtwg.QGraphicsRectItem):
    label: qtwg.QGraphicsTextItem
    in_btn: qtwg.QGraphicsRectItem | None
    out_btn: qtwg.QGraphicsRectItem | None

    ii_names: tuple[str, ...]
    ii_dialog: qtwg.QGraphicsProxyWidget | None = NonInitField_NONE()
    ii_widgets: dict[str, ii_widget_p] | None = NonInitField_NONE()

    config_btn: qtwg.QGraphicsRectItem | None = NON_INIT_FIELD
    state_btn: qtwg.QGraphicsRectItem = NON_INIT_FIELD
    remove_btn: qtwg.QGraphicsRectItem = NON_INIT_FIELD

    right_to_left: bool = False

    true_name_request: bool = d.field(init=False, default=True)

    @property
    def intake_socket_coordinates(self) -> qtcr.QPointF:
        """"""
        return self._SocketCoordinates(True)

    @property
    def output_socket_coordinates(self) -> qtcr.QPointF:
        """"""
        return self._SocketCoordinates(False)

    def _SocketCoordinates(self, is_intake: bool, /) -> qtcr.QPointF:
        """"""
        if self.right_to_left:
            is_intake = not is_intake

        output = self.scenePos()
        output.setY(output.y() + int(0.5 * self.boundingRect().height()))

        if not is_intake:
            output.setX(output.x() + self.boundingRect().width())

        return output

    def __post_init__(self) -> None:
        """"""
        qtwg.QGraphicsRectItem.__init__(self, _NODE_RECTANGLE)

        for flag in (
            _flag_e.ItemIsSelectable,
            _flag_e.ItemIsMovable,
            _flag_e.ItemSendsGeometryChanges,
        ):
            self.setFlag(flag)
        self.setBrush(NODE_BRUSH_RESTING)
        self.setZValue(2)

        if self.ii_names.__len__() > 0:
            config_btn = qtwg.QGraphicsRectItem(_CONFIG_BUTTON_RECTANGLE)
            config_btn.setBrush(BUTTON_BRUSH_CONFIG)
        else:
            config_btn = None

        state_btn = qtwg.QGraphicsRectItem(_STATE_BUTTON_RECTANGLE)
        state_btn.setToolTip(NEEDS_RUNNING)
        state_btn.setBrush(BUTTON_BRUSH_STATE_TODO)

        remove_btn = qtwg.QGraphicsRectItem(_REMOVE_BUTTON_RECTANGLE)
        remove_btn.setBrush(BUTTON_BRUSH_REMOVE)

        self.config_btn, self.state_btn, self.remove_btn = (
            config_btn,
            state_btn,
            remove_btn,
        )
        for item in (
            self.label,
            self.in_btn,
            self.out_btn,
            self.config_btn,
            self.state_btn,
            self.remove_btn,
        ):
            if item is not None:
                item.setParentItem(self)

        SCREEN_BACKEND.AddMessageCanal(
            self.label.document(),
            "contentsChanged",
            self.RequestNewName,
        )

    @classmethod
    def NewForFunctional(
        cls,
        functional: functional_t,
        InvalidateOutputs: h.Callable[[], None],
        /,
    ) -> h.Self:
        """"""
        label = qtwg.QGraphicsTextItem(functional.name)
        label.setPos(BUTTON_WIDTH, 0)
        label.setTextWidth(NODE_WIDTH_TOTAL - 2 * BUTTON_WIDTH)
        label.setTextInteractionFlags(qt_e.TextInteractionFlag.TextEditorInteraction)

        description = NODE_CATALOG[functional.catalog_name]
        right_to_left = description.right_to_left

        if description.n_intakes > 0:
            if right_to_left:
                rectangle = _OUT_BUTTON_RECTANGLE
            else:
                rectangle = _IN_BUTTON_RECTANGLE
            in_btn = qtwg.QGraphicsRectItem(rectangle)
            in_btn.setBrush(INOUT_BRUSH_INACTIVE)
        else:
            in_btn = None

        if description.n_outputs > 0:
            if right_to_left:
                rectangle = _IN_BUTTON_RECTANGLE
            else:
                rectangle = _OUT_BUTTON_RECTANGLE
            out_btn = qtwg.QGraphicsRectItem(rectangle)
            out_btn.setBrush(INOUT_BRUSH_INACTIVE)
        else:
            out_btn = None

        ii_names = tuple(
            _nme
            for _nme, _rcd in description.intakes.items()
            if _rcd.assignment is assignment_e.full
        )

        output = cls(
            label=label,
            in_btn=in_btn,
            out_btn=out_btn,
            ii_names=ii_names,
            right_to_left=right_to_left,
        )
        if ii_names.__len__() > 0:
            output.CreateIIWidgets(description, InvalidateOutputs)

        return output

    def RequestNewName(self) -> None:
        """"""
        if self.true_name_request:
            MESSENGER.Transmit(
                MSG_NEW_NODE_NAME_REQUESTED, self, self.label.toPlainText()
            )
        else:
            self.true_name_request = True

    def SetNewName(self, name: str, /) -> None:
        """"""
        label = self.label

        cursor = label.textCursor()
        where = cursor.position()

        self.true_name_request = False
        label.setPlainText(name)

        cursor.setPosition(min(where, name.__len__()))
        label.setTextCursor(cursor)

    def CreateIIWidgets(
        self, description: descriptive_t, InvalidateOutputs: h.Callable[[], None], /
    ) -> None:
        """"""
        ii_widgets = {}
        layout = qtwg.QGridLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        for i_idx, (name, record) in enumerate(description.intakes.items()):
            if record.assignment is assignment_e.full:
                type_wgt, value_wgt = TypeAndValueWidgetsForType(
                    record.type, SCREEN_BACKEND
                )
                ii_widgets[name] = value_wgt
                if record.has_default:
                    value_wgt.Assign(record.default_value, record.type)

                layout.addWidget(qtwg.QLabel(name), i_idx, 0, 1, 1)
                layout.addWidget(type_wgt, i_idx, 1, 1, 1)
                layout.addWidget(value_wgt.library_wgt, i_idx, 2, 1, 1)
        self.ii_widgets = ii_widgets

        widget = qtwg.QWidget()
        widget.setFixedWidth(3 * NODE_WIDTH_TOTAL)
        widget.setLayout(layout)
        widget.setStyleSheet(f"background-color: {II_WIDGET_BACKGROUND.name()};")

        ii_dialog = qtwg.QGraphicsProxyWidget()
        ii_dialog.setZValue(2)
        ii_dialog.setWidget(widget)
        ii_dialog.setPos(self.x(), self.y() + NODE_HEIGHT_TOTAL)
        self.ii_dialog = ii_dialog

        self.SetNewValueAcknowledgementFunction(InvalidateOutputs)

    def SetNewValueAcknowledgementFunction(
        self, InvalidateOutputs: h.Callable[[], None] | None, /
    ) -> None:
        """"""
        if self.ii_widgets is None:
            return

        for ii_widget in self.ii_widgets.values():
            if isinstance(ii_widget.library_wgt, qtwg.QStackedWidget):
                widgets = (_elm for _elm in ii_widget.values)
            else:
                widgets = (ii_widget,)
            for widget in widgets:
                widget.SetNewValueAcknowledgementFunction(InvalidateOutputs)

    def SetIIValue(self, intake_name: str, value: h.Any, description: str, /) -> None:
        """"""
        if isinstance(value, value_not_set_t):
            pass
        elif isinstance(value, invalid_ii_value_t):
            # TODO: Implement SetText whenever appropriate.
            widget = self.ii_widgets[intake_name]
            if hasattr(widget, "SetText"):
                widget.SetText(value.as_str)
        else:
            description = NODE_CATALOG[description]
            stripe = description.intakes[intake_name].type
            self.ii_widgets[intake_name].Assign(value, stripe)

    def IIValue(
        self, catalog_name: str, /, *, intake_name: str | None = None
    ) -> h.Any | dict[str, h.Any]:
        """"""
        if (ii_widgets := self.ii_widgets) is None:
            return {}

        if intake_name is None:
            intake_names = self.ii_names
            return_as_dict = True
        elif intake_name in self.ii_names:
            intake_names = (intake_name,)
            return_as_dict = False
        else:
            raise NotAnInteractiveInputError(
                f"Not an interactive input: {intake_name}."
            )

        output = {}

        intakes = NODE_CATALOG[catalog_name].intakes
        for intake_name in intake_names:
            intake_description = intakes[intake_name]
            value_as_str = ii_widgets[intake_name].Text()
            if value_as_str.__len__() > 0:
                expected_type = intake_description.type
                value, issues = expected_type.InterpretedValueOf(value_as_str)
                if issues.__len__() > 0:
                    value = invalid_ii_value_t(as_str=value_as_str, issues=issues)
            elif intake_description.has_default:
                value = intake_description.default_value
            else:
                value = VALUE_NOT_SET
            output[intake_name] = value

        if return_as_dict:
            return output
        return output[intake_name]

    def ToggleIIDialog(self) -> None:
        """
        IIDialog placement could be handled automatically with graphics anchors. Keeping
        manual management for the moment.
        """
        if self.ii_dialog.isVisible():
            self.ii_dialog.hide()
        else:
            self.ii_dialog.setPos(self.x(), self.y() + NODE_HEIGHT_TOTAL)
            self.ii_dialog.show()

    def AlignOnGrid(self) -> None:
        """"""
        position_x, position_y = (
            round(self.x() / GRID_RESOLUTION_H) * GRID_RESOLUTION_H,
            round(self.y() / GRID_RESOLUTION_V) * GRID_RESOLUTION_V,
        )
        self.setPos(position_x, position_y)

    def DisableEvents(self) -> None:
        """"""
        SCREEN_BACKEND.RemoveMessageCanal(
            self.label.document(),
            "contentsChanged",
        )
        self.SetNewValueAcknowledgementFunction(None)

    def itemChange(self, change: _change_e, data: h.Any, /) -> h.Any:
        """"""
        if change is _change_e.ItemSelectedHasChanged:
            if data:
                self.setBrush(NODE_BRUSH_SELECTED)
            else:
                self.setBrush(NODE_BRUSH_RESTING)
        elif change is _change_e.ItemPositionHasChanged:
            MESSENGER.Transmit(MSG_NEW_NODE_POSITION, self)
            if (self.ii_dialog is not None) and self.ii_dialog.isVisible():
                self.ii_dialog.setPos(self.x(), self.y() + NODE_HEIGHT_TOTAL)

        return qtwg.QGraphicsRectItem.itemChange(self, change, data)

    def __str__(self) -> str:
        """"""
        rectangle = self.sceneBoundingRect()
        bounding_box = (
            rectangle.y(),
            rectangle.x() + rectangle.width(),
            rectangle.y() + rectangle.height(),
            rectangle.x(),
        )

        ii_names = ", ".join(self.ii_names)

        output = [
            self.label.toPlainText(),
            f"    Interactive input(s): {ii_names}",
            f"    Bounding box (NESW): {str(bounding_box)[1:-1]}",
        ]

        return "\n".join(output)


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
