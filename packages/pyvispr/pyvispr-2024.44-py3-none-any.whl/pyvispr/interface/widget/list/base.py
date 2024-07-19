"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d

from pyvispr.constant.interface.widget.list import COL_SIZE_PADDING, MAX_LIST_WIDTH
from pyvispr.extension.object.field import NON_INIT_FIELD
from pyvispr.extension.qt.imports import qt_e, qtwg
from pyvispr.runtime.backend import SCREEN_BACKEND


@d.dataclass(slots=True, repr=False, eq=False)
class list_wgt_t(qtwg.QListWidget):
    should_be_sorted: bool = True
    filter_wgt: qtwg.QLineEdit = NON_INIT_FIELD
    element_name: d.InitVar[str] = "MISSING ELEMENT NAME"

    def __post_init__(self, element_name: str) -> None:
        """"""
        qtwg.QListWidget.__init__(self)
        self.setSelectionMode(qtwg.QAbstractItemView.SelectionMode.NoSelection)

        filter_wgt = qtwg.QLineEdit()
        filter_wgt.setPlaceholderText(f"Filter {element_name}")
        filter_wgt.setClearButtonEnabled(True)
        SCREEN_BACKEND.AddMessageCanal(filter_wgt, "textEdited", self.Filter)
        self.filter_wgt = filter_wgt

        self.Reload()

    def AddDisabledItem(self, text: str, /) -> None:
        """"""
        self.addItem(text)
        _DisableItem(self.item(self.count() - 1))

    def Reload(self) -> None:
        """"""
        self.clear()
        self.ActualReload()
        if self.should_be_sorted:
            self.sortItems()

        width = min(self.sizeHintForColumn(0) + COL_SIZE_PADDING, MAX_LIST_WIDTH)
        self.setFixedWidth(width)
        self.filter_wgt.setFixedWidth(width)

    def ActualReload(self) -> None:
        """"""
        raise NotImplementedError

    def Filter(self, new_filter: str, /) -> None:
        """"""
        if new_filter.__len__() > 0:
            matched_items = self.findItems(new_filter, qt_e.MatchFlag.MatchContains)

            for item_idx in range(self.count()):
                node_item = self.item(item_idx)

                if node_item not in matched_items:
                    node_item.setHidden(True)
                else:
                    node_item.setHidden(False)
        else:
            for item_idx in range(self.count()):
                self.item(item_idx).setHidden(False)

    def SelectedItemsOrAll(self) -> tuple[qtwg.QListWidgetItem, ...]:
        """"""
        output = self.selectedItems()

        if output.__len__() == 0:
            output = (self.item(_row) for _row in range(self.count()))
            output = filter(ItemIsEnabled, output)

        return tuple(output)


def _DisableItem(item: qtwg.QListWidgetItem, /) -> None:
    """"""
    item.setFlags(item.flags() & ~qt_e.ItemFlag.ItemIsEnabled)


def ItemIsEnabled(item: qtwg.QListWidgetItem, /) -> bool:
    """"""
    return (item.flags() & qt_e.ItemFlag.ItemIsEnabled) == qt_e.ItemFlag.ItemIsEnabled


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
