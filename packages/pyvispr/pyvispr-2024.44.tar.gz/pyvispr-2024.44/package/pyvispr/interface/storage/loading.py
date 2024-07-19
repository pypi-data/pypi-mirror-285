"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

from pathlib import Path as path_t

from logger_36.instance.loggers import LOGGERS
from logger_36.logger import LogException
from pyvispr.extension.qt.imports import qtwg
from pyvispr.flow.naming import name_manager_t
from pyvispr.flow.visual.whiteboard import whiteboard_t
from pyvispr.interface.storage.description import LoadedDescription


def LoadWorkflow(
    whiteboard: whiteboard_t,
    last_loading: path_t,
    name_manager: name_manager_t,
    manager: qtwg.QWidget,
    /,
    *,
    status_bar: qtwg.QStatusBar | None = None,
) -> path_t | None:
    """"""
    if last_loading.is_file():
        filename = last_loading
    else:
        filename = qtwg.QFileDialog.getOpenFileName(
            manager,
            "Load Workflow",
            str(last_loading),
            "pyVispr Workflows (*.json.*)",
        )
        if (filename is None) or (len(filename[0]) == 0):
            return None
        filename = path_t(filename[0])

    if whiteboard.graph.functional.__len__() > 0:
        loading_mode = qtwg.QMessageBox(manager)
        loading_mode.setWindowTitle("Loading Options")
        loading_mode.setText(
            "About to load a workflow while the current workflow is not empty\n"
            "Loading options:"
        )
        merging = loading_mode.addButton(
            "Merge Workflows", qtwg.QMessageBox.ButtonRole.YesRole
        )
        _ = loading_mode.addButton(
            "Replace Workflow", qtwg.QMessageBox.ButtonRole.NoRole
        )
        loading_mode.exec()

        should_merge = loading_mode.clickedButton() is merging
    else:
        should_merge = False

    if status_bar is not None:
        status_bar.showMessage(f"Loading Workflow {filename}...")

    try:
        loaded = LoadedDescription(filename)
    except Exception as exception:
        LogException(exception, logger=LOGGERS.active)
        qtwg.QMessageBox.critical(
            None,
            f"Workflow Loading Error",
            "See Messages tab.",
        )
        return None

    whiteboard.SetNewLoadedGraph(
        loaded, should_merge=should_merge, from_file=filename, name_manager=name_manager
    )

    if status_bar is not None:
        status_bar.showMessage("Done Loading")

    return filename


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
