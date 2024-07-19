"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h
from datetime import datetime as date_time_t

from logger_36.instance.loggers import LOGGERS
from logger_36.logger import LogException
from pyvispr.config.appearance.color import (
    BUTTON_BRUSH_STATE_DISABLED,
    BUTTON_BRUSH_STATE_DOING,
    BUTTON_BRUSH_STATE_DONE,
    BUTTON_BRUSH_STATE_ERROR,
    BUTTON_BRUSH_STATE_TODO,
    INOUT_BRUSH_ACTIVE,
    INOUT_BRUSH_INACTIVE,
    LINK_PEN_EMPTY,
    LINK_PEN_FULL,
    LINK_PEN_HALF,
    NODE_BRUSH_RESTING,
    NODE_BRUSH_RUNNING,
)
from pyvispr.constant.flow.node import (
    MSG_NEW_NODE_INTAKE,
    MSG_NEW_NODE_NAME_REQUESTED,
    MSG_NEW_NODE_OUTPUT,
    MSG_NEW_NODE_STATE,
    UNIQUE_NAME_INTAKE,
)
from pyvispr.constant.flow.value import VALUE_NOT_SET
from pyvispr.exception.graph import InvalidJSONFormatError
from pyvispr.extension.object.type import TypesAreCompatible
from pyvispr.extension.qt.imports import qtcr, qtwg
from pyvispr.flow.complete.socket import active_socket_t
from pyvispr.flow.descriptive.intake import intake_t
from pyvispr.flow.functional.graph import ShouldIgnorePredecessorValue
from pyvispr.flow.functional.graph import graph_t as functional_graph_t
from pyvispr.flow.functional.node import node_t as functional_node_t
from pyvispr.flow.functional.node import state_e
from pyvispr.flow.visual.graph import graph_t as visual_graph_t
from pyvispr.flow.visual.link import link_t
from pyvispr.flow.visual.node import node_t as visual_node_t
from pyvispr.interface.storage.description import (
    json_description_2024a_h,
    json_description_any_h,
    json_description_h,
)
from pyvispr.runtime.catalog import NODE_CATALOG
from sio_messenger import MESSENGER

_CANALS_AND_ACTIONS = {
    MSG_NEW_NODE_NAME_REQUESTED: "ProcessNodeRenamingRequest",
    MSG_NEW_NODE_STATE: "AccountForNewNodeState",
    MSG_NEW_NODE_INTAKE: "AccountForNewNodeIntake",
    MSG_NEW_NODE_OUTPUT: "AccountForNewNodeOutput",
}


