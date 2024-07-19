"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import typing as h
from pathlib import Path as path_t

from babelwidget.backend.generic.path_chooser import NewSelectedInputDocument
from logger_36.handler import AddRichConsoleHandler
from logger_36.instance.loggers import LOGGERS
from pyvispr.catalog.installer import (
    ExistingUserPaths,
    InstallLocalFunction,
    InstallReferencedFunction,
    InstallSystemFunction,
    PathForSystem,
    UpdateFunction,
)
from pyvispr.config.appearance.behavior import TOO_MANY_SELECTED
from pyvispr.config.appearance.color import BLACK_BRUSH
from pyvispr.constant.app import APP_NAME
from pyvispr.extension.introspection.function import function_t
from pyvispr.extension.object.field import NonInitField_NONE
from pyvispr.extension.qt.imports import qt_e, qtwg
from pyvispr.flow.descriptive.node import installation_type_e
from pyvispr.interface.widget.function_header import HeaderDialog, header_wgt_t
from pyvispr.interface.widget.list.file import file_list_wgt_t
from pyvispr.interface.widget.list.function import function_list_wgt_t
from pyvispr.interface.widget.list.module import module_list_wgt_t
from pyvispr.interface.widget.list.node import node_list_wgt_t
from pyvispr.runtime.backend import SCREEN_BACKEND
from pyvispr.runtime.catalog import NODE_CATALOG


