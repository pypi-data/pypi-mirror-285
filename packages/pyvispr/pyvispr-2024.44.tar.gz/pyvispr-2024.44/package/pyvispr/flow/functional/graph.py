"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import textwrap as text
import typing as h

from logger_36.instance.loggers import LOGGERS
from pyvispr.flow.descriptive.intake import intake_t
from pyvispr.flow.functional.link import links_t
from pyvispr.flow.functional.node import node_t, state_e
from pyvispr.flow.functional.value import EncodedValue
from pyvispr.flow.naming import name_manager_t
from pyvispr.runtime.catalog import NODE_CATALOG
from pyvispr.runtime.config import APP_CONFIG


@d.dataclass(repr=False, eq=False)
class graph_t(list[node_t]):
    """
    Cannot be sloted because of QThread issue with weak reference (see visual.graph).
    """

    name_manager: name_manager_t = d.field(init=False, default_factory=name_manager_t)
    links: links_t = d.field(init=False, default_factory=links_t)

    def AddNode(
        self,
        stripe: str,
        /,
        *,
        wished_name: str | None = None,
        and_return_it: bool = False,
    ) -> node_t | None:
        """"""
        node = node_t.NewWithType(stripe, self.name_manager, wished_name=wished_name)
        if node is None:
            return None

        self.append(node)
        if and_return_it:
            return node

    def RemoveNode(self, node: node_t, /) -> None:
        """"""
        self.InvalidateNodeOutputs(node)

        self.RemoveLink(node, None, None, None)
        self.RemoveLink(None, None, node, None)

        self.remove(node)
        self.name_manager.RemoveName(node.name)

    def RenameNode(self, node: node_t, wished_name: str, /) -> None:
        """"""
        node.name = self.name_manager.NewUniqueName(
            wished_name, in_replacement_of=node.name
        )

    def AddLink(
        self, source: node_t, output_name: str, target: node_t, intake_name: str, /
    ) -> None:
        """"""
        self.links.Add(
            source,
            output_name,
            target,
            intake_name,
        )
        self.InvalidateNodeOutputs(target)

    def RemoveLink(
        self,
        source: node_t | None,
        output_name: str | None,
        target: node_t | None,
        intake_name: str | None,
        /,
    ) -> None:
        """
        Removes one or several links assuming that the link(s) exist(s).
        """
        if target is not None:
            self.InvalidateNodeOutputs(target)
        self.links.Remove(source, output_name, target, intake_name)

    def Run(
        self,
        /,
        *,
        workflow: str | None = None,
        script_accessor: h.TextIO = None,
    ) -> tuple[node_t, ...]:
        """"""
        if should_log_node_run := APP_CONFIG.should_log_node_run:
            LOGGERS.active.info(f"WORKFLOW {workflow}...")

        should_save_as_script = script_accessor is not None

        if should_save_as_script:
            _WritePrologue(self, script_accessor)
            values_script = {}
        else:
            values_script = None

        while True:
            needs_running = tuple(filter(lambda _elm: _elm.needs_running, self))
            if needs_running.__len__() == 0:
                break
            can_run = tuple(filter(lambda _elm: _elm.can_run, needs_running))
            if can_run.__len__() == 0:
                break

            for node in can_run:
                if should_save_as_script:
                    self._UpdateValuesForScript(values_script, node)

                if should_log_node_run:
                    LOGGERS.active.info(f"Running {node.name}")
                node.Run(
                    workflow=workflow,
                    script_accessor=script_accessor,
                    values_script=values_script,
                )
                self._SendOutputsThroughLinks(node)

        if should_save_as_script and (needs_running.__len__() > 0):
            script_accessor.write(
                'print("Workflow saving might be incomplete due to some nodes not '
                'being runnable.")'
            )

        if should_log_node_run:
            LOGGERS.active.info(f"WORKFLOW done (un-run: {needs_running.__len__()})")

        return needs_running

    def _UpdateValuesForScript(
        self, values_script: dict[str, str], node: node_t, /
    ) -> None:
        """"""
        values_script.clear()

        for name, intake in node.intakes.items():
            feeding_socket = self.links.IntakeSocketIsFree(
                node, name, should_return_socket=True
            )
            if feeding_socket is None:
                value_script = EncodedValue(intake.value)
            else:
                predecessor, name_s_out = feeding_socket
                description = NODE_CATALOG[node.catalog_name].intakes[name]
                if ShouldIgnorePredecessorValue(predecessor, name_s_out, description):
                    value_script = EncodedValue(description.default_value)
                else:
                    value_script = predecessor.FullNameOfOutput(name_s_out)
            values_script[name] = value_script

    def _SendOutputsThroughLinks(self, node: node_t, /) -> None:
        """"""
        for name_out, output in node.outputs.items():
            value = output.value
            successors = self.links.FirstDegreeSuccessors(node, output_name=name_out)
            for successor, socket_pairs in successors:
                for _, name_in in socket_pairs:
                    successor.SetIntakeValue(name_in, value)

    def ToggleNodeAbility(self, node: node_t, /) -> None:
        """"""
        if node.state is state_e.disabled:
            node.state = state_e.todo
        else:
            self.InvalidateNodeOutputs(node)
            node.state = state_e.disabled

    def SetNodeAbility(self, node: node_t, ability: bool, /) -> None:
        """"""
        if (ability and (node.state is state_e.disabled)) or not (
            ability or (node.state is state_e.disabled)
        ):
            self.ToggleNodeAbility(node)

    def InvalidateNodeOutputs(self, node: node_t, /) -> None:
        """"""
        if node.state is state_e.disabled:
            return

        node.InvalidateOutputs()

        for descendant in self.links.AllDegreesSuccessors(node):
            descendant, socket_pairs = descendant
            for _, intake_name in socket_pairs:
                descendant.InvalidateIntake(name=intake_name)

    def Invalidate(self) -> None:
        """"""
        for node in self:
            if node.state is not state_e.disabled:
                node.InvalidateIntake()

    def Clear(self) -> None:
        """"""
        # Do not iterate directly on the list since it is modified in the process.
        while self.__len__() > 0:
            self.RemoveNode(self[0])

    def __str__(self) -> str:
        """"""
        output = [
            "FUNCTIONAL GRAPH",
            f"Functional nodes: {self.__len__()}",
            f"Functional links: {sum(sum(_inr.__len__() for _inr in _elm.values()) for _elm in self.links.values())}",
            "NODE(S):",
        ]

        for node in self:
            output.append(text.indent(str(node), "    "))

        output.extend(("LINK(S):", text.indent(str(self.links), "    ")))

        return "\n".join(output)