@d.dataclass(slots=True, repr=False, eq=False)
class graph_t:
    functional: functional_graph_t = d.field(
        init=False, default_factory=functional_graph_t
    )
    visual: visual_graph_t = d.field(init=False, default_factory=visual_graph_t)
    functional_node_of: dict[visual_node_t, functional_node_t] = d.field(
        init=False, default_factory=dict
    )
    visual_node_of: dict[functional_node_t, visual_node_t] = d.field(
        init=False, default_factory=dict
    )

    _active_socket: active_socket_t = d.field(
        init=False, default_factory=active_socket_t
    )

    def __post_init__(self) -> None:
        """"""
        for canal, action in _CANALS_AND_ACTIONS.items():
            MESSENGER.AddCanalWithAction(canal, getattr(self, action))

    @classmethod
    def __NewFromJsonDescription__(
        cls, description: json_description_any_h, /
    ) -> h.Self:
        """"""
        output = cls()
        output.PopulateFromJsonDescription(description)
        return output

    def __DescriptionForJSON__(self) -> json_description_h:
        """"""
        return self.DescriptionForJSON(False)

    def __str__(self) -> str:
        """"""
        return f"{self.functional}\n\n{self.visual}"

    def PopulateFromJsonDescription(
        self,
        description: json_description_any_h,
        /,
        *,
        should_select_new_nodes: bool = False,
    ) -> None:
        """"""
        PopulateFromJsonDescription_s = (self._PopulateFromJsonDescription_2024a,)
        logger = LOGGERS.active
        for PopulateFromJsonDescription in PopulateFromJsonDescription_s:
            try:
                PopulateFromJsonDescription(
                    description, should_select_new_nodes=should_select_new_nodes
                )
            except:
                if logger is not None:
                    logger.warning(
                        "Workflow using an old JSON format; "
                        "Please consider re-saving to replace with latest format."
                    )
                    logger = None
                continue
            else:
                return

        raise InvalidJSONFormatError(f"No JSON format found for:\n{description}")

    def _PopulateFromJsonDescription_2024a(
        self,
        description: json_description_2024a_h,
        /,
        *,
        should_select_new_nodes: bool = False,
    ) -> None:
        """"""
        nodes, links = description

        new_name_for_old = {}
        new_visuals = []
        for (
            stripe,
            wished_name,
            is_disabled,
            ii_values,
            ii_is_visible,
            position_x,
            position_y,
        ) in nodes:
            functional, visual = self.AddNode(
                stripe,
                wished_name=wished_name,
                is_disabled=is_disabled,
                ii_values=ii_values,
                ii_is_visible=ii_is_visible,
                position_x=position_x,
                position_y=position_y,
                and_return_it=True,
            )
            new_name_for_old[wished_name] = functional.name
            self.AccountForNewNodeState(functional)
            if should_select_new_nodes:
                new_visuals.append(visual)

        for source, target, *sockets in links:
            self.AddLinks(new_name_for_old[source], new_name_for_old[target], sockets)

        for visual in new_visuals:
            visual.setSelected(True)

    def DescriptionForJSON(self, only_selected: bool, /) -> json_description_h:
        """"""
        if only_selected:
            NodeShouldBeIncluded = lambda _elm: _elm.isSelected()
            LinkShouldBeIncluded = (
                lambda _elm: _elm.source.isSelected() and _elm.target.isSelected()
            )
        else:
            NodeShouldBeIncluded = LinkShouldBeIncluded = lambda _elm: True

        nodes = tuple(
            (
                self.functional_node_of[_elm].catalog_name,
                self.functional_node_of[_elm].name,
                self.functional_node_of[_elm].state is state_e.disabled,
                _elm.IIValue(self.functional_node_of[_elm].catalog_name),
                (_elm.ii_dialog is not None) and _elm.ii_dialog.isVisible(),
                _elm.x(),
                _elm.y(),
            )
            for _elm in self.visual.nodes
            if NodeShouldBeIncluded(_elm)
        )
        links = tuple(
            (
                self.functional_node_of[_elm.source].name,
                self.functional_node_of[_elm.target].name,
            )
            + tuple(
                self.functional.links[self.functional_node_of[_elm.source]][
                    self.functional_node_of[_elm.target]
                ],
            )
            for _elm in self.visual.links
            if LinkShouldBeIncluded(_elm)
        )
        return nodes, links

    def AddNode(
        self,
        stripe: str,
        /,
        *,
        wished_name: str | None = None,
        is_disabled: bool = False,
        ii_values: dict[str, h.Any] | None = None,
        ii_is_visible: bool = False,
        position_x: float | None = None,
        position_y: float | None = None,
        and_return_it: bool = False,
    ) -> tuple[functional_node_t, visual_node_t] | None:
        """"""
        try:
            functional = self.functional.AddNode(
                stripe, wished_name=wished_name, and_return_it=True
            )
        except Exception as exception:
            # TODO: Properly log every errors/exceptions in self.functional.AddNode,
            #     then remove logging here; just return.
            logger = LOGGERS.active
            logger.error(
                "The following message might not describe the actual cause of error, "
                "but a consequence of it.\n"
                "Look for messages above for the actual cause."
            )
            LogException(exception, logger=logger)
            return

        visual = self.visual.AddNodeForFunctional(
            functional,
            self.InvalidateThisNodeOutputs(functional),
            and_return_it=True,
        )

        self.functional_node_of[visual] = functional
        self.visual_node_of[functional] = visual

        if is_disabled:
            functional.state = state_e.disabled
        if ii_values is not None:
            for intake_name, value in ii_values.items():
                visual.SetIIValue(intake_name, value, functional.catalog_name)
        if position_x is not None:
            visual.setPos(position_x, position_y)
        if not ((visual.ii_dialog is None) or ii_is_visible):
            visual.ToggleIIDialog()

        if and_return_it:
            return functional, visual

    def RemoveNode(self, node: visual_node_t, /) -> None:
        """"""
        self.functional.RemoveNode(self.functional_node_of[node])
        self.visual.RemoveNode(node)

    def InvalidateThisNodeOutputs(
        self, node: functional_node_t, /
    ) -> h.Callable[[], None]:
        """"""
        return lambda: self.functional.InvalidateNodeOutputs(node)

    def AddLink(
        self,
        source: visual_node_t,
        output_name: str,
        target: visual_node_t,
        intake_name: str,
        /,
    ) -> None:
        """"""
        functional_source = self.functional_node_of[source]
        functional_target = self.functional_node_of[target]
        self.functional.AddLink(
            functional_source, output_name, functional_target, intake_name
        )
        link = self.visual.AddLink(source, target, should_return_it=True)
        self.SetOutboundLinkAppearanceOfNode(functional_source)
        link.UpdateTooltip(self.functional.links[functional_source][functional_target])

    def AddLinks(
        self, source: str, target: str, sockets: tuple[tuple[str, str], ...]
    ) -> None:
        """"""
        for visual in self.visual.nodes:
            current_name = self.functional_node_of[visual].name
            if current_name == source:
                source = visual
            elif current_name == target:
                target = visual
            if isinstance(source, visual_node_t) and isinstance(target, visual_node_t):
                break

        for output_name, intake_name in sockets:
            self.AddLink(source, output_name, target, intake_name)

    def RemoveLink(
        self,
        link: link_t,
        /,
        output_name: str | None = None,
        intake_name: str | None = None,
    ) -> None:
        """"""
        functional_source = self.functional_node_of[link.source]
        functional_target = self.functional_node_of[link.target]
        self.functional.RemoveLink(
            functional_source, output_name, functional_target, intake_name
        )
        links = self.functional.links
        if links[functional_source][functional_target].__len__() > 0:
            self.SetOutboundLinkAppearanceOfNode(functional_source)
            link.UpdateTooltip(links[functional_source][functional_target])
        else:
            self.visual.RemoveLink(link)

    def MergeWith(
        self, other: json_description_any_h, /, *, should_select_new_nodes: bool = False
    ) -> None:
        """"""
        self.PopulateFromJsonDescription(
            other, should_select_new_nodes=should_select_new_nodes
        )

    def Run(
        self,
        /,
        *,
        workflow: str | None = None,
        script_accessor: h.TextIO = None,
    ) -> None:
        """"""
        for node in self.visual.nodes:
            functional = self.functional_node_of[node]
            if functional.state is state_e.todo:
                self.SetInitialIntakeValues(node, functional)

        un_run_nodes = self.functional.Run(
            workflow=workflow, script_accessor=script_accessor
        )

        if un_run_nodes.__len__() > 0:
            un_run_nodes = ", ".join(sorted(_elm.name for _elm in un_run_nodes))
            if script_accessor is None:
                LOGGERS.active.error(f"Un-run nodes: {un_run_nodes}.")
            else:
                message = (
                    f"Workflow saving as a script was incomplete "
                    f"due to the following node(s) not being runnable:\n"
                    f"{un_run_nodes}."
                )
                LOGGERS.active.error(message)
                qtwg.QMessageBox.critical(
                    None,
                    "Workflow Saving as Script Error",
                    message,
                )

    def SetInitialIntakeValues(
        self, visual: visual_node_t, functional: functional_node_t, /
    ) -> None:
        """"""
        ii_widgets = visual.ii_widgets
        has_ii_widgets = ii_widgets is not None

        node_description = NODE_CATALOG[functional.catalog_name]
        for intake_name, description in node_description.intakes.items():
            feeding_socket = self.functional.links.IntakeSocketIsFree(
                functional, intake_name, should_return_socket=True
            )
            if feeding_socket is not None:
                predecessor, output_name = feeding_socket
                if ShouldIgnorePredecessorValue(predecessor, output_name, description):
                    functional.SetIntakeValue(intake_name, description.default_value)
                continue

            if has_ii_widgets and (intake_name in visual.ii_names):
                value_as_str = ii_widgets[intake_name].Text()
                if value_as_str.__len__() > 0:
                    expected_type = description.type
                    value, issues = expected_type.InterpretedValueOf(value_as_str)
                    if issues.__len__() > 0:
                        issues = "\n".join(issues)
                        LOGGERS.active.error(
                            f"Invalid value of {functional.name}.{intake_name}:\n"
                            f"{issues}"
                        )
                        value = VALUE_NOT_SET
                elif description.has_default:
                    value = description.default_value
                else:
                    value = VALUE_NOT_SET
            elif description.has_default:
                value = description.default_value
            else:
                value = VALUE_NOT_SET

            functional.SetIntakeValue(intake_name, value)

    def SetOutboundLinkAppearanceOfNode(self, node: functional_node_t, /) -> None:
        """"""
        empty = []
        half = []
        full = []
        for successor, socket_pairs in self.functional.links.FirstDegreeSuccessors(
            node
        ):
            n_with_values = sum(
                1 if node.outputs[_elm].has_value else 0 for _elm, _ in socket_pairs
            )
            if n_with_values == 0:
                empty.append(successor)
            elif n_with_values < socket_pairs.__len__():
                half.append(successor)
            else:
                full.append(successor)

        for successors, pen in zip(
            (empty, half, full), (LINK_PEN_EMPTY, LINK_PEN_HALF, LINK_PEN_FULL)
        ):
            for successor in successors:
                for link in self.visual.links:
                    if (self.functional_node_of[link.source] is node) and (
                        self.functional_node_of[link.target] is successor
                    ):
                        link.setPen(pen)

        found = None
        for visual in self.visual.nodes:
            if self.functional_node_of[visual] is node:
                found = visual
                break
        if found is not None:
            # This happens when instantiating from json.
            as_str = "\n".join(
                f"{_nme} = {_vle}" for _nme, _vle in node.outputs.items()
            )
            found.out_btn.setToolTip(as_str)

        qtcr.QCoreApplication.processEvents()

    def ManageLinkAddition(
        self, node: visual_node_t, node_is_source: bool, position: qtcr.QPoint, /
    ) -> None:
        """"""
        if self._active_socket.node is None:
            self._SetActiveSocket(node, node_is_source, position)
            return

        same_node = node is self._active_socket.node
        same_kind = (node_is_source and self._active_socket.is_source) or not (
            node_is_source or self._active_socket.is_source
        )
        if same_node or same_kind:
            if same_node and same_kind:
                if node_is_source:
                    button = self._active_socket.node.out_btn
                else:
                    button = self._active_socket.node.in_btn
                self._active_socket.node = None
                button.setBrush(INOUT_BRUSH_INACTIVE)
            return

        source, source_name, target, target_name = (
            self._LinkDetailsBetweenNodeAndActive(node, node_is_source, position)
        )
        if source is None:
            return

        self.AddLink(source, source_name, target, target_name)
        self._active_socket.node = None

    def _SetActiveSocket(
        self, node: visual_node_t, node_is_source: bool, position: qtcr.QPoint, /
    ) -> None:
        """"""
        functional = self.functional_node_of[node]
        description = NODE_CATALOG[functional.catalog_name]
        if node_is_source:
            sockets = description.outputs
            possible_names = description.output_names
            button = node.out_btn
        else:
            sockets = description.intakes
            links = self.functional.links
            possible_names = tuple(
                _nme
                for _nme in functional.intakes
                if links.IntakeSocketIsFree(functional, _nme)
            )
            button = node.in_btn
        possible_names = tuple(
            filter(lambda _elm: _elm != UNIQUE_NAME_INTAKE, possible_names)
        )

        if possible_names.__len__() > 1:
            selected = _SelectedSocketName(possible_names, position)
        elif possible_names.__len__() > 0:
            selected = possible_names[0]
        else:
            selected = None
        if selected is None:
            return

        socket = sockets[selected]
        if isinstance(socket, intake_t):
            stripe = socket.type
        else:
            stripe = socket
        self._active_socket.node = node
        self._active_socket.is_source = node_is_source
        self._active_socket.name = selected
        self._active_socket.type = stripe
        button.setBrush(INOUT_BRUSH_ACTIVE)

    def _LinkDetailsBetweenNodeAndActive(
        self, node: visual_node_t, node_is_source: bool, position: qtcr.QPoint, /
    ) -> tuple[
        visual_node_t | None,
        str | None,
        visual_node_t | None,
        str | None,
    ]:
        """"""
        functional = self.functional_node_of[node]
        description = NODE_CATALOG[functional.catalog_name]
        if node_is_source:
            source = node
            source_name = None
            target, _, target_name, target_type = self._active_socket.AsTuple()
            possible_names = tuple(
                _nme
                for _nme, _tpe in description.outputs.items()
                if TypesAreCompatible(_tpe, target_type)
            )
        else:
            source, _, source_name, source_type = self._active_socket.AsTuple()
            target = node
            target_name = None
            links = self.functional.links
            possible_names = tuple(
                _nme
                for _nme in functional.intakes
                if links.IntakeSocketIsFree(functional, _nme)
                and TypesAreCompatible(description.intakes[_nme].type, source_type)
            )
        possible_names = tuple(
            filter(lambda _elm: _elm != UNIQUE_NAME_INTAKE, possible_names)
        )
        if (n_names := possible_names.__len__()) == 0:
            return None, None, None, None

        if n_names > 1:
            selected = _SelectedSocketName(possible_names, position)
            if selected is None:
                return None, None, None, None
        else:
            selected = possible_names[0]
        if node_is_source:
            source_name = selected
            button = target.in_btn
        else:
            target_name = selected
            button = source.out_btn
        button.setBrush(INOUT_BRUSH_INACTIVE)

        return source, source_name, target, target_name

    def Clear(self) -> None:
        """"""
        self.functional.Clear()
        self.visual.Clear()

    def ProcessNodeRenamingRequest(
        self, node: visual_node_t, wished_name: str, /
    ) -> None:
        """"""
        functional = self.functional_node_of[node]
        self.functional.RenameNode(functional, wished_name)
        if functional.name != wished_name:
            node.SetNewName(functional.name)

    def AccountForNewNodeState(self, node: functional_node_t, /) -> None:
        """"""
        if node.state is state_e.disabled:
            message = "Disabled"
            brushes = (NODE_BRUSH_RESTING, BUTTON_BRUSH_STATE_DISABLED)
        elif node.state is state_e.todo:
            message = "Needs Running"
            brushes = (NODE_BRUSH_RESTING, BUTTON_BRUSH_STATE_TODO)
        elif node.state is state_e.doing:
            message = f"Running since {date_time_t.now()}"
            brushes = (NODE_BRUSH_RUNNING, BUTTON_BRUSH_STATE_DOING)
        elif node.state is state_e.done:
            message = f"Run Successfully ({date_time_t.now()})"
            brushes = (NODE_BRUSH_RESTING, BUTTON_BRUSH_STATE_DONE)
        else:  # state_e.done_with_error
            message = f"Run with ERROR ({date_time_t.now()})"
            brushes = (NODE_BRUSH_RESTING, BUTTON_BRUSH_STATE_ERROR)

        for current in self.visual.nodes:
            if self.functional_node_of[current] is node:
                current.setBrush(brushes[0])
                current.state_btn.setBrush(brushes[1])
                current.state_btn.setToolTip(message)
                qtcr.QCoreApplication.processEvents()
                break

    def AccountForNewNodeIntake(self, node: functional_node_t, /) -> None:
        """"""
        found = None
        for visual in self.visual.nodes:
            if self.functional_node_of[visual] is node:
                found = visual
                break

        if found is not None:
            # This happens when instantiating from json.
            as_str = "\n".join(
                f"{_nme} = {_vle}" for _nme, _vle in node.intakes.items()
            )
            found.in_btn.setToolTip(as_str)

    def AccountForNewNodeOutput(self, node: functional_node_t, /) -> None:
        """"""
        empty = []
        half = []
        full = []
        for successor, socket_pairs in self.functional.links.FirstDegreeSuccessors(
            node
        ):
            n_with_values = sum(
                1 if node.outputs[_elm].has_value else 0 for _elm, _ in socket_pairs
            )
            if n_with_values == 0:
                empty.append(successor)
            elif n_with_values < socket_pairs.__len__():
                half.append(successor)
            else:
                full.append(successor)

        for successors, pen in zip(
            (empty, half, full), (LINK_PEN_EMPTY, LINK_PEN_HALF, LINK_PEN_FULL)
        ):
            for successor in successors:
                for link in self.visual.links:
                    if (self.functional_node_of[link.source] is node) and (
                        self.functional_node_of[link.target] is successor
                    ):
                        link.setPen(pen)

        found = None
        for visual in self.visual.nodes:
            if self.functional_node_of[visual] is node:
                found = visual
                break
        if found is not None:
            # This happens when instantiating from json.
            as_str = "\n".join(
                f"{_nme} = {_vle}" for _nme, _vle in node.outputs.items()
            )
            found.out_btn.setToolTip(as_str)

        qtcr.QCoreApplication.processEvents()


def _SelectedSocketName(
    possible_names: tuple[str, ...], position: qtcr.QPoint, /
) -> str | None:
    """"""
    menu = qtwg.QMenu()
    actions = tuple(menu.addAction(_elm) for _elm in possible_names)
    selected_action = menu.exec(position)
    if selected_action is None:
        return None

    return possible_names[actions.index(selected_action)]


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