@d.dataclass(slots=True, repr=False, eq=False)
class installer_wdw_t(qtwg.QMainWindow):
    node_list: node_list_wgt_t
    file_list: file_list_wgt_t
    module_list: module_list_wgt_t
    function_list: function_list_wgt_t
    recursivity_wgt: qtwg.QCheckBox
    # For retrieval of header dialog details.
    ii_names: str | None = NonInitField_NONE()
    output_names: str | None = NonInitField_NONE()
    final_header: str | None = NonInitField_NONE()

    def __post_init__(self) -> None:
        """"""
        qtwg.QMainWindow.__init__(self)
        self.setWindowTitle(f"{APP_NAME} - Node Installer")

        catalog = _CatalogWidget(self.node_list)
        single = _SingleWidget(self.InstallUserFunction)
        multiple = _MultipleWidget(
            self.recursivity_wgt,
            self.file_list,
            self.ChooseUserFolder,
            self.InstallUserFolder,
        )
        system = _SystemWidget(
            self.module_list,
            self.function_list,
            self.InstallSystemFunction,
        )
        tabs = qtwg.QTabWidget()
        for widget, name in (
            (catalog, "Manage Installed"),
            (single, "Install Single"),
            (multiple, "Install Batch - User"),
            (system, "Install Batch - System"),
        ):
            tabs.addTab(widget, name)
        done = qtwg.QPushButton("Done")

        layout = qtwg.QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(done)

        central = qtwg.QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        SCREEN_BACKEND.AddMessageCanal(
            self.node_list, "itemClicked", self.CorrectHeaderOrUninstall
        )
        SCREEN_BACKEND.AddMessageCanal(
            self.module_list, "itemClicked", self.LoadFunctions
        )
        SCREEN_BACKEND.AddMessageCanal(done, "clicked", self.close)

        AddRichConsoleHandler(logger=LOGGERS.active)

    @classmethod
    def New(cls) -> h.Self:
        """"""
        node_list = node_list_wgt_t(element_name="Nodes")
        file_list = file_list_wgt_t(element_name="Python Files")
        module_list = module_list_wgt_t(element_name="Modules")
        function_list = function_list_wgt_t(element_name="Functions")
        recursivity_wgt = qtwg.QCheckBox("Search Recursively")

        file_list.setSelectionMode(
            qtwg.QAbstractItemView.SelectionMode.ExtendedSelection
        )
        function_list.setSelectionMode(
            qtwg.QAbstractItemView.SelectionMode.ExtendedSelection
        )

        return cls(
            node_list=node_list,
            file_list=file_list,
            module_list=module_list,
            function_list=function_list,
            recursivity_wgt=recursivity_wgt,
        )

    def LoadFunctions(self, item: qtwg.QListWidgetItem, /) -> None:
        """"""
        # self.setEnabled(False)
        # qtcr.QCoreApplication.processEvents()
        self.function_list.module = item.text()
        self.function_list.Reload()
        # self.setEnabled(True)

    def InstallUserFunction(self, mode: installation_type_e, /) -> None:
        """"""
        path = NewSelectedInputDocument(
            "Select Python File",
            "Select Python File",
            SCREEN_BACKEND,
            mode="document",
            valid_types={"Python File": "py"},
        )
        if path is None:
            return

        self._InstallUserFunctionForPath(path, True, mode)
        self.node_list.Reload()

    def _InstallUserFunctionForPath(
        self, path: path_t, should_correct_header: bool, mode: installation_type_e, /
    ) -> None:
        """"""
        function = function_t.NewFromPath(path)
        if function is None:
            return

        existing_s = ExistingUserPaths(function.name)
        if (existing_s.__len__() > 0) and _ShouldNotProceedWithInstallation(
            f"{path}: {function.name}"
        ):
            return

        for existing in existing_s:
            existing.unlink()

        if should_correct_header:
            header_dialog = HeaderDialog(
                None,
                function,
                self._HeaderRetrievalInitialization,
                self._RetrieveFinalHeader,
                self,
            )
            header_dialog.exec()
            if self.final_header is None:
                return

            header = self.final_header
        else:
            header = function.header
            self.output_names = function.output_names

        if mode is installation_type_e.local:
            InstallFunction = InstallLocalFunction
        else:
            InstallFunction = InstallReferencedFunction
        InstallFunction(function, header, self.ii_names, self.output_names)

    def ChooseUserFolder(self) -> None:
        """"""
        path = NewSelectedInputDocument(
            "Select Base Folder", "Select Base Folder", SCREEN_BACKEND, mode="folder"
        )
        if path is None:
            return

        self.file_list.base_folder = path
        self.file_list.recursive_mode = self.recursivity_wgt.isChecked()
        self.file_list.Reload()

    def InstallUserFolder(self, mode: installation_type_e, /) -> None:
        """"""
        if self.file_list.base_folder is None:
            return

        selected_s = self.file_list.SelectedItemsOrAll()
        should_correct_header = selected_s.__len__() < TOO_MANY_SELECTED
        for selected in selected_s:
            path = self.file_list.files[selected.text()]
            self._InstallUserFunctionForPath(path, should_correct_header, mode)

        self.node_list.Reload()

    def InstallSystemFunction(self) -> None:
        """"""
        if self.function_list.module is None:
            return

        selected_s = self.function_list.SelectedItemsOrAll()
        should_correct_header = selected_s.__len__() < TOO_MANY_SELECTED
        for selected in selected_s:
            function_display_name = selected.text()
            if "." in function_display_name:
                _, function_name = function_display_name.rsplit(".", maxsplit=1)
            else:
                function_name = function_display_name
            module_pypath = self.function_list.functions[function_display_name].pypath
            where = PathForSystem(module_pypath, function_name)
            if where.is_file() and _ShouldNotProceedWithInstallation(
                f"{module_pypath}.{function_name}"
            ):
                continue

            function = self.function_list.functions[function_display_name]
            if should_correct_header:
                header_dialog = HeaderDialog(
                    None,
                    function,
                    self._HeaderRetrievalInitialization,
                    self._RetrieveFinalHeader,
                    self,
                )
                header_dialog.exec()
                if self.final_header is None:
                    continue

                header = self.final_header
            else:
                header = function.header
                self.output_names = function.output_names

            InstallSystemFunction(
                module_pypath,
                function_name,
                function.imports,
                header,
                self.ii_names,
                self.output_names,
            )

        self.node_list.Reload()

    def CorrectHeaderOrUninstall(self, item: qtwg.QListWidgetItem, /) -> None:
        """"""
        node = NODE_CATALOG[item.text()]

        menu = qtwg.QMenu()
        correct_action = menu.addAction("Correct Definition")
        uninstall_menu = menu.addMenu("Uninstall...")
        _ = uninstall_menu.addAction("... Now")
        position = self.node_list.mapToGlobal(
            self.node_list.viewport().pos()
            + self.node_list.visualItemRect(item).topRight()
        )
        selected_action = menu.exec(position)
        if selected_action is None:
            return

        if selected_action is correct_action:
            proxy_function = function_t.NewFromPath(
                node.proxy.path, name=node.proxy.name
            )
            actual_function = function_t.NewFromPath(
                node.actual.path, name=node.actual.name
            )
            header_dialog = HeaderDialog(
                proxy_function,
                actual_function,
                self._HeaderRetrievalInitialization,
                self._RetrieveFinalHeader,
                self,
            )
            header_dialog.exec()

            if self.final_header is not None:
                UpdateFunction(
                    node.name,
                    proxy_function,
                    actual_function,
                    self.final_header,
                    self.ii_names,
                    self.output_names,
                    node.installation_type,
                )
                node.requires_completion = False
                item.setForeground(BLACK_BRUSH)
        else:
            node.proxy.path.unlink()
            self.node_list.source.remove(node)
            _ = self.node_list.takeItem(self.node_list.row(item))

    def _HeaderRetrievalInitialization(self) -> None:
        """"""
        self.ii_names = None
        self.output_names = None
        self.final_header = None

    def _RetrieveFinalHeader(
        self, header_wgt: header_wgt_t, header_dialog: qtwg.QDialog, /
    ) -> None:
        """"""
        if header_wgt.header_is_valid:
            self.ii_names = header_wgt.ii_names
            self.output_names = header_wgt.output_names
            self.final_header = header_wgt.header_final
            header_dialog.close()


