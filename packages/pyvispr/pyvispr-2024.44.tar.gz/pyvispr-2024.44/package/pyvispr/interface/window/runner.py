"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

from __future__ import annotations  # For use in static method.

import dataclasses as d
from pathlib import Path as path_t

from logger_36.instance.loggers import LOGGERS
from pyvispr import __version__
from pyvispr.config.appearance.color import PLAIN_BLUE, color_e
from pyvispr.config.type import load_mode_h, save_mode_h
from pyvispr.constant.app import APP_NAME, DOCUMENTATION_ADDRESS, SOURCE_ADDRESS
from pyvispr.constant.flow.node import (
    MSG_NODE_DOCUMENTATION_NEEDED,
    MSG_NODE_IN_OUT_NEEDED,
)
from pyvispr.constant.interface.widget.menu import MAIN_MENUS
from pyvispr.constant.interface.widget.whiteboard import WHITEBOARD_DEFAULT_NAME
from pyvispr.exception.catalog import NodeNotFoundError
from pyvispr.exception.graph import LoadSaveError
from pyvispr.extension.object.field import NON_INIT_FIELD, NonInitField_NONE
from pyvispr.extension.qt.graphics_view import ViewRegion
from pyvispr.extension.qt.imports import qt_e, qtcr, qtgi, qtwg
from pyvispr.extension.qt.menu import AddEntriesToMenu, BuildMenu, entry_t
from pyvispr.flow.naming import name_manager_t
from pyvispr.flow.visual.node import node_t
from pyvispr.flow.visual.whiteboard import whiteboard_t
from pyvispr.interface.storage.description import json_description_h
from pyvispr.interface.storage.loading import LoadWorkflow
from pyvispr.interface.storage.stowing import (
    SaveWorkflow,
    SaveWorkflowAsScreenshot,
    SaveWorkflowAsScript,
)
from pyvispr.interface.widget.about import about_t
from pyvispr.interface.widget.config import config_wgt_t
from pyvispr.interface.widget.doc_area import doc_wgt_t
from pyvispr.interface.widget.list.node import node_list_wgt_t
from pyvispr.interface.widget.log_area import log_wgt_t, per_whiteboard_wgt_t
from pyvispr.runtime.backend import SCREEN_BACKEND
from pyvispr.runtime.catalog import NODE_CATALOG
from pyvispr.runtime.config import APP_CONFIG
from sio_messenger import MESSENGER

_DEFAULT_TAB_COLOR: color_e | None = None


