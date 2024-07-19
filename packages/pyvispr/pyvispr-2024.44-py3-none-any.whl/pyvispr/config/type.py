"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h
from configparser import DEFAULTSECT as DEFAULT_SECTION
from configparser import ConfigParser as config_parser_t
from pathlib import Path as path_t

from logger_36.instance.loggers import LOGGERS
from logger_36.logger import LogException
from pyvispr.config.constant import (
    APPEARANCE_SECTION,
    DEFAULT_CONFIG,
    HISTORY_N_NODES_MOST_USED,
    HISTORY_N_NODES_RECENT,
    HISTORY_NODE_USAGE_SEPARATOR,
    HISTORY_NODES_MOST_USED,
    HISTORY_NODES_RECENT,
    HISTORY_NODES_SEPARATOR,
    HISTORY_SECTION,
    LINK_SMOOTH,
    LOG_NODE_RUN,
    LOG_SECTION,
    PATH_FLOWS_RECENT,
    PATH_LAST_LOADING_FOLDER,
    PATH_LAST_SAVING_AS_SCREENSHOT_FOLDER,
    PATH_LAST_SAVING_AS_SCRIPT_FOLDER,
    PATH_LAST_SAVING_FOLDER,
    PATH_N_FLOWS_RECENT,
    PATH_SECTION,
    PATH_SEPARATOR,
)
from pyvispr.config.path import CONFIG_FILE
from pyvispr.exception.catalog import NodeNotFoundError
from pyvispr.extension.object.text import AsStr
from pyvispr.runtime.catalog import NODE_CATALOG

load_mode_h = h.Literal[
    "load",
    "load recent",
]
save_mode_h = h.Literal["save", "save as", "save as script", "save as screenshot"]


# /!\ Must be larger than the length of argument "etc".
_MAX_LENGTH = 30
_DELIMITER = "="


