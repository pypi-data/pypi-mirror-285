"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import builtins as bltn
import dataclasses as d
import typing as h
from keyword import iskeyword as IsKeyword
from keyword import issoftkeyword as IsSoftKeyword

from pyvispr.constant.flow.node import NO_OUTPUT_NAMES
from pyvispr.constant.interface.widget.function_header import (
    FIRST_INTAKE_ROW,
    HINT_CHARACTER_SET,
    HINT_COL_IDX,
    INTAKE_OUTPUT_ROW_INCREMENT,
    MISSING_DETAIL,
    N_LAYOUT_COLS,
)
from pyvispr.extension.introspection.function import function_t
from pyvispr.extension.object.field import NON_INIT_FIELD, NonInitField_NONE
from pyvispr.extension.qt.imports import qt_e, qtwg
from pyvispr.runtime.backend import SCREEN_BACKEND


@d.dataclass(slots=True, repr=False, eq=False)
class header_wgt_t(qtwg.QWidget):
    proxy_function: function_t | None
    actual_function: function_t | None
    #
    ii_names: str | None = NonInitField_NONE()
    output_names: str | None = NonInitField_NONE()
    header_final: str = NON_INIT_FIELD
    header_is_valid: bool = NON_INIT_FIELD
    prologue: qtwg.QTextEdit = NON_INIT_FIELD
    layout_in_out: qtwg.QGridLayout = NON_INIT_FIELD
    #
    next_intake_row: int = 0
    next_output_row: int = 0

    def __post_init__(self) -> None:
        """"""
        qtwg.QWidget.__init__(self)

        if self.proxy_function is None:
            self.proxy_function = self.actual_function
        elif self.actual_function is None:
            self.actual_function = self.proxy_function

        layout_in_out = qtwg.QGridLayout()
        layout_in_out.setContentsMargins(0, 0, 0, 0)
        self.layout_in_out = layout_in_out

        label = qtwg.QLabel(
            f'<span style="font-size:x-large; font-weight:bold; color:blue">'
            f"{self.actual_function.pypath}.{self.actual_function.name}"
            f"</span>"
        )
        label.setWordWrap(True)
        label.setTextInteractionFlags(
            qt_e.TextInteractionFlag.TextSelectableByKeyboard
            | qt_e.TextInteractionFlag.TextSelectableByMouse
        )
        layout_in_out.addWidget(label, 0, 0, 1, N_LAYOUT_COLS)
        next_row = 1

        _AddParameterHeader(
            layout_in_out, "Input(s)", ("Name", "Type", "Value", "II"), next_row
        )
        next_row += 2
        for name, value in self.proxy_function.header_intakes.items():
            if isinstance(value, tuple):
                elements = (name,) + value
            else:
                elements = (name, value)
            self._AddParameterDetails(layout_in_out, next_row, elements, True)
            next_row += 1

        self._AddNewParameterButton(layout_in_out, next_row, True)
        self.next_intake_row = next_row

        if self.proxy_function.has_outputs:
            next_row = self.next_intake_row + 1
            _AddParameterHeader(layout_in_out, "Output(s)", ("Name", "Type"), next_row)
            self._AddParameterDetails(
                layout_in_out,
                next_row + 2,
                (NO_OUTPUT_NAMES, self.proxy_function.header_outputs[NO_OUTPUT_NAMES]),
                False,
            )
            self._AddNewParameterButton(layout_in_out, next_row + 3, False)
            self.next_output_row = next_row + 3

        if (documentation := self.actual_function.documentation) is None:
            scrollable = qtwg.QLabel("No Documentation Available.")
        else:
            label = qtwg.QLabel(documentation)
            label.setWordWrap(True)
            label.setTextInteractionFlags(
                qt_e.TextInteractionFlag.TextSelectableByKeyboard
                | qt_e.TextInteractionFlag.TextSelectableByMouse
            )
            scrollable = qtwg.QScrollArea()
            scrollable.setWidget(label)

        prologue = qtwg.QTextEdit()
        self.prologue = prologue

        layout_left = qtwg.QVBoxLayout()
        layout_left.setContentsMargins(0, 0, 0, 0)
        layout_left.addWidget(prologue)
        layout_left.addLayout(layout_in_out)

        layout_main = qtwg.QHBoxLayout()
        layout_main.setContentsMargins(0, 0, 0, 0)
        layout_main.addLayout(layout_left)
        layout_main.addWidget(scrollable)
        self.setLayout(layout_main)

        self.BuildHeaderOutput()

    def BuildHeaderOutput(self) -> None:
        """"""
        layout = self.layout_in_out

        header_is_valid = True

        intakes_positional = []
        intakes_w_default = []
        intakes_interactive = []
        for row in range(FIRST_INTAKE_ROW, self.next_intake_row):
            intake_pieces = []
            for col, (replacement, epilogue) in enumerate(
                ((MISSING_DETAIL, ": "), (MISSING_DETAIL, " = "), ("", ""))
            ):
                item = layout.itemAtPosition(row, col)
                if item is None:
                    continue
                widget = item.widget()
                text = widget.text().strip()
                if (text_is_not_empty := (text.__len__() > 0)) or (
                    replacement.__len__() > 0
                ):
                    if text_is_not_empty:
                        if col < 2:
                            if _IsValidIdentifierOrHint(text, col == HINT_COL_IDX):
                                widget.setStyleSheet("background-color:white")
                            else:
                                header_is_valid = False
                                widget.setStyleSheet("background-color:coral")
                    else:
                        text = replacement
                        header_is_valid = False
                        widget.setStyleSheet("background-color:coral")
                    intake_pieces.append(f"{text}{epilogue}")

            intake = "".join(intake_pieces).strip()
            if intake[-1] == "=":
                intakes_positional.append(intake[:-2])
            else:
                intakes_w_default.append(intake)

            if layout.itemAtPosition(row, N_LAYOUT_COLS - 2).widget().isChecked():
                text = layout.itemAtPosition(row, 0).widget().text().strip()
                if text.__len__() == 0:
                    text = MISSING_DETAIL
                intakes_interactive.append(text)

        intakes = intakes_positional
        if intakes.__len__() > 0:
            intakes.append("/")
        if intakes_w_default.__len__() > 0:
            intakes.append("*")
            intakes.extend(intakes_w_default)

        self.ii_names = ", ".join(intakes_interactive)

        if self.proxy_function.has_outputs:
            output_names = []
            output_hints = []
            for row in range(
                self.next_intake_row + INTAKE_OUTPUT_ROW_INCREMENT, self.next_output_row
            ):
                for col, output_list in enumerate((output_names, output_hints)):
                    widget = layout.itemAtPosition(row, col).widget()
                    text = widget.text().strip()
                    if text.__len__() == 0:
                        text = MISSING_DETAIL
                        header_is_valid = False
                        widget.setStyleSheet("background-color:coral")
                    elif _IsValidIdentifierOrHint(text, col == HINT_COL_IDX):
                        widget.setStyleSheet("background-color:white")
                    else:
                        header_is_valid = False
                        widget.setStyleSheet("background-color:coral")
                    output_list.append(text)

            if output_hints.__len__() > 1:
                output_hints = ", ".join(output_hints)
                output_hints = f"tuple[{output_hints}]"
            else:
                output_hints = output_hints[0]

            self.output_names = ", ".join(output_names)
        else:
            output_hints = "None"

        intakes = ", ".join(intakes)
        self.header_final = (
            f"{self.prologue.toPlainText()}\n\n"
            f"def {self.proxy_function.name}({intakes}) -> {output_hints}:"
        )
        self.header_is_valid = header_is_valid

    def _AddParameterDetails(
        self,
        layout: qtwg.QGridLayout,
        row: int,
        elements: h.Sequence[str],
        is_intake: bool,
        /,
    ) -> None:
        """"""
        for col, element in enumerate(elements):
            detail = qtwg.QLineEdit(element)
            layout.addWidget(detail, row, col)
            SCREEN_BACKEND.AddMessageCanal(detail, "textEdited", self.BuildHeaderOutput)
        if is_intake:
            intake = qtwg.QCheckBox("")
            layout.addWidget(intake, row, N_LAYOUT_COLS - 2)
            SCREEN_BACKEND.AddMessageCanal(
                intake, "stateChanged", self.BuildHeaderOutput
            )

        remove_btn = qtwg.QPushButton("x")
        remove_btn.setStyleSheet("color:coral")
        width = remove_btn.fontMetrics().boundingRect("x").width() + 12
        remove_btn.setMaximumWidth(width)
        layout.addWidget(remove_btn, row, N_LAYOUT_COLS - 1)
        SCREEN_BACKEND.AddMessageCanal(
            remove_btn,
            "clicked",
            self._RemoveParameter,
            remove_btn,
            is_intake,
        )

    def _AddNewParameterButton(
        self, layout: qtwg.QGridLayout, row: int, is_intake: bool, /
    ) -> None:
        """"""
        new_btn = qtwg.QPushButton("+")
        new_btn.setStyleSheet("font-weight:bold; color:green")

        layout.addWidget(new_btn, row, 0, 1, N_LAYOUT_COLS)

        if is_intake:
            action = self._AddIntakeParameter
        else:
            action = self._AddOutputParameter
        SCREEN_BACKEND.AddMessageCanal(new_btn, "clicked", action)

    def _AddIntakeParameter(self) -> None:
        """"""
        self._AddParameter(True)

    def _AddOutputParameter(self) -> None:
        """"""
        self._AddParameter(False)

    def _AddParameter(self, is_intake: bool, /) -> None:
        """"""
        if is_intake:
            next_row = self.next_intake_row
            elements = ("", "", "")
        else:
            next_row = self.next_output_row
            elements = ("", "")
        layout = self.layout_in_out
        for row in reversed(range(next_row, layout.rowCount())):
            # /!\ If a widget spans several columns, it will appear in each cell, not
            # just the first one. Hence the necessity to manage the column index
            # manually instead of a for-loop.
            col = 0
            while col < N_LAYOUT_COLS:
                content = layout.itemAtPosition(row, col)
                if (content is None) or content.isEmpty():
                    col += 1
                    continue
                widget = content.widget()
                index = layout.indexOf(widget)
                *_, col_span = layout.getItemPosition(index)
                layout.removeWidget(widget)
                layout.addWidget(widget, row + 1, col, 1, col_span)
                col += col_span

        self._AddParameterDetails(layout, next_row, elements, is_intake)

        if is_intake:
            self.next_intake_row += 1
        if self.proxy_function.has_outputs:
            self.next_output_row += 1

        self.BuildHeaderOutput()

    def _RemoveParameter(
        self, from_button: qtwg.QPushButton, is_intake: bool, /
    ) -> None:
        """"""
        layout = self.layout_in_out
        button_row, *_ = layout.getItemPosition(layout.indexOf(from_button))

        for col in range(N_LAYOUT_COLS):
            content = layout.itemAtPosition(button_row, col)
            if (content is None) or content.isEmpty():
                continue
            widget = content.widget()
            layout.removeWidget(widget)
            widget.setParent(None)

        for row in range(button_row + 1, layout.rowCount()):
            # /!\ If a widget spans several columns, it will appear in each cell, not
            # just the first one. Hence the necessity to manage the column index
            # manually instead of a for-loop.
            col = 0
            while col < N_LAYOUT_COLS:
                content = layout.itemAtPosition(row, col)
                if (content is None) or content.isEmpty():
                    col += 1
                    continue
                widget = content.widget()
                index = layout.indexOf(widget)
                *_, col_span = layout.getItemPosition(index)
                layout.removeWidget(widget)
                layout.addWidget(widget, row - 1, col, 1, col_span)
                col += col_span

        if is_intake:
            self.next_intake_row -= 1
        if self.proxy_function.has_outputs:
            self.next_output_row -= 1

        self.BuildHeaderOutput()


