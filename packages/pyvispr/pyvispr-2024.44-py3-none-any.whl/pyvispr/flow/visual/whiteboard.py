"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h
from pathlib import Path as path_t

from pyvispr.config.constant import APPEARANCE_SECTION, LINK_SMOOTH
from pyvispr.config.type import save_mode_h
from pyvispr.constant.flow.node import (
    MSG_NODE_DOCUMENTATION_NEEDED,
    MSG_NODE_IN_OUT_NEEDED,
)
from pyvispr.constant.interface.storage.path import FORMAT_EXTENSION_LENGTH
from pyvispr.constant.interface.widget.menu import WHITEBOARD_MENU
from pyvispr.extension.object.field import NonInitField_NONE
from pyvispr.extension.qt.imports import qt_e, qtcr, qtgi, qtwg
from pyvispr.extension.qt.menu import BuildMenu
from pyvispr.flow.complete.graph import graph_t
from pyvispr.flow.functional.node import state_e
from pyvispr.flow.naming import name_manager_t
from pyvispr.flow.visual.link import link_t
from pyvispr.flow.visual.node import node_t
from pyvispr.interface.storage.description import json_description_any_h
from pyvispr.interface.widget.menu import (
    link_menu_t,
    node_menu_edit_t,
    node_menu_info_t,
    nodes_menu_edit_t,
)
from pyvispr.runtime.config import APP_CONFIG
from sio_messenger import MESSENGER


