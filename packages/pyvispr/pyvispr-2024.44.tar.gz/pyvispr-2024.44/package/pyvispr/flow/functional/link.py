"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import collections as c
import dataclasses as d

from pyvispr.constant.flow.value import VALUE_NOT_SET
from pyvispr.exception.link import ExistingLinkError, LinkNotFoundError
from pyvispr.flow.functional.node import node_t, state_e

socket_pairs_h = list[tuple[str, str]]


@d.dataclass(slots=True, repr=False, eq=False)
class links_t(dict[node_t, c.defaultdict[node_t, socket_pairs_h]]):

    def __missing__(self, _, /) -> c.defaultdict:
        """"""
        return c.defaultdict(lambda: [])

    def Add(
        self,
        source: node_t,
        output_name: str,
        target: node_t,
        intake_name: str,
        /,
    ) -> None:
        """"""
        socket_pair = (output_name, intake_name)

        if source not in self:
            self[source] = c.defaultdict(lambda: [], {target: []})
        elif target not in self[source]:
            self[source][target] = []
        elif socket_pair in self[source][target]:
            raise ExistingLinkError(
                f"Link {source.name}.{output_name} -> "
                f"{target.name}.{intake_name} already present."
            )

        self[source][target].append(socket_pair)

        value = source.outputs[output_name].value
        target.SetIntakeValue(intake_name, value)

    def Remove(
        self,
        source: node_t | None,
        output_name: str | None,
        target: node_t | None,
        intake_name: str | None,
        /,
    ) -> None:
        """"""
        to_be_removed = []
        for current_src, links in self.items():
            if source in (None, current_src):
                for current_tgt, socket_pairs in links.items():
                    if target in (None, current_tgt):
                        for current_out, current_in in socket_pairs:
                            if (output_name in (None, current_out)) and (
                                intake_name in (None, current_in)
                            ):
                                to_be_removed.append(
                                    (
                                        (current_src, current_tgt),
                                        (current_out, current_in),
                                    )
                                )

        if to_be_removed.__len__() == 0:
            if (source is not None) and (target is not None):
                raise LinkNotFoundError(
                    f"No link(s) {source.name}.{output_name} -> "
                    f"{target.name}.{intake_name} found."
                )
            return

        for (current_src, current_tgt), socket_pair in to_be_removed:
            socket_pairs = self[current_src][current_tgt]
            # Remove socket pair from link, then remove link if no sockets remain.
            socket_pairs.remove(socket_pair)
            if socket_pairs.__len__() == 0:
                del self[current_src][current_tgt]
                if self[current_src].__len__() == 0:
                    del self[current_src]
            current_tgt.SetIntakeValue(socket_pair[1], VALUE_NOT_SET)

    def IntakeSocketIsFree(
        self, node: node_t, intake_name: str, /, *, should_return_socket: bool = False
    ) -> bool | tuple[node_t, str] | None:
        """"""
        for source, links in self.items():
            for target, socket_pairs in links.items():
                if target is node:
                    if should_return_socket:
                        for s_out, s_in in socket_pairs:
                            if s_in == intake_name:
                                return source, s_out
                    elif any(_s_in == intake_name for _, _s_in in socket_pairs):
                        return False

        if should_return_socket:
            return None
        return True

    def FirstDegreeSuccessors(
        self, node: node_t, /, *, output_name: str | None = None
    ) -> tuple[tuple[node_t, socket_pairs_h], ...]:
        """"""
        output = []

        for source, links in self.items():
            if source is node:
                for target, socket_pairs in links.items():
                    if target.state is state_e.disabled:
                        continue

                    if output_name is not None:
                        socket_pairs = list(
                            filter(lambda _elm: _elm[0] == output_name, socket_pairs)
                        )
                    output.append((target, socket_pairs))

        return tuple(output)

    def AllDegreesSuccessors(
        self, node: node_t, /, *, visited: list[node_t] | None = None
    ) -> tuple[tuple[node_t, socket_pairs_h], ...]:
        """"""
        output = []

        if visited is None:
            visited = [node]

        found = True
        while found:
            found = False
            for source, links in self.items():
                if source is node:
                    for target, socket_pairs in links.items():
                        if (target in visited) or (target.state is state_e.disabled):
                            continue

                        visited.append(target)
                        output.append((target, socket_pairs))
                        output.extend(
                            self.AllDegreesSuccessors(target, visited=visited)
                        )
                        found = True

        return tuple(output)

    def __str__(self) -> str:
        """"""
        output = []

        for source, links in self.items():
            for target, socket_pairs in links.items():
                output.append(f"{source.name} => {target.name}")
                for socket_pair in socket_pairs:
                    output.append(f"    {socket_pair[0]} -> {socket_pair[1]}")

        return "\n".join(output)


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
