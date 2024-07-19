"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h

from pyvispr.extension.qt.imports import qtgi, qtwg
from pyvispr.runtime.backend import SCREEN_BACKEND


class entry_t(h.NamedTuple):
    text: str
    #
    action: str | h.Callable[..., ...] | None = None
    args: h.Any | tuple[h.Any, ...] | None = None
    kwargs: dict[str, h.Any] | None = None
    #
    disabled: bool = False
    checkable: bool = False
    checked: bool = False
    shortcut: qtgi.QKeySequence | qtgi.QKeySequence.StandardKey | str | None = None
    status_tip: str | None = None


entries_h = entry_t | tuple[entry_t, ...] | str | None


def BuildMenu(
    menu: qtwg.QMenu,
    entries: entries_h | dict[str, entries_h],
    manager: h.Any,
    /,
    *,
    should_return_entries: str | h.Sequence[str] | None = None,
) -> dict[str, qtwg.QMenu | qtgi.QAction] | None:
    """"""
    if isinstance(entries, str):
        DynamicEntries = getattr(manager, entries)
        entries = DynamicEntries()
    if isinstance(entries, entry_t):
        entries = (entries,)

    return AddEntriesToMenu(
        entries, menu, manager, should_return_entries=should_return_entries
    )


def AddEntriesToMenu(
    entries: tuple[entry_t, ...],
    menu: qtwg.QMenu,
    manager: qtwg.QWidget,
    /,
    *,
    should_return_entries: str | h.Sequence[str] | None = None,
) -> dict[str, qtwg.QMenu | qtgi.QAction] | None:
    """"""
    output = {}

    if should_return_entries is None:
        should_return_entries = ()
    elif isinstance(should_return_entries, str):
        should_return_entries = (should_return_entries,)

    for entry in entries:
        if isinstance(entry, entry_t):
            action = AddEntryToMenu(entry, menu, manager)
            if entry.text in should_return_entries:
                output[entry.text] = action
        elif entry is None:
            menu.addSeparator()
        else:
            entry: dict[str, entries_h]
            for text, sub_entries in entry.items():
                sub_menu = menu.addMenu(text)
                if text in should_return_entries:
                    output[text] = sub_menu
                sub_entries = BuildMenu(
                    sub_menu,
                    sub_entries,
                    manager,
                    should_return_entries=should_return_entries,
                )
                if sub_entries is not None:
                    output.update(sub_entries)

    if should_return_entries.__len__() > 0:
        return output


def AddEntryToMenu(
    entry: entry_t,
    menu: qtwg.QMenu,
    manager: qtwg.QWidget,
    /,
) -> qtgi.QAction:
    """"""
    qt_action = qtgi.QAction(entry.text, parent=manager)

    if entry.action is None:
        qt_action.setEnabled(False)
    else:
        if isinstance(entry.action, str):
            action = manager
            for piece in entry.action.split("."):
                action = getattr(action, piece)
        else:
            action = entry.action
        if entry.args is None:
            args = ()
        elif isinstance(entry.args, tuple):
            args = entry.args
        else:
            args = (entry.args,)
        if entry.kwargs is None:
            kwargs = {}
        else:
            kwargs = entry.kwargs
        SCREEN_BACKEND.AddMessageCanal(qt_action, "triggered", action, *args, **kwargs)

    if entry.status_tip is not None:
        qt_action.setStatusTip(entry.status_tip)
    if entry.shortcut is not None:
        qt_action.setShortcut(entry.shortcut)
    if entry.disabled:
        qt_action.setEnabled(False)
    if entry.checkable:
        qt_action.setCheckable(True)
        qt_action.setChecked(entry.checked)

    menu.addAction(qt_action)

    return qt_action


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