def _CatalogWidget(node_list: node_list_wgt_t, /) -> qtwg.QWidget:
    """"""
    output = qtwg.QWidget()

    layout = qtwg.QVBoxLayout()
    layout.setAlignment(qt_e.AlignmentFlag.AlignCenter)

    layout.addWidget(node_list.filter_wgt)
    layout.addWidget(node_list)
    output.setLayout(layout)

    return output


def _SingleWidget(
    InstallUserFunction: h.Callable[[installation_type_e], None], /
) -> qtwg.QWidget:
    """"""
    output = qtwg.QWidget()

    local = qtwg.QPushButton("Select Python File For LOCAL Installation")
    referenced = qtwg.QPushButton("Select Python File For REFERENCED Installation")

    for widget in (local, referenced):
        widget.setSizePolicy(
            qtwg.QSizePolicy.Policy.Expanding,
            qtwg.QSizePolicy.Policy.Expanding,
        )

    layout = qtwg.QVBoxLayout()

    layout.addWidget(local)
    layout.addWidget(referenced)
    output.setLayout(layout)

    SCREEN_BACKEND.AddMessageCanal(
        local, "clicked", InstallUserFunction, installation_type_e.local
    )
    SCREEN_BACKEND.AddMessageCanal(
        referenced, "clicked", InstallUserFunction, installation_type_e.referenced
    )

    return output


def _MultipleWidget(
    recursivity_wgt: qtwg.QCheckBox,
    file_list: file_list_wgt_t,
    ChooseUserFolder: h.Callable[[], None],
    InstallUserFolder: h.Callable[[installation_type_e], None],
    /,
) -> qtwg.QWidget:
    """"""
    output = qtwg.QWidget()

    select = qtwg.QPushButton(f"Select Base Folder")
    install_local = qtwg.QPushButton("Install Selected or All as LOCAL")
    install_referenced = qtwg.QPushButton("Install Selected or All as REFERENCED")

    select.setSizePolicy(
        qtwg.QSizePolicy.Policy.Expanding,
        qtwg.QSizePolicy.Policy.Expanding,
    )

    left = qtwg.QVBoxLayout()
    right = qtwg.QVBoxLayout()
    main_layout = qtwg.QHBoxLayout()

    left.addWidget(select)
    left.addWidget(recursivity_wgt)

    right.addWidget(file_list)
    right.addWidget(install_local)
    right.addWidget(install_referenced)

    main_layout.addLayout(left)
    main_layout.addLayout(right)

    output.setLayout(main_layout)

    SCREEN_BACKEND.AddMessageCanal(select, "clicked", ChooseUserFolder)
    SCREEN_BACKEND.AddMessageCanal(
        install_local,
        "clicked",
        InstallUserFolder,
        installation_type_e.local,
    )
    SCREEN_BACKEND.AddMessageCanal(
        install_referenced,
        "clicked",
        InstallUserFolder,
        installation_type_e.referenced,
    )

    return output


def _SystemWidget(
    module_list: module_list_wgt_t,
    function_list: function_list_wgt_t,
    InstallSystemFunction_: h.Callable[[], None],
    /,
) -> qtwg.QWidget:
    """"""
    output = qtwg.QWidget()

    install = qtwg.QPushButton("Install Selected or All")

    layout = qtwg.QGridLayout()
    for col, widget in enumerate((module_list, function_list)):
        layout.addWidget(widget.filter_wgt, 0, col)
        layout.addWidget(widget, 1, col)
    layout.addWidget(install, 2, 0, 1, 2)

    output.setLayout(layout)

    SCREEN_BACKEND.AddMessageCanal(install, "clicked", InstallSystemFunction_)

    return output


def _ShouldNotProceedWithInstallation(what: str, /, *, how_installed: str = "") -> bool:
    """"""
    answer_cancel = qtwg.QMessageBox.StandardButton.Cancel
    update = qtwg.QMessageBox()
    update.setWindowTitle(f'Proceed Updating "{what}"?')
    update.setText(
        f'"{what}" is already {how_installed}installed. '
        f"Would you like to proceed updating/overwriting its installation?"
    )
    update.setStandardButtons(answer_cancel | qtwg.QMessageBox.StandardButton.Ok)
    update.setDefaultButton(answer_cancel)
    answer = update.exec()

    return answer == answer_cancel


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
