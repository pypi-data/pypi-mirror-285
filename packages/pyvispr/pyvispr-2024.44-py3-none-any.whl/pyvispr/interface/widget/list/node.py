"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
from re import search as SearchRegEx

from logger_36.instance.loggers import LOGGERS
from logger_36.logger import LogException
from pyvispr.config.appearance.color import ORANGE_BRUSH
from pyvispr.exception.catalog import NodeNotFoundError
from pyvispr.extension.qt.imports import qt_e
from pyvispr.flow.descriptive.node import node_t
from pyvispr.interface.widget.list.base import list_wgt_t
from pyvispr.runtime.catalog import NODE_CATALOG


@d.dataclass(slots=True, repr=False, eq=False)
class node_list_wgt_t(list_wgt_t):
    source: list[node_t] | tuple[str, ...] | None = None

    def __post_init__(self, element_name: str) -> None:
        """"""
        if self.source is None:
            self.source = NODE_CATALOG
        list_wgt_t.__post_init__(self, element_name)

    def ActualReload(self) -> None:
        """"""
        for node in self.source:
            if isinstance(node, str):
                try:
                    node = NODE_CATALOG[node]
                except NodeNotFoundError as exception:
                    LogException(exception, logger=LOGGERS.active)
                    continue

            self.addItem(node.name)
            item = self.item(self.count() - 1)
            if node.documentation is not None:
                item.setToolTip(node.documentation)
            if node.requires_completion:
                item.setForeground(ORANGE_BRUSH)

    def UpdateSource(self, source: list[node_t] | tuple[str, ...], /) -> None:
        """"""
        self.source = source
        self.Reload()

    def Filter(self, new_filter: str, /) -> None:
        """"""
        if new_filter.__len__() > 0:
            matched_items = self.findItems(new_filter, qt_e.MatchFlag.MatchContains)

            for item_idx in range(self.count()):
                node_item = self.item(item_idx)
                node_description = NODE_CATALOG[node_item.text()]

                if node_description.keywords is None:
                    mismatches_key_xpressions = True
                else:
                    mismatches_key_xpressions = (
                        new_filter not in node_description.keywords
                    )

                if node_description.short_description is None:
                    mismatches_short_description = True
                else:
                    mismatches_short_description = (
                        SearchRegEx(
                            "\b" + new_filter + "\b", node_description.short_description
                        )
                        is None
                    )

                node_item.setHidden(
                    (node_item not in matched_items)
                    and mismatches_key_xpressions
                    and mismatches_short_description
                )
        else:
            for item_idx in range(self.count()):
                self.item(item_idx).setHidden(False)


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