class config_t(dict[str, h.Any]):
    @staticmethod
    def NewConfigParser() -> config_parser_t:
        """"""
        return config_parser_t(delimiters=_DELIMITER, comment_prefixes="#")

    def __init__(self) -> None:
        """"""
        dict.__init__(self)
        self.Load()

    def Load(self) -> None:
        """"""
        ini_config = config_t.NewConfigParser()
        ini_config.read_dict(DEFAULT_CONFIG)
        ini_config.read(CONFIG_FILE)

        self.clear()
        self.update(
            {
                _nme: dict(_sct)
                for _nme, _sct in ini_config.items()
                if _nme != DEFAULT_SECTION
            }
        )

        history_section = self[HISTORY_SECTION]
        path_section = self[PATH_SECTION]

        for which in (HISTORY_N_NODES_RECENT, HISTORY_N_NODES_MOST_USED):
            history_section[which] = int(history_section[which])

        history_section[HISTORY_NODES_RECENT] = _Split(
            history_section[HISTORY_NODES_RECENT], HISTORY_NODES_SEPARATOR
        )
        invalid_s = []
        for name in history_section[HISTORY_NODES_RECENT]:
            try:
                _ = NODE_CATALOG[name]
            except NodeNotFoundError as exception:
                invalid_s.append(name)
                LogException(exception, logger=LOGGERS.active)
        for invalid in invalid_s:
            history_section[HISTORY_NODES_RECENT].remove(invalid)

        nodes = history_section[HISTORY_NODES_MOST_USED]
        if nodes is None:
            nodes = {}
        elif HISTORY_NODES_SEPARATOR in nodes:
            nodes = nodes.split(HISTORY_NODES_SEPARATOR)
            nodes = map(lambda _elm: _elm.split(HISTORY_NODE_USAGE_SEPARATOR), nodes)
            nodes = map(lambda _elm: [_elm[0], int(_elm[1])], nodes)
            nodes = dict(nodes)
        elif nodes.__len__() > 0:
            name, usage = nodes.split(HISTORY_NODE_USAGE_SEPARATOR)
            nodes = {name: int(usage)}
        else:
            nodes = {}
        for name in tuple(nodes.keys()):
            try:
                _ = NODE_CATALOG[name]
            except NodeNotFoundError as exception:
                del nodes[name]
                LogException(exception, logger=LOGGERS.active)
        history_section[HISTORY_NODES_MOST_USED] = nodes

        for which in (
            PATH_LAST_LOADING_FOLDER,
            PATH_LAST_SAVING_FOLDER,
            PATH_LAST_SAVING_AS_SCRIPT_FOLDER,
            PATH_LAST_SAVING_AS_SCREENSHOT_FOLDER,
        ):
            path_section[which] = path_t(path_section[which])

        path_section[PATH_N_FLOWS_RECENT] = int(path_section[PATH_N_FLOWS_RECENT])
        paths = _Split(path_section[PATH_FLOWS_RECENT], PATH_SEPARATOR)
        path_section[PATH_FLOWS_RECENT] = list(map(path_t, paths))

        for section, parameter in (
            (LOG_SECTION, LOG_NODE_RUN),
            (APPEARANCE_SECTION, LINK_SMOOTH),
        ):
            self[section][parameter] = self[section][parameter].lower() == "true"

    @property
    def recent_nodes(self) -> tuple[str, ...]:
        """"""
        return tuple(self[HISTORY_SECTION][HISTORY_NODES_RECENT])

    @property
    def most_used_nodes(self) -> tuple[str, ...]:
        """"""
        history_section = self[HISTORY_SECTION]
        nodes = history_section[HISTORY_NODES_MOST_USED].items()
        nodes = sorted(nodes, key=lambda _elm: _elm[1], reverse=True)
        nodes = nodes[: history_section[HISTORY_N_NODES_MOST_USED]]
        nodes = (_elm[0] for _elm in nodes)

        return tuple(nodes)

    def UpdateRecentNodes(self, name: str, /) -> None:
        """"""
        history_section = self[HISTORY_SECTION]
        _UpdateRecent_s(
            history_section[HISTORY_NODES_RECENT],
            name,
            history_section[HISTORY_N_NODES_RECENT],
        )

    def UpdateMostUsedNodes(self, name: str, /) -> None:
        """"""
        nodes = self[HISTORY_SECTION][HISTORY_NODES_MOST_USED]
        if name in nodes:
            nodes[name] += 1
        else:
            nodes[name] = 1

    @property
    def recent_flows(self) -> tuple[path_t, ...]:
        """"""
        output = self[PATH_SECTION][PATH_FLOWS_RECENT]
        output = filter(lambda _elm: _elm.is_file(), output)
        return tuple(output)

    def UpdateRecentFlows(self, path: path_t, /) -> None:
        """"""
        path_section = self[PATH_SECTION]
        _UpdateRecent_s(
            path_section[PATH_FLOWS_RECENT],
            path,
            path_section[PATH_N_FLOWS_RECENT],
        )

    @property
    def last_loading_folder(self) -> path_t:
        """"""
        return self[PATH_SECTION][PATH_LAST_LOADING_FOLDER]

    def UpdateLastLoadingFolder(self, folder: path_t, /) -> None:
        """"""
        self[PATH_SECTION][PATH_LAST_LOADING_FOLDER] = folder

    def LastSavingFolder(self, which: save_mode_h, /) -> path_t:
        """"""
        if which in ("save", "save as"):
            return self[PATH_SECTION][PATH_LAST_SAVING_FOLDER]
        if which == "save as script":
            return self[PATH_SECTION][PATH_LAST_SAVING_AS_SCRIPT_FOLDER]
        if which == "save as screenshot":
            return self[PATH_SECTION][PATH_LAST_SAVING_AS_SCREENSHOT_FOLDER]

    def UpdateLastSavingFolder(self, which: save_mode_h, folder: path_t, /) -> None:
        """"""
        if which in ("save", "save as"):
            self[PATH_SECTION][PATH_LAST_SAVING_FOLDER] = folder
        if which == "save as script":
            self[PATH_SECTION][PATH_LAST_SAVING_AS_SCRIPT_FOLDER] = folder
        if which == "save as screenshot":
            self[PATH_SECTION][PATH_LAST_SAVING_AS_SCREENSHOT_FOLDER] = folder

    @property
    def should_log_node_run(self) -> bool:
        """"""
        return self[LOG_SECTION][LOG_NODE_RUN]

    def Save(self) -> None:
        """"""
        formatted = {
            _ky1: {_ky2: _vl2 for _ky2, _vl2 in _vl1.items()}
            for _ky1, _vl1 in self.items()
        }

        history_section = formatted[HISTORY_SECTION]
        path_section = formatted[PATH_SECTION]

        history_section[HISTORY_NODES_RECENT] = HISTORY_NODES_SEPARATOR.join(
            history_section[HISTORY_NODES_RECENT]
        )

        nodes = history_section[HISTORY_NODES_MOST_USED].items()
        nodes = map(
            lambda _elm: f"{_elm[0]}{HISTORY_NODE_USAGE_SEPARATOR}{_elm[1]}", nodes
        )
        history_section[HISTORY_NODES_MOST_USED] = HISTORY_NODES_SEPARATOR.join(nodes)

        path_section[PATH_FLOWS_RECENT] = PATH_SEPARATOR.join(
            map(str, path_section[PATH_FLOWS_RECENT])
        )

        config = config_t.NewConfigParser()
        config.read_dict(formatted)
        with open(CONFIG_FILE, "w") as accessor:
            config.write(accessor)

    def SaveRawAndReload(self, text: str, /) -> None:
        """"""
        if text[-1] != "\n":
            text += "\n"

        with open(CONFIG_FILE, "w") as accessor:
            accessor.write(text)
        self.Load()

    def AsStr(
        self,
        /,
        *,
        max_length: int | None = _MAX_LENGTH,
        bold: tuple[str, str] = ("<b>", "</b>"),
        newline: str = "<br/>",
        etc: str = " [...]",
    ) -> str:
        """
        Unfortunately, pprint.pformat fails to effectively pretty-print.
        """
        output = []

        if max_length is None:
            truncated_max_length = None
        else:
            truncated_max_length = max_length - etc.__len__()
        for key1, value1 in self.items():
            output.append(f"{bold[0]}[{key1}]{bold[1]}")

            for key2, value2 in value1.items():
                value2 = AsStr(value2)
                both_ends = value2[0] + value2[-1]
                if both_ends in ("()", "[]", "{}", "''", '""'):
                    value2 = value2[1:-1]
                if (max_length is not None) and (value2.__len__() > max_length):
                    value2 = value2[:truncated_max_length] + etc
                output.append(f"{key2} {_DELIMITER} {value2}")

        return newline.join(output)


def _Split(joined: str | None, separator: str, /) -> list[str]:
    """"""
    if joined is None:
        return []

    if separator in joined:
        return joined.split(separator)

    if joined.__len__() > 0:
        return [joined]

    return []


def _UpdateRecent_s(
    recent_s: list[h.Any], new_element: h.Any, max_length: int, /
) -> None:
    """"""
    if new_element in recent_s:
        recent_s.remove(new_element)
        recent_s.insert(0, new_element)
    else:
        recent_s.insert(0, new_element)
        if recent_s.__len__() > max_length:
            del recent_s[-1]


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