@d.dataclass(slots=True, repr=False, eq=False)
class runner_wdw_t(qtwg.QMainWindow):
    node_list: node_list_wgt_t = NON_INIT_FIELD
    recent_list: node_list_wgt_t = NON_INIT_FIELD
    most_used_list: node_list_wgt_t = NON_INIT_FIELD
    name_manager: name_manager_t = d.field(init=False, default_factory=name_manager_t)
    active_whiteboard: whiteboard_t = NON_INIT_FIELD
    clipboard: json_description_h | None = NonInitField_NONE()
    #
    tabs: qtwg.QTabWidget = NON_INIT_FIELD
    log_area: log_wgt_t = NON_INIT_FIELD
    doc_area: doc_wgt_t = NON_INIT_FIELD
    #
    load_recent_menu: qtwg.QMenu = NON_INIT_FIELD
    status_bar: qtwg.QStatusBar = NON_INIT_FIELD

    @property
    def active_paths(self) -> dict[save_mode_h, path_t]:
        """"""
        return self.active_whiteboard.paths

    def __post_init__(self) -> None:
        """"""
        qtwg.QMainWindow.__init__(self)
        self.setWindowTitle(APP_NAME)

        node_list = node_list_wgt_t(element_name="Nodes")
        recent_list = node_list_wgt_t(
            element_name="Recent",
            source=APP_CONFIG.recent_nodes,
            should_be_sorted=False,
        )
        most_used_list = node_list_wgt_t(
            element_name="Most Used",
            source=APP_CONFIG.most_used_nodes,
            should_be_sorted=False,
        )
        self.node_list = node_list
        self.recent_list = recent_list
        self.most_used_list = most_used_list

        name = self.name_manager.NewUniqueName(WHITEBOARD_DEFAULT_NAME)
        whiteboard = whiteboard_t(name=name)

        log_area = log_wgt_t(whiteboard)
        self.log_area = log_area

        doc_area = doc_wgt_t()
        self.doc_area = doc_area

        tabs = qtwg.QTabWidget()
        tabs.addTab(whiteboard, whiteboard.name)
        tabs.addTab(log_area, "Messages")
        tabs.addTab(doc_area, "Documentation")
        tabs.setStyleSheet("QTabWidget::tab-bar {alignment: center;}")
        tabs.setMovable(True)
        tabs.setTabsClosable(True)
        self.tabs = tabs

        global _DEFAULT_TAB_COLOR
        _DEFAULT_TAB_COLOR = tabs.tabBar().tabTextColor(0)
        self._SetActiveWhiteboard(whiteboard, 0)

        self._BuildMenuBar()
        self.status_bar = self.statusBar()

        layout = qtwg.QGridLayout()
        layout.addWidget(node_list.filter_wgt, 0, 0)
        layout.addWidget(node_list, 1, 0, 3, 1)
        layout.addWidget(
            qtwg.QLabel('<span style="font-weight:bold; color:blue">Recent</span>'),
            0,
            1,
        )
        layout.addWidget(recent_list, 1, 1)
        layout.addWidget(
            qtwg.QLabel('<span style="font-weight:bold; color:blue">Most Used</span>'),
            2,
            1,
        )
        layout.addWidget(most_used_list, 3, 1)
        layout.addWidget(tabs, 0, 2, 4, 1)

        central = qtwg.QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        MESSENGER.AddCanalWithAction(
            MSG_NODE_DOCUMENTATION_NEEDED,
            self.ShowNodeDocumentation,
            should_allow_existing_canal=False,
        )
        MESSENGER.AddCanalWithAction(
            MSG_NODE_IN_OUT_NEEDED,
            self.ShowNodeIntakesAndOutputs,
            should_allow_existing_canal=False,
        )
        for list_ in (node_list, recent_list, most_used_list):
            SCREEN_BACKEND.AddMessageCanal(
                list_, "itemClicked", self.ReactToNodeSelectionInList
            )
        SCREEN_BACKEND.AddMessageCanal(
            tabs, "currentChanged", self.ReactToWhiteboardSwitch
        )
        SCREEN_BACKEND.AddMessageCanal(tabs, "tabCloseRequested", self.RemoveWhiteboard)

    @staticmethod
    def Instance() -> runner_wdw_t | None:
        """"""
        for widget in qtwg.QApplication.topLevelWidgets():
            if isinstance(widget, runner_wdw_t):
                return widget

        return None

    def _BuildMenuBar(self) -> None:
        """"""
        menu_bar = self.menuBar()

        look_for = "Load Recent..."
        found = 0
        for text, entries in MAIN_MENUS.items():
            menu = menu_bar.addMenu(text)
            entries = BuildMenu(menu, entries, self, should_return_entries=look_for)
            if look_for in entries:
                self.load_recent_menu = entries[look_for]
                found += 1

        if found != 1:
            raise RuntimeError(f'No, or too many, "{look_for}" menu(s) found.')

    def AddWhiteboard(self) -> None:
        """"""
        name = self.name_manager.NewUniqueName(WHITEBOARD_DEFAULT_NAME)
        whiteboard = whiteboard_t(name=name)

        self.tabs.insertTab(0, whiteboard, whiteboard.name)
        self._SetActiveWhiteboard(whiteboard, 0)

    def RemoveWhiteboard(self, index: int, /) -> None:
        """"""
        tabs = self.tabs
        if tabs.__len__() < 4:
            return

        widget = tabs.widget(index)
        if isinstance(widget, whiteboard_t):
            self.name_manager.RemoveName(tabs.tabText(index))
            tabs.removeTab(index)
            self.log_area.RemoveAreaOfWhiteboard(widget)
            for idx in range(tabs.count()):
                new_widget = tabs.widget(idx)
                if isinstance(new_widget, whiteboard_t):
                    self._SetActiveWhiteboard(new_widget, idx)
                    break

    def _SetActiveWhiteboard(
        self, whiteboard: whiteboard_t, index: int, /, *, should_set_index: bool = True
    ) -> None:
        """"""
        self.active_whiteboard = whiteboard
        self.active_whiteboard.setFocus()

        tabs = self.tabs
        tab_bar = tabs.tabBar()

        for current in range(tabs.count()):
            if current == index:
                color = PLAIN_BLUE
            else:
                color = _DEFAULT_TAB_COLOR
            tab_bar.setTabTextColor(current, color)

        if should_set_index:
            tabs.setCurrentIndex(index)
        self.log_area.SwitchAreaForWhiteboard(whiteboard)

    def AddNode(self, name: str, /) -> None:
        """"""
        whiteboard = self.active_whiteboard
        returned = whiteboard.graph.AddNode(name, and_return_it=True)
        if returned is None:
            self.tabs.setCurrentWidget(self.log_area)
            return
        visual = returned[1]
        center = ViewRegion(whiteboard.graph.visual.view).center()
        shift = qtcr.QPointF(visual.rect().width() / 2.0, visual.rect().height() / 2.0)
        visual.setPos(center - shift)

        APP_CONFIG.UpdateRecentNodes(name)
        APP_CONFIG.UpdateMostUsedNodes(name)
        self.recent_list.UpdateSource(APP_CONFIG.recent_nodes)
        self.most_used_list.UpdateSource(APP_CONFIG.most_used_nodes)

    def CopySubGraph(self) -> None:
        """"""
        if isinstance(self.tabs.currentWidget(), whiteboard_t):
            self.clipboard = self.active_whiteboard.graph.DescriptionForJSON(True)
        else:
            current = qtwg.QApplication.focusWidget()
            if isinstance(current, per_whiteboard_wgt_t) or (
                current is self.doc_area.content_wgt
            ):
                if current.textCursor().hasSelection():
                    current.copy()

    def CutSubGraph(self) -> None:
        """"""
        if isinstance(self.tabs.currentWidget(), whiteboard_t):
            self.CopySubGraph()

            graph = self.active_whiteboard.graph
            for item in graph.visual.selectedItems():
                if isinstance(item, node_t):
                    graph.RemoveNode(item)

    def PasteSubGraph(self) -> None:
        """"""
        if isinstance(self.tabs.currentWidget(), whiteboard_t):
            whiteboard = self.active_whiteboard
            whiteboard.SelectOrNotAllNodes(False)
            whiteboard.graph.MergeWith(self.clipboard, should_select_new_nodes=True)

    def RunWorkflow(self) -> None:
        """"""
        tabs = self.tabs
        index = tabs.indexOf(self.active_whiteboard)
        workflow = tabs.tabText(index)

        self.log_area.InsertLineBreak()
        self.status_bar.showMessage(f"WORKFLOW {workflow}...")
        self.active_whiteboard.RunWorkflow()
        self.status_bar.showMessage("WORKFLOW done")

    def ReactToWhiteboardSwitch(self, index: int, /) -> None:
        """"""
        widget = self.tabs.widget(index)
        if isinstance(widget, whiteboard_t):
            self._SetActiveWhiteboard(widget, index, should_set_index=False)

    def ReactToNodeSelectionInList(self, item: qtwg.QListWidgetItem, /) -> None:
        """"""
        name = item.text()
        if isinstance(self.tabs.currentWidget(), whiteboard_t):
            self.AddNode(name)
        else:
            self.ShowNodeDocumentation(name)

    def ShowNodeDocumentation(self, stripe: str, /) -> None:
        """"""
        try:
            description = NODE_CATALOG[stripe]
        except NodeNotFoundError:
            description = None

        doc_area = self.doc_area
        doc_area.content_wgt.clear()
        if description is None:
            doc_area.content_wgt.setText(f"Node {stripe}: Not found in catalog.")
        else:
            description.Activate()
            doc_area.content_wgt.setText(description.AsStr())
        tabs = self.tabs
        if tabs.widget(tabs.currentIndex()) is not doc_area:
            tabs.setCurrentIndex(tabs.indexOf(doc_area))

    def ShowNodeIntakesAndOutputs(self, node: node_t, /) -> None:
        """"""
        functional = self.active_whiteboard.graph.functional_node_of[node]
        logger = LOGGERS.active

        logger.info(f"NODE {functional.name}")
        for name, elements in zip(
            ("Input(s)", "Output(s)"), (functional.intakes, functional.outputs)
        ):
            as_str = []
            for key, value in elements.items():
                as_str.append(f"{key}: {value}")
            as_str = "\n".join(as_str)
            logger.info(f"{name}\n{as_str}")
        logger.info(
            f"=> Needs running: {functional.needs_running}, Can run: {functional.can_run}"
        )

        log_area = self.log_area
        tabs = self.tabs
        if tabs.widget(tabs.currentIndex()) is not log_area:
            tabs.setCurrentIndex(tabs.indexOf(log_area))

    def LoadOrSaveWorkflow(
        self,
        operation: load_mode_h | save_mode_h,
        /,
        *,
        recent: path_t | None = None,
    ) -> None:
        """"""
        filename = None
        if operation in ("save as script", "save as screenshot"):
            operation: save_mode_h
            last_saving = self.active_paths.get(
                operation, APP_CONFIG.LastSavingFolder(operation)
            )
        else:
            last_saving = None

        active_whiteboard = self.active_whiteboard
        active_graph = active_whiteboard.graph

        if operation == "load":
            filename = LoadWorkflow(
                active_whiteboard,
                APP_CONFIG.last_loading_folder,
                self.name_manager,
                self,
                status_bar=self.status_bar,
            )
        elif operation == "load recent":
            filename = LoadWorkflow(
                active_whiteboard,
                recent,
                self.name_manager,
                self,
                status_bar=self.status_bar,
            )
        elif operation == "save":
            operation: save_mode_h
            last_saving = self.active_paths.get(operation)
            if last_saving is None:
                self.LoadOrSaveWorkflow("save as")
            else:
                _ = SaveWorkflow(
                    active_graph,
                    last_saving,
                    self,
                    status_bar=self.status_bar,
                )
        elif operation == "save as":
            operation: save_mode_h
            filename = SaveWorkflow(
                active_graph,
                APP_CONFIG.LastSavingFolder(operation),
                self,
                status_bar=self.status_bar,
            )
        elif operation == "save as script":
            filename = SaveWorkflowAsScript(
                active_graph,
                last_saving,
                self,
                status_bar=self.status_bar,
            )
        elif operation == "save as screenshot":
            filename = SaveWorkflowAsScreenshot(
                active_whiteboard,
                last_saving,
                self,
                status_bar=self.status_bar,
            )
        else:
            raise LoadSaveError(f"Operation {operation} invalid.")

        if filename is None:
            return

        if operation in ("load", "load recent", "save as"):
            APP_CONFIG.UpdateRecentFlows(filename)
            if operation in ("load", "load recent"):
                self.log_area.ClearForWhiteboard(active_whiteboard)
                APP_CONFIG.UpdateLastLoadingFolder(filename.parent)
            elif operation == "save as":
                active_whiteboard.RenameFromFile(filename, self.name_manager)
                operation: save_mode_h
                APP_CONFIG.UpdateLastSavingFolder(operation, filename.parent)

            tabs = self.tabs
            index = tabs.indexOf(active_whiteboard)
            tabs.setTabText(index, active_whiteboard.name)
            tooltip = "\n".join(
                f"{_key}: {_vle}" for _key, _vle in self.active_paths.items()
            )
            tabs.setTabToolTip(index, tooltip)

            self.load_recent_menu.clear()
            AddEntriesToMenu(
                self._EntriesForLoadingRecent(),
                self.load_recent_menu,
                self,
            )
        elif operation in ("save as script", "save as screenshot"):
            operation: save_mode_h
            APP_CONFIG.UpdateLastSavingFolder(operation, filename.parent)
            self.active_paths[operation] = filename

    def _EntriesForLoadingRecent(self) -> entry_t | tuple[entry_t, ...]:
        """
        Must be an instance method because of the way menu actions are built.
        """
        recent_s = APP_CONFIG.recent_flows
        if recent_s.__len__() > 0:
            return tuple(
                entry_t(
                    text=str(_pth),
                    action="LoadOrSaveWorkflow",
                    args="load recent",
                    kwargs={"recent": _pth},
                )
                for _pth in recent_s
            )

        return entry_t(text="No Recent Workflows")

    def OpenAboutDialog(self, _: bool, /) -> None:
        """"""
        qtwg.QMessageBox.about(
            self,
            "About pyVispr",
            f"<b>pyVispr {__version__}</b><br/><br/>"
            f"<i>Documentation:</i><br/>"
            f"<a href={DOCUMENTATION_ADDRESS}>{DOCUMENTATION_ADDRESS}</a><br/>"
            f"<i>Source Code:</i><br/>"
            f"<a href={SOURCE_ADDRESS}>{SOURCE_ADDRESS}</a>",
        )

    def OpenConfiguration(self, _: bool, /) -> None:
        """
        Must be an instance method because of the way menu actions are built.
        """
        config = config_wgt_t()
        config.exec()

    def OpenAboutWorkflowDialog(self, _: bool, /) -> None:
        """"""
        about = about_t()
        about.SetTitleAndContent("About Workflow", str(self.active_whiteboard.graph))
        about.exec()

    def keyPressEvent(self, event: qtgi.QKeyEvent, /) -> None:
        """"""
        if event.modifiers() is not qt_e.KeyboardModifier.NoModifier:
            qtwg.QMainWindow.keyPressEvent(self, event)
            return

        if not isinstance(
            qtwg.QApplication.focusWidget(), (qtwg.QLineEdit, qtwg.QTextEdit)
        ):
            current = self.tabs.currentWidget()
            if current is self.active_whiteboard:
                self.node_list.filter_wgt.keyPressEvent(event)
                return
            elif current is self.doc_area:
                self.doc_area.filter_wgt.keyPressEvent(event)
                return

        qtwg.QMainWindow.keyPressEvent(self, event)

    def Close(self) -> None:
        """"""
        tabs = self.tabs
        for idx in range(tabs.count()):
            widget = tabs.widget(idx)
            if not isinstance(widget, whiteboard_t):
                continue

            self.active_whiteboard = widget

            if (self.active_paths.get("save") is None) and (
                self.active_whiteboard.graph.functional.__len__() > 0
            ):
                should_save = qtwg.QMessageBox(parent=self)
                should_save.setText(
                    f"The workflow {self.active_whiteboard.name} has not been saved."
                )
                should_save.setInformativeText("Do you want to save it?")
                should_save.setStandardButtons(
                    qtwg.QMessageBox.StandardButton.Yes
                    | qtwg.QMessageBox.StandardButton.No
                )
                should_save.setDefaultButton(qtwg.QMessageBox.StandardButton.Yes)
                answer = should_save.exec()
                if answer == qtwg.QMessageBox.StandardButton.Yes:
                    self.LoadOrSaveWorkflow("save as")

        APP_CONFIG.Save()
        self.close()


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
