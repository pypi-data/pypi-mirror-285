"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import pprint as pprt
import typing as h

import numpy
from pyvispr.extension.qt.app import ExecuteApp, NewApp
from pyvispr.extension.qt.imports import qt_e, qtcr, qtgi, qtwg
from pyvispr.interface.window.runner import runner_wdw_t
from pyvispr.runtime.backend import SCREEN_BACKEND
from pyvispr.runtime.persistence import PERSISTENCE


def pyVisprValueViewer(value: h.Any, /, *, pyvispr_name: str | None = None) -> None:
    """
    Simpler value viewer with a table view for sequences of sequences of numbers that
    can be converted to Numpy arrays.
    Numpy: https://numpy.org/
    """
    if pyvispr_name in PERSISTENCE:
        viewer = PERSISTENCE[pyvispr_name]
        viewer.Update(value)
    else:
        app, should_exec = NewApp()
        viewer = viewer_t(pyvispr_name)
        viewer.show()
        viewer.Update(value)
        ExecuteApp(app, should_exec=should_exec, should_exit=False)


class viewer_t(qtwg.QMainWindow):
    def __init__(self, name: str | None, /) -> None:
        """"""
        qtwg.QMainWindow.__init__(self, runner_wdw_t.Instance())
        self.setAttribute(qt_e.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle("pyVispr Value Viewer")
        if name is None:
            self.name = f"Unknown Node {id(self)}"
        else:
            self.name = name
        PERSISTENCE[self.name] = self

        name_wgt = qtwg.QLabel(f'<span style="font-weight:bold">{self.name}</span>')
        name_wgt.setContentsMargins(6, 0, 0, 0)
        content = qtwg.QTextEdit()
        progress = qtwg.QProgressBar()
        progress.setVisible(False)
        progress.setTextVisible(False)
        done_btn = qtwg.QPushButton("Done")

        layout = qtwg.QVBoxLayout()
        layout.addWidget(name_wgt)
        layout.addWidget(content)
        layout.addWidget(progress)
        layout.addWidget(done_btn)

        central = qtwg.QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        timer = qtcr.QTimer()
        timer.setTimerType(qt_e.TimerType.CoarseTimer)
        timer.setInterval(1000)
        timer.timeout.connect(self._AcknowledgeProgress)

        self.as_array: numpy.ndarray | None = None
        self.content: qtwg.QTextEdit | qtwg.QTableView = content
        self.model: qtgi.QStandardItemModel | None = None
        self.progress = progress
        self.timer = timer
        self.filling_done = False
        self.current_row = 0

        SCREEN_BACKEND.AddMessageCanal(done_btn, "clicked", self.close)

    def Update(self, value: h.Any, /) -> None:
        """"""
        self.as_array = _ValueAs2DimensionalArray(value)
        if self.as_array is None:
            if not isinstance(self.content, qtwg.QTextEdit):
                content = qtwg.QTextEdit()
                layout = self.centralWidget().layout()
                _ = layout.replaceWidget(self.content, content)
                self.content = content
                self.model = None

            as_str = pprt.pformat(value, width=120, compact=True, sort_dicts=False)
            self.content.setText(as_str)
        else:
            if isinstance(self.content, qtwg.QTableView):
                self.content.selectAll()
                self.content.clearSelection()
                self.model.clear()
            else:
                content = qtwg.QTableView()
                model = qtgi.QStandardItemModel(content)
                content.setModel(model)
                layout = self.centralWidget().layout()
                _ = layout.replaceWidget(self.content, content)
                self.content = content
                self.model = model

            self._InitializeContentFilling()
            qtcr.QThreadPool.globalInstance().start(self._FillContent)

    def _InitializeContentFilling(self) -> None:
        """"""
        n_cols = self.as_array.shape[1]

        self.content.setEnabled(False)
        self.model.setColumnCount(n_cols)

        self.progress.setValue(0)
        self.progress.setMaximum(n_cols)
        self.progress.setVisible(True)

        self.filling_done = False
        self.current_row = 0
        self.timer.start()

    def _FillContent(self) -> None:
        """"""
        array = self.as_array

        min_value, max_value = numpy.amin(array), numpy.amax(array)
        if max_value > min_value:
            color = qtgi.QColor()
            if (min_value, max_value) != (0, 255):
                factor = 255.0 / (max_value - min_value)
            else:
                factor = None
        else:
            color = factor = None

        model = self.model
        MakeCell = qtgi.QStandardItem.__call__
        align_right = qt_e.AlignmentFlag.AlignRight
        as_background = qt_e.ItemDataRole.BackgroundRole
        for self.current_row, row in enumerate(array, start=1):
            cells = tuple(map(MakeCell, map(str, row)))
            for cell in cells:
                cell.setTextAlignment(align_right)
            if color is not None:
                for cell, gray in zip(cells, row):
                    if factor is not None:
                        gray = int(round(factor * (gray - min_value)))
                    color.setRgb(255 - gray, 255, 255 - gray, 255)
                    color_data = qtcr.QVariant(qtgi.QBrush(color))
                    cell.setData(color_data, as_background)
            model.appendRow(cells)

        self.filling_done = True

    def _AcknowledgeProgress(self) -> None:
        """"""
        if self.filling_done:
            self.timer.stop()
            self.progress.setVisible(False)
            content = self.content
            content.resizeColumnsToContents()
            content.setEnabled(True)
        else:
            self.progress.setValue(self.current_row)

    def closeEvent(self, event: qtgi.QCloseEvent, /) -> None:
        """"""
        del PERSISTENCE[self.name]
        qtwg.QMainWindow.closeEvent(self, event)


def _ValueAs2DimensionalArray(value: h.Any, /) -> numpy.ndarray | None:
    """"""
    try:
        output = numpy.array(value)
    except:
        pass
    else:
        if (
            (output.ndim < 3)
            and (output.size > 1)
            and (
                numpy.issubdtype(output.dtype, numpy.integer)
                or numpy.issubdtype(output.dtype, numpy.floating)
            )
        ):
            if output.ndim == 1:
                return output[numpy.newaxis, :]  # One-row, 2D array.
            return output

    return None


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
