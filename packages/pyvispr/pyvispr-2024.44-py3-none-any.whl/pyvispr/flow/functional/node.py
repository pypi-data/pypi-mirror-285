"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import time
import typing as h
from enum import Enum as enum_t

from logger_36.instance.loggers import LOGGERS
from logger_36.logger import LogException
from pyvispr.constant.flow.node import (
    MSG_NEW_NODE_INTAKE,
    MSG_NEW_NODE_OUTPUT,
    MSG_NEW_NODE_STATE,
    UNIQUE_NAME_INTAKE,
)
from pyvispr.constant.flow.uid import UNIQUE_OUTPUT_NAME_SEPARATOR
from pyvispr.constant.flow.value import VALUE_NOT_SET, value_loop_done_t
from pyvispr.exception.catalog import NodeNotFoundError
from pyvispr.flow.functional.socket import intake_t, output_t
from pyvispr.flow.naming import name_manager_t
from pyvispr.runtime.catalog import NODE_CATALOG
from sio_messenger import MESSENGER


class state_e(enum_t):
    disabled = 0
    todo = 1
    doing = 2
    done = 3
    done_with_error = -1


@d.dataclass(slots=True, repr=False, eq=False)
class node_t:
    name: str
    catalog_name: str
    intakes: dict[str, intake_t]
    outputs: dict[str, output_t]
    state: state_e = state_e.todo

    name_for_script: str | None = None

    @classmethod
    def NewWithType(
        cls,
        stripe: str,
        name_manager: name_manager_t,
        /,
        *,
        wished_name: str | None = None,
    ) -> h.Self | None:
        """"""
        try:
            description = NODE_CATALOG[stripe]
        except NodeNotFoundError as exception:
            LogException(exception, logger=LOGGERS.active)
            return None
        description.Activate()

        if wished_name is None:
            wished_name = description.name  # == stripe.
        name = name_manager.NewUniqueName(wished_name)

        intakes = {_nme: intake_t() for _nme in description.intakes}
        outputs = {_nme: output_t() for _nme in description.outputs}

        return cls(
            name=name,
            catalog_name=description.name,
            intakes=intakes,
            outputs=outputs,
        )

    def FullNameOfOutput(self, output_name: str, /) -> str:
        """"""
        if self.name_for_script is None:
            self.name_for_script = f"{self.catalog_name}_{time.monotonic_ns()}"
        return f"{self.name_for_script}{UNIQUE_OUTPUT_NAME_SEPARATOR}{output_name}"

    @property
    def needs_running(self) -> bool:
        """"""
        return self.state is state_e.todo

    @property
    def can_run(self) -> bool:
        """
        It must have been checked that the state is not disabled.

        This method is meant to be called from functional.graph.Run,
        i.e., after visual.Run has read the ii_values
        to set the corresponding node input values if appropriate.
        Appropriate means: the corresponding intakes have mode "full" (actually,
        not "link") and they are not linked to outputs.
        """
        return (self.intakes.__len__() == 0) or all(
            _elm.has_value for _elm in self.intakes.values()
        )

    def Run(
        self,
        /,
        *,
        workflow: str | None = None,
        script_accessor: h.TextIO | None = None,
        values_script: dict[str, str] | None = None,
    ) -> None:
        """
        It must have been checked that the state is not disabled.
        """
        self.state = state_e.doing
        MESSENGER.Transmit(MSG_NEW_NODE_STATE, self)

        should_save_as_script = script_accessor is not None

        description = NODE_CATALOG[self.catalog_name]
        if should_save_as_script:
            if description.n_outputs > 0:
                output_assignments = (
                    self.FullNameOfOutput(_elm) for _elm in self.outputs
                )
                output_assignments = ", ".join(output_assignments) + " = "
            else:
                output_assignments = ""
        else:
            output_assignments = None

        if description.n_intakes > 0:
            anonymous_args = []
            named_args = {}
            anonymous_args_script = []
            named_args_script = []

            for name, intake in description.intakes.items():
                value = self.intakes[name].value

                if intake.has_default:
                    named_args[name] = value
                    if should_save_as_script and (name != UNIQUE_NAME_INTAKE):
                        named_args_script.append(f"{name}={values_script[name]}")
                else:
                    anonymous_args.append(value)
                    if should_save_as_script:
                        anonymous_args_script.append(values_script[name])
            if description.wants_unique_name:
                # This overwrites the already present, None default value.
                if workflow is None:
                    unique_name = self.name
                else:
                    unique_name = f"{workflow}.{self.name}"
                named_args[UNIQUE_NAME_INTAKE] = unique_name

                if should_save_as_script:
                    named_args_script.append(f'{UNIQUE_NAME_INTAKE}="{self.name}"')

            output_values, error = self._RunSafely(anonymous_args, named_args)

            if should_save_as_script and not error:
                arguments = ", ".join(anonymous_args_script + named_args_script)
                script_accessor.write(
                    f"{output_assignments}{description.function_name_for_script}"
                    f"({arguments})\n"
                )
        else:
            output_values, error = self._RunSafely(None, None)

            if should_save_as_script and not error:
                script_accessor.write(
                    f"{output_assignments}"
                    f"{description.function_name_for_script}()\n"
                )

        # Since output values are computed here, it makes more sense to directly set
        # them, as opposed to returning them and letting the caller doing it. Hence,
        # _SetOutputValue is meant for internal use, whereas SetIntakeValue is meant for
        # external use.
        output_names = description.output_names
        n_outputs = output_names.__len__()
        if n_outputs > 1:
            for name, value in zip(output_names, output_values):
                self._SetOutputValue(name, value)
        elif n_outputs > 0:
            self._SetOutputValue(output_names[0], output_values)

        if error:
            self.state = state_e.done_with_error
        else:
            self.state = state_e.done
        MESSENGER.Transmit(MSG_NEW_NODE_STATE, self)

    def _RunSafely(
        self,
        anonymous_args: h.Sequence[h.Any] | None,
        named_args: dict[str, h.Any] | None,
        /,
    ) -> tuple[h.Any | None, bool]:
        """"""
        description = NODE_CATALOG[self.catalog_name]
        try:
            if anonymous_args is None:
                output = description.RunFunction()
            else:
                output = description.RunFunction(*anonymous_args, **named_args)
            error = False
        except Exception as exception:
            if (n_outputs := description.n_outputs) > 1:
                output = n_outputs * (VALUE_NOT_SET,)
            else:
                output = VALUE_NOT_SET
            error = True
            LOGGERS.active.error(f"Error while running {self.name}:")
            LogException(exception, logger=LOGGERS.active, should_remove_caller=True)

        return output, error

    def SetIntakeValue(self, name: str, value: h.Any, /) -> None:
        """"""
        if isinstance(value, value_loop_done_t):
            # This makes the node un-runnable. However, the invalidation of the outputs
            # is not wanted since this would trigger the invalidation of the outputs of
            # the last node in the loop body, thus depriving the subsequent nodes of
            # their intakes.
            value = VALUE_NOT_SET
        else:
            self.InvalidateOutputs()
        self.intakes[name].value = value
        MESSENGER.Transmit(MSG_NEW_NODE_INTAKE, self)

    def _SetOutputValue(self, name: str, value: h.Any, /) -> None:
        """"""
        self.outputs[name].value = value
        MESSENGER.Transmit(MSG_NEW_NODE_OUTPUT, self)

    def InvalidateIntake(self, /, *, name: str | None = None) -> None:
        """"""
        if name is None:
            for element in self.intakes.values():
                element.value = VALUE_NOT_SET
        else:
            self.intakes[name].value = VALUE_NOT_SET

        if self.intakes.__len__() > 0:
            MESSENGER.Transmit(MSG_NEW_NODE_INTAKE, self)

        self.InvalidateOutputs()

    def InvalidateOutputs(self) -> None:
        """"""
        if self.outputs.__len__() > 0:
            for element in self.outputs.values():
                element.value = VALUE_NOT_SET
            MESSENGER.Transmit(MSG_NEW_NODE_OUTPUT, self)

        self.state = state_e.todo
        MESSENGER.Transmit(MSG_NEW_NODE_STATE, self)

    def __str__(self) -> str:
        """"""
        description = NODE_CATALOG[self.catalog_name]
        return "\n".join(
            (
                self.name,
                f"Function: {description.module.__name__}.{description.actual.name}",
                f"State: {self.state.name}",
            )
        )


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
