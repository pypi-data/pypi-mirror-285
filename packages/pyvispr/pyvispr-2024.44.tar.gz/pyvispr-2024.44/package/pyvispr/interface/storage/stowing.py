"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

from pathlib import Path as path_t

from json_any.task.storage import StoreAsJSON
from logger_36.instance.loggers import LOGGERS
from logger_36.logger import LogException
from pyvispr.constant.interface.storage.path import FORMAT_EXTENSION
from pyvispr.extension.qt.imports import qtwg
from pyvispr.flow.complete.graph import graph_t
from pyvispr.flow.visual.whiteboard import whiteboard_t


def SaveWorkflow(
    graph: graph_t,
    last_saving: path_t,
    manager: qtwg.QWidget,
    /,
    *,
    status_bar: qtwg.QStatusBar | None = None,
) -> path_t | None:
    """"""
    filename = _FilenameFromLast(
        last_saving,
        "Save Workflow",
        f"pyVispr Workflows (*{FORMAT_EXTENSION})",
        FORMAT_EXTENSION,
        manager,
    )
    if filename is None:
        return None

    try:
        filename = StoreAsJSON(
            graph,
            filename,
            should_continue_on_error=True,
            should_overwrite_path=True,
            indent=2,
        )
    except Exception as exception:
        LogException(exception, logger=LOGGERS.active)
        qtwg.QMessageBox.critical(
            None,
            "Workflow Saving Error",
            "See Messages tab.",
        )
        return None

    if isinstance(filename, path_t):
        message = f"Workflow Successfully Saved in: {filename}"
        if status_bar is None:
            qtwg.QMessageBox.about(
                None,
                "Workflow Successfully Saved",
                message + ".",
            )
        else:
            status_bar.showMessage(message)
        return filename

    message = "Workflow Saving Error:\n" + "\n".join(filename)
    LOGGERS.active.error(message)
    qtwg.QMessageBox.critical(None, "Workflow Saving Error", message)

    return None


def SaveWorkflowAsScript(
    graph: graph_t,
    last_saving: path_t,
    manager: qtwg.QWidget,
    /,
    *,
    status_bar: qtwg.QStatusBar | None = None,
) -> path_t | None:
    """"""
    extension = ".py"
    filename = _FilenameFromLast(
        last_saving,
        "Save Workflow as Script",
        f"Python Scripts (*{extension})",
        extension,
        manager,
    )
    if filename is None:
        return None

    graph.functional.Invalidate()
    try:
        with open(filename, mode="w") as accessor:
            graph.Run(script_accessor=accessor)
    except Exception as exception:
        LogException(exception, logger=LOGGERS.active)
        qtwg.QMessageBox.critical(
            None,
            "Workflow Saving-as-Script Error",
            "See Messages tab.",
        )
        return None

    message = f"Workflow Successfully Saved as a Python Script in: {filename}"
    if status_bar is None:
        qtwg.QMessageBox.about(
            None,
            "Workflow Successfully Saved-as-script",
            message + ".",
        )
    else:
        status_bar.showMessage(message)

    return filename


def SaveWorkflowAsScreenshot(
    whiteboard: whiteboard_t,
    last_saving: path_t,
    manager: qtwg.QWidget,
    /,
    *,
    status_bar: qtwg.QStatusBar | None = None,
) -> path_t | None:
    """"""
    extension = ".png"
    filename = _FilenameFromLast(
        last_saving,
        "Save Workflow as Screenshot",
        f"Images (*{extension} *.jpg)",
        extension,
        manager,
    )
    if filename is None:
        return None

    try:
        whiteboard.Screenshot().save(str(filename))
    except Exception as exception:
        LogException(exception, logger=LOGGERS.active)
        qtwg.QMessageBox.critical(
            None,
            "Workflow Saving-as-Screenshot Error",
            "See Messages tab.",
        )
        return None

    message = f"Workflow Screenshot Successfully Saved in: {filename}"
    if status_bar is None:
        qtwg.QMessageBox.about(
            None,
            "Workflow Successfully Saved-as-screenshot",
            message + ".",
        )
    else:
        status_bar.showMessage(message)

    return filename


def _FilenameFromLast(
    last_saving: path_t,
    caption: str,
    formats: str,
    extension: str,
    manager: qtwg.QWidget,
    /,
) -> path_t | None:
    """"""
    if last_saving.is_file():
        return last_saving

    filename = qtwg.QFileDialog.getSaveFileName(
        manager,
        caption,
        str(last_saving),
        formats,
    )
    if (filename is None) or (filename[0].__len__() == 0):
        return None

    output = path_t(filename[0])
    if output.suffix.__len__() == 0:
        output = output.with_suffix(extension)
        if output.exists():
            if output.is_file():
                confirmation = qtwg.QMessageBox(parent=manager)
                confirmation.setWindowTitle("Workflow Saving")
                confirmation.setText(f"{output} exists.")
                confirmation.setInformativeText("Do you want to overwrite it?")
                confirmation.setStandardButtons(
                    qtwg.QMessageBox.StandardButton.No
                    | qtwg.QMessageBox.StandardButton.Yes
                )
                confirmation.setDefaultButton(qtwg.QMessageBox.StandardButton.No)
                answer = confirmation.exec()
                if answer == qtwg.QMessageBox.StandardButton.No:
                    return None
            else:
                qtwg.QMessageBox.critical(
                    manager,
                    "Workflow Saving Error",
                    f"{output} exists and is not a file.",
                )
                return None

    return output


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
