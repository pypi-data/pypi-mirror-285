"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h

from pyvispr.extension.qt.imports import qtgi, qtwg


class node_menu_info_t(qtwg.QMenu):

    def __init__(self) -> None:
        """"""
        qtwg.QMenu.__init__(self)

        self.cancel_action = self.addAction("Close Menu")
        no_action = self.addAction("or")
        self.documentation_action = self.addAction("Show Documentation")
        self.in_out_action = self.addAction("Show Inputs/Outputs")

        no_action.setEnabled(False)


class node_menu_edit_t(qtwg.QMenu):

    def __init__(self) -> None:
        """"""
        qtwg.QMenu.__init__(self)

        self.cancel_action = self.addAction("Close Menu")
        no_action = self.addAction("or")
        self.invalidate_action = self.addAction("Invalidate Node")
        self.disable_action = self.addAction("??? Node")
        self.remove_action = self.addAction("Remove Node")

        no_action.setEnabled(False)

    def Update(self, node_is_disabled: bool, /) -> None:
        """"""
        if node_is_disabled:
            operation = "Enable"
        else:
            operation = "Disable"
        self.disable_action.setText(f"{operation} Node")


class nodes_menu_edit_t(qtwg.QMenu):

    def __init__(self) -> None:
        """"""
        qtwg.QMenu.__init__(self)

        self.cancel_action = self.addAction("Close Menu")
        no_action = self.addAction("or")
        self.invalidate_action = self.addAction("Invalidate Node(s)")
        self.disable_action = self.addAction("Disable Node(s)")
        self.enable_action = self.addAction("Enable Node(s)")
        self.remove_action = self.addAction("Remove Node(s)")

        no_action.setEnabled(False)


class link_menu_t(qtwg.QMenu):
    def __init__(self) -> None:
        """"""
        qtwg.QMenu.__init__(self)

        self.cancel_action = self.addAction("Close Menu")
        no_action = self.addAction("or Remove Link(s):")
        no_action.setEnabled(False)
        self.n_links = 0
        self.remove_actions: list[qtgi.QAction] = []
        self.remove_all_action: qtgi.QAction | None = None

    def Update(self, links: h.Sequence[tuple[str, str]], /) -> None:
        """"""
        for action in self.remove_actions:
            self.removeAction(action)

        self.n_links = links.__len__()
        self.remove_actions = [
            self.addAction(f"{_elm[0]} -> {_elm[1]}") for _elm in links
        ]
        if self.n_links > 1:
            self.remove_all_action = self.addAction("Remove All")
            self.remove_actions.append(self.remove_all_action)
        else:
            self.remove_all_action = None


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
