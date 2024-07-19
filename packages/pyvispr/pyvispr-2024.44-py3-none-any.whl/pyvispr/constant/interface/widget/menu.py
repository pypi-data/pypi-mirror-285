"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

from pyvispr.constant.app import DOCUMENTATION_ADDRESS, SOURCE_ADDRESS
from pyvispr.extension.qt.imports import qtcr, qtgi
from pyvispr.extension.qt.menu import entry_t

_LOAD_RECENT_MENU = {"Load Recent...": "_EntriesForLoadingRecent"}

_STOW_MENU = {
    "Save As...": (
        entry_t(
            text="New Name",
            action="LoadOrSaveWorkflow",
            args="save as",
        ),
        entry_t(
            text="Script",
            action="LoadOrSaveWorkflow",
            args="save as script",
        ),
        entry_t(
            text="Screenshot",
            action="LoadOrSaveWorkflow",
            args="save as screenshot",
        ),
    )
}

_RESET_MENU = {
    "Reset...": entry_t(text="Now", action="active_whiteboard.InvalidateWorkflow")
}
_CLEAR_MENU = {"Clear...": entry_t(text="Now", action="active_whiteboard.Clear")}

MAIN_MENUS = {
    "py&Vispr": (
        entry_t(text="About", action="OpenAboutDialog"),
        entry_t(text="Configure", action="OpenConfiguration"),
        None,
        entry_t(
            text="Documentation (https)",
            action=qtgi.QDesktopServices.openUrl,
            args=qtcr.QUrl(DOCUMENTATION_ADDRESS),
        ),
        entry_t(
            text="Source Code (https)",
            action=qtgi.QDesktopServices.openUrl,
            args=qtcr.QUrl(SOURCE_ADDRESS),
        ),
        None,
        entry_t(text="&Quit", action="Close", shortcut="Ctrl+Q"),
    ),
    "&File": (
        entry_t(
            text="L&oad",
            action="LoadOrSaveWorkflow",
            args="load",
            shortcut="Ctrl+O",
        ),
        _LOAD_RECENT_MENU,
        None,
        entry_t(
            text="&Save",
            action="LoadOrSaveWorkflow",
            args="save",
            shortcut="Ctrl+S",
        ),
        _STOW_MENU,
    ),
    "&View": (
        entry_t(
            text="Toggle Smooth Links", action="active_whiteboard.ToggleSmoothLinks"
        ),
        entry_t(text="Toggle Grid", action="active_whiteboard.ToggleGridVisibility"),
    ),
    "&Edit": (
        entry_t(
            text="Select &All",
            action="active_whiteboard.SelectOrNotAllNodes",
            args=(True,),
            shortcut="Ctrl+A",
        ),
        entry_t(
            text="Deselect All",
            action="active_whiteboard.SelectOrNotAllNodes",
            args=(False,),
            shortcut="Ctrl+Shift+A",
        ),
        None,
        entry_t(
            text="Copy",
            action="CopySubGraph",
            shortcut="Ctrl+C",
        ),
        entry_t(
            text="Cut",
            action="CutSubGraph",
            shortcut="Ctrl+X",
        ),
        entry_t(
            text="Paste",
            action="PasteSubGraph",
            shortcut="Ctrl+V",
        ),
        None,
        entry_t(text="Align on Grid", action="active_whiteboard.AlignNodesOnGrid"),
        None,
        _CLEAR_MENU,
    ),
    "&Workflow": (
        entry_t(text="About", action="OpenAboutWorkflowDialog"),
        entry_t(
            text="&Run",
            action="RunWorkflow",
            shortcut="Ctrl+R",
        ),
        _RESET_MENU,
        None,
        entry_t(
            text="&New",
            action="AddWhiteboard",
            shortcut="Ctrl+N",
        ),
    ),
    "&Catalog": entry_t(text="Refresh", action="node_list.Reload"),
}

WHITEBOARD_MENU = (
    entry_t(text="View"),
    entry_t(text="Toggle Smooth Links", action="ToggleSmoothLinks"),
    entry_t(text="Toggle Grid", action="ToggleGridVisibility"),
    entry_t(text="Edit"),
    entry_t(
        text="Select All",
        action="SelectOrNotAllNodes",
        args=(True,),
    ),
    entry_t(
        text="Deselect All",
        action="SelectOrNotAllNodes",
        args=(False,),
    ),
    entry_t(text="Align on Grid", action="AlignNodesOnGrid"),
    {"Clear...": entry_t(text="Now", action="Clear")},
    entry_t(text="Workflow"),
    entry_t(
        text="Run",
        action="RunWorkflow",
    ),
    {"Reset...": entry_t(text="Now", action="InvalidateWorkflow")},
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
