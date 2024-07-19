"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

from pyvispr.constant.interface.storage.path import HOME_FOLDER

HISTORY_SECTION = "HISTORY"
HISTORY_N_NODES_RECENT = "n recent nodes"
HISTORY_N_NODES_MOST_USED = "n most used nodes"
HISTORY_NODES_RECENT = "recent nodes"
HISTORY_NODES_MOST_USED = "most used nodes"
HISTORY_NODES_SEPARATOR = ", "
HISTORY_NODE_USAGE_SEPARATOR = ":"

PATH_SECTION = "PATH"
PATH_LAST_LOADING_FOLDER = "last loading folder"
PATH_LAST_SAVING_FOLDER = "last saving folder"
PATH_LAST_SAVING_AS_SCRIPT_FOLDER = "last saving-as-script folder"
PATH_LAST_SAVING_AS_SCREENSHOT_FOLDER = "last saving-as-screenshot folder"
PATH_N_FLOWS_RECENT = "n recent flows"
PATH_FLOWS_RECENT = "recent flows"
PATH_SEPARATOR = HISTORY_NODES_SEPARATOR

LOG_SECTION = "LOG"
LOG_NODE_RUN = "node run"

APPEARANCE_SECTION = "APPEARANCE"
LINK_SMOOTH = "smooth links"

DEFAULT_CONFIG = {
    HISTORY_SECTION: {
        HISTORY_N_NODES_RECENT: 20,
        HISTORY_N_NODES_MOST_USED: 20,
        HISTORY_NODES_RECENT: "",
        HISTORY_NODES_MOST_USED: "",
    },
    PATH_SECTION: {
        PATH_LAST_LOADING_FOLDER: HOME_FOLDER,
        PATH_LAST_SAVING_FOLDER: HOME_FOLDER,
        PATH_LAST_SAVING_AS_SCRIPT_FOLDER: HOME_FOLDER,
        PATH_LAST_SAVING_AS_SCREENSHOT_FOLDER: HOME_FOLDER,
        PATH_N_FLOWS_RECENT: 10,
        PATH_FLOWS_RECENT: "",
    },
    LOG_SECTION: {
        LOG_NODE_RUN: True,
    },
    APPEARANCE_SECTION: {LINK_SMOOTH: False},
}

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