@d.dataclass(slots=True, repr=False, eq=False)
class whiteboard_t(qtwg.QGraphicsView):
    name: str
    paths: dict[save_mode_h, path_t] = d.field(init=False, default_factory=dict)

    graph: graph_t = d.field(init=False, default_factory=graph_t)
    zoom_factor: h.ClassVar[float] = 1.25

    _whiteboard_menu: qtwg.QMenu | None = NonInitField_NONE()
    _node_menu_info: node_menu_info_t | None = NonInitField_NONE()
    _node_menu_edit: node_menu_edit_t | None = NonInitField_NONE()
    _nodes_menu_edit: nodes_menu_edit_t | None = NonInitField_NONE()
    _link_menu: link_menu_t | None = NonInitField_NONE()

    def __post_init__(self) -> None:
        """"""
        qtwg.QGraphicsView.__init__(self)

        self.setRenderHint(qtgi.QPainter.RenderHint.Antialiasing)
        self.setDragMode(qtwg.QGraphicsView.DragMode.RubberBandDrag)
        self.setScene(self.graph.visual)

        self._whiteboard_menu = qtwg.QMenu()
        self._node_menu_info = node_menu_info_t()
        self._node_menu_edit = node_menu_edit_t()
        self._nodes_menu_edit = nodes_menu_edit_t()
        self._link_menu = link_menu_t()
        BuildMenu(self._whiteboard_menu, WHITEBOARD_MENU, self)

    def SetNewLoadedGraph(
        self,
        description: json_description_any_h,
        /,
        *,
        should_merge: bool = False,
        from_file: path_t | None = None,
        name_manager: name_manager_t | None = None,
    ) -> None:
        """"""
        if not should_merge:
            self.Clear()
        self.graph.MergeWith(description, should_select_new_nodes=should_merge)

        if from_file is not None:
            self.RenameFromFile(from_file, name_manager)

    def RenameFromFile(
        self, path: path_t | None = None, name_manager: name_manager_t | None = None, /
    ) -> None:
        """"""
        wished_name = path.name[:-FORMAT_EXTENSION_LENGTH]
        self.name = name_manager.NewUniqueName(wished_name, in_replacement_of=self.name)
        self.paths.clear()
        self.paths["save"] = path

    def ToggleSmoothLinks(self) -> None:
        """"""
        APP_CONFIG[APPEARANCE_SECTION][LINK_SMOOTH] = not APP_CONFIG[
            APPEARANCE_SECTION
        ][LINK_SMOOTH]
        for node in self.graph.visual.nodes:
            self.graph.visual.UpdateLinkPath(node)

    def Clear(self) -> None:
        """"""
        self.graph.functional.Clear()
        self.graph.visual.Clear()
        self.graph.visual.setSceneRect(qtcr.QRectF())

    def Screenshot(self) -> qtgi.QPixmap:
        """"""
        frame = self.viewport().rect()
        output = qtgi.QPixmap(frame.size())
        painter = qtgi.QPainter(output)
        self.render(painter, output.rect().toRectF(), frame)

        return output

    def mousePressEvent(self, event: qtgi.QMouseEvent, /) -> None:
        """"""
        view_position = event.pos()
        scene_position = self.mapToScene(view_position)
        # Used to be: self.graph.views()[0].transform().
        transform = self.transform()
        item: node_t | link_t | None = None
        for current_item in self.graph.visual.items(
            scene_position, deviceTransform=transform
        ):
            if isinstance(current_item, (node_t, link_t)):
                item = current_item
                break

        if item is None:
            if event.buttons() == qt_e.MouseButton.RightButton:
                self._whiteboard_menu.exec(self.mapToGlobal(event.pos()))
            else:
                qtwg.QGraphicsView.mousePressEvent(self, event)
        elif isinstance(item, node_t):
            if event.buttons() == qt_e.MouseButton.LeftButton:
                should_make_transparent = (
                    event.modifiers() == qt_e.KeyboardModifier.AltModifier
                )
                if should_make_transparent:
                    for element in item.childItems():
                        element.setAcceptedMouseButtons(qt_e.MouseButton.NoButton)
                self._DealWithNodePressed(item, scene_position, view_position, event)
                if should_make_transparent:
                    for element in item.childItems():
                        element.setAcceptedMouseButtons(qt_e.MouseButton.AllButtons)
            elif (
                event.buttons() == qt_e.MouseButton.RightButton
            ) and item.isSelected():
                position_global = self.mapToGlobal(view_position)
                selected_action = self._nodes_menu_edit.exec(position_global)
                if selected_action in (None, self._node_menu_info.cancel_action):
                    return

                selected = tuple(
                    _elm
                    for _elm in self.graph.visual.selectedItems()
                    if isinstance(_elm, node_t)
                )
                if selected_action is self._nodes_menu_edit.invalidate_action:
                    for node in selected:
                        self.graph.functional.InvalidateNodeOutputs(
                            self.graph.functional_node_of[node]
                        )
                elif selected_action in (
                    self._nodes_menu_edit.disable_action,
                    self._nodes_menu_edit.enable_action,
                ):
                    ability = selected_action is self._nodes_menu_edit.enable_action
                    for node in selected:
                        functional = self.graph.functional_node_of[node]
                        self.graph.functional.SetNodeAbility(functional, ability)
                        self.graph.AccountForNewNodeState(functional)
                elif selected_action is self._nodes_menu_edit.remove_action:
                    for node in selected:
                        self.graph.RemoveNode(node)
        else:
            if event.buttons() == qt_e.MouseButton.LeftButton:
                self._DealWithLinkPressed(item, view_position)

    def _DealWithNodePressed(
        self,
        node: node_t,
        scene_position: qtcr.QPointF,
        view_position: qtcr.QPoint,
        event: qtgi.QMouseEvent,
        /,
    ) -> None:
        """"""
        position = node.mapFromScene(scene_position)
        if (node.in_btn is not None) and node.in_btn.contains(position):
            position_global = self.mapToGlobal(view_position)
            self.graph.ManageLinkAddition(node, False, position_global)
        elif (node.out_btn is not None) and node.out_btn.contains(position):
            position_global = self.mapToGlobal(view_position)
            self.graph.ManageLinkAddition(node, True, position_global)
        elif (node.config_btn is not None) and node.config_btn.contains(position):
            node.ToggleIIDialog()
        elif node.state_btn.contains(position):
            position_global = self.mapToGlobal(view_position)
            selected_action = self._node_menu_info.exec(position_global)
            if selected_action in (None, self._node_menu_info.cancel_action):
                return

            if selected_action is self._node_menu_info.documentation_action:
                MESSENGER.Transmit(
                    MSG_NODE_DOCUMENTATION_NEEDED,
                    self.graph.functional_node_of[node].catalog_name,
                )
            elif selected_action is self._node_menu_info.in_out_action:
                MESSENGER.Transmit(MSG_NODE_IN_OUT_NEEDED, node)
        elif node.remove_btn.contains(position):
            position_global = self.mapToGlobal(view_position)
            self._node_menu_edit.Update(
                self.graph.functional_node_of[node].state is state_e.disabled
            )
            selected_action = self._node_menu_edit.exec(position_global)
            if selected_action in (None, self._node_menu_edit.cancel_action):
                return

            if selected_action is self._node_menu_edit.invalidate_action:
                self.graph.functional.InvalidateNodeOutputs(
                    self.graph.functional_node_of[node]
                )
            elif selected_action is self._node_menu_edit.disable_action:
                functional = self.graph.functional_node_of[node]
                self.graph.functional.ToggleNodeAbility(functional)
                self.graph.AccountForNewNodeState(functional)
            elif selected_action is self._node_menu_edit.remove_action:
                self.graph.RemoveNode(node)
        else:
            qtwg.QGraphicsView.mousePressEvent(self, event)

    def _DealWithLinkPressed(self, link: link_t, view_position: qtcr.QPoint, /) -> None:
        """"""
        source = self.graph.functional_node_of[link.source]
        target = self.graph.functional_node_of[link.target]
        socket_pairs = self.graph.functional.links[source][target]

        position_global = self.mapToGlobal(view_position)
        self._link_menu.Update(socket_pairs)
        selected_action = self._link_menu.exec(position_global)
        if selected_action in (None, self._link_menu.cancel_action):
            return

        if (self._link_menu.n_links == 1) or (
            selected_action is self._link_menu.remove_all_action
        ):
            self.graph.RemoveLink(link)
        else:
            which = self._link_menu.remove_actions.index(selected_action)
            socket_pair = socket_pairs[which]
            self.graph.RemoveLink(
                link, output_name=socket_pair[0], intake_name=socket_pair[1]
            )

    def wheelEvent(self, event, /) -> None:
        """"""
        if event.modifiers() == qt_e.KeyboardModifier.ControlModifier:
            scale_factor = (
                1 / whiteboard_t.zoom_factor
                if event.angleDelta().y() > 0
                else whiteboard_t.zoom_factor
            )
            self.scale(scale_factor, scale_factor)
        else:
            qtwg.QGraphicsView.wheelEvent(self, event)

    def InvalidateWorkflow(self) -> None:
        """"""
        self.graph.functional.Invalidate()

    def SelectOrNotAllNodes(self, should_select: bool, /) -> None:
        """"""
        self.graph.visual.SelectOrNotAllNodes(should_select)

    def ToggleGridVisibility(self) -> None:
        """"""
        self.graph.visual.ToggleGridVisibility()

    def AlignNodesOnGrid(self) -> None:
        """"""
        self.graph.visual.AlignOnGrid()

    def RunWorkflow(self) -> None:
        """"""
        # TODO: When called from the whiteboard context menu, this method is of course
        #     called directly, i.e. w/o inserting a blank line in the log area, and w/o
        #     updating the status bar. Turn these tasks into message actions.
        self.graph.Run(workflow=self.name)


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