def HeaderDialog(
    proxy_function: function_t | None,
    actual_function: function_t | None,
    HeaderRetrievalInitialization: h.Callable[[], None],
    FinalHeaderTransmission: h.Callable[[header_wgt_t, qtwg.QDialog], None],
    parent: qtwg.QWidget,
    /,
) -> qtwg.QDialog:
    """"""
    output = qtwg.QDialog(parent=parent)

    header_wgt = header_wgt_t(
        proxy_function=proxy_function, actual_function=actual_function
    )
    cancel_btn = qtwg.QPushButton("Cancel")
    done_btn = qtwg.QPushButton("Done")

    layout_btn = qtwg.QHBoxLayout()
    layout_btn.addWidget(cancel_btn)
    layout_btn.addWidget(done_btn)

    layout = qtwg.QVBoxLayout()
    layout.addWidget(header_wgt)
    layout.addLayout(layout_btn)
    output.setLayout(layout)

    HeaderRetrievalInitialization()
    FinalHeaderTransmission_ = lambda *args, **kwargs: FinalHeaderTransmission(
        header_wgt, output
    )
    SCREEN_BACKEND.AddMessageCanal(cancel_btn, "clicked", output.close)
    SCREEN_BACKEND.AddMessageCanal(done_btn, "clicked", FinalHeaderTransmission_)

    return output


def _AddParameterHeader(
    layout: qtwg.QGridLayout, what: str, titles: h.Sequence[str], from_row: int, /
) -> None:
    """"""
    layout.addWidget(
        qtwg.QLabel(f'<span style="font-weight:bold; color:blue">{what}</span>'),
        from_row,
        0,
        1,
        N_LAYOUT_COLS,
    )
    for col, content in enumerate(titles):
        layout.addWidget(
            qtwg.QLabel(f'<span style="color:green">{content}</span>'),
            from_row + 1,
            col,
        )


def _IsValidIdentifierOrHint(string: str, is_hint: bool, /) -> bool:
    """"""
    if (string.__len__() == 0) or IsKeyword(string) or IsSoftKeyword(string):
        return False

    if is_hint:
        return (
            string.isidentifier()
            or (
                (string[0] == '"')
                and (string[-1] == '"')
                and string[1:-1].isidentifier()
                and not (IsKeyword(string[1:-1]) or IsSoftKeyword(string[1:-1]))
            )
            or set(string).issubset(HINT_CHARACTER_SET)
        )

    return string.isidentifier() and not hasattr(bltn, string)


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