def ShouldIgnorePredecessorValue(
    predecessor: node_t, output_name: str, current: intake_t, /
) -> bool:
    """"""
    return current.has_default and not predecessor.outputs[output_name].has_value


def _WritePrologue(nodes: h.Sequence[node_t], script_accessor: h.TextIO, /) -> None:
    """"""
    script_accessor.write(
        "from importlib import import_module\n"
        "from importlib import util\n"
        "from pathlib import Path as path_t\n"
        "from json_any import JsonStringOf, ObjectFromJsonString\n\n"
    )

    already_written = []
    for node in nodes:
        if node.state is state_e.disabled:
            continue

        description = NODE_CATALOG[node.catalog_name]
        if description in already_written:
            continue

        actual_path = description.actual.path
        actual_name = description.actual.name
        if isinstance(actual_path, str):
            loading = f'module = import_module("{actual_path}")'
        else:
            ldg_path = f'path = path_t("{actual_path}").expanduser()'
            ldg_spec = "spec = util.spec_from_file_location(path.stem, path)"
            ldg_module = "module = spec.loader.load_module(spec.name)"
            loading = f"{ldg_path}\n{ldg_spec}\n{ldg_module}"
        getting = (
            f"{description.function_name_for_script} = "
            f'getattr(module, "{actual_name}")'
        )
        script_accessor.write(f"{loading}\n{getting}\n\n")
        already_written.append(description)


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
