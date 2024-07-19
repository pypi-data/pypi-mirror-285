"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import ast as prsr
import dataclasses as d
import inspect as spct
import typing as h
from enum import Enum as enum_t
from pathlib import Path as path_t
from types import EllipsisType
from types import ModuleType as module_t

from logger_36.instance.loggers import LOGGERS
from pyvispr.catalog.parser import N_A_F_A
from pyvispr.constant.flow.node import (
    NO_ANNOTATION,
    NO_OUTPUT_NAMES,
    UNIQUE_NAME_INTAKE,
)
from pyvispr.extension.introspection.function import FirstFunctionAsAstNode
from pyvispr.extension.introspection.module import (
    M_F_FromPathAndName,
    M_F_FromPyPathAndName,
)
from pyvispr.extension.object.field import NonInitField_NONE
from pyvispr.flow.descriptive.intake import IntakesFromAST, intake_t
from str_to_obj.api.type import type_t


class installation_type_e(enum_t):
    not_set = 0
    local = 1
    referenced = 2
    system = 3


class _function_t(h.NamedTuple):
    """
    path: Either a path or py_path to module.
    """

    path: path_t | str
    name: str


@d.dataclass(slots=True, repr=False, eq=False)
class node_t:
    name: str
    keywords: str
    short_description: str
    long_description: str
    installation_type: installation_type_e
    intakes: dict[str, intake_t]
    outputs: dict[str, type_t | None]
    requires_completion: bool

    proxy: _function_t
    actual: _function_t

    right_to_left: bool

    wants_unique_name: bool = d.field(init=False, default=False)
    # Of actual function, not proxy.
    module: module_t | None = NonInitField_NONE()
    RunFunction: h.Callable[..., h.Any] | None = NonInitField_NONE()
    documentation: str | None = NonInitField_NONE()

    def __post_init__(self) -> None:
        """"""
        self.wants_unique_name = (UNIQUE_NAME_INTAKE in self.intakes) and self.intakes[
            UNIQUE_NAME_INTAKE
        ].has_default

    @classmethod
    def NewForPath(cls, path: str | path_t, /) -> h.Self | None:
        """"""
        if isinstance(path, str):
            path = path_t(path)
        path = path.expanduser()

        with open(path) as accessor:
            proxy_function = FirstFunctionAsAstNode(accessor.read())
        if proxy_function is None:
            LOGGERS.active.error(f"No proper function found for node {path}")
            return None

        description = prsr.get_docstring(proxy_function)
        (
            name,
            actual_path,
            function_name,
            ii_names,
            output_names,
            right_to_left,
        ) = N_A_F_A(description, proxy_function.name)

        if actual_path is None:
            installation_type = installation_type_e.local
            actual_path = path
        elif actual_path.endswith(".py"):
            installation_type = installation_type_e.referenced
            actual_path = path_t(actual_path)
        else:
            installation_type = installation_type_e.system

        intakes, requires_completion = IntakesFromAST(
            proxy_function, ii_names, installation_type is installation_type_e.system
        )

        if (output_names is None) or (output_names.__len__() == 0):
            outputs = {}
        elif output_names == NO_OUTPUT_NAMES:
            outputs = {NO_OUTPUT_NAMES: None}
            requires_completion = True
        else:
            outputs = {_elm.strip(): None for _elm in output_names.split(",")}

        proxy = _function_t(path=path, name=proxy_function.name)
        if actual_path == path:
            actual = proxy
        else:
            actual = _function_t(path=actual_path, name=function_name)

        return cls(
            name=name,
            keywords="",
            short_description="",
            long_description="",
            installation_type=installation_type,
            intakes=intakes,
            outputs=outputs,
            requires_completion=requires_completion,
            proxy=proxy,
            actual=actual,
            right_to_left=right_to_left,
        )

    @property
    def n_intakes(self) -> int:
        """"""
        return self.intakes.__len__()

    @property
    def n_outputs(self) -> int:
        """"""
        return self.outputs.__len__()

    @property
    def output_names(self) -> tuple[str, ...]:
        """"""
        return tuple(self.outputs.keys())

    @property
    def function_name_for_script(self) -> str:
        """"""
        module = self.module.__name__.replace(".", "_")
        return f"{module}__{self.actual.name}"

    def Activate(self) -> None:
        """"""
        if self.module is not None:
            return

        if self.installation_type is installation_type_e.system:
            ModuleAndFunction = M_F_FromPyPathAndName
        else:  # installation_type_e.local or installation_type_e.referenced
            ModuleAndFunction = M_F_FromPathAndName
        self.module, self.RunFunction = ModuleAndFunction(
            self.actual.path, self.actual.name
        )
        self.documentation = spct.getdoc(self.RunFunction)

        if self.proxy is self.actual:
            Function = self.RunFunction
        else:
            # Always use the signature of the proxy function since it might have been
            # corrected.
            _, Function = M_F_FromPathAndName(self.proxy.path, self.proxy.name)
        signature = spct.signature(Function)

        # /!\
        # Importing annotations from __future__ changes the way type hints are
        # processed. In consequence, when inspecting a function, the same code cannot be
        # used depending on whether the defining module imported it or not.
        # In short... it's nonsense.
        try:
            annotations_ = spct.get_annotations(Function, eval_str=True)
        except NameError:
            annotations_ = spct.get_annotations(Function)
        intake_specs = signature.parameters
        for name, intake in self.intakes.items():
            if intake.UpdateFromSignature(intake_specs[name], annotations_[name]):
                self.requires_completion = True

        if self.outputs.__len__() > 0:
            if self._UpdateOutputsFromSignature(signature.return_annotation):
                self.requires_completion = True

    def _UpdateOutputsFromSignature(self, outputs: h.Any, /) -> bool:
        """
        Note: requires_completion could be set here; However, for coherence with
        UpdateFromSignature, it is returned instead.
        """
        if outputs == NO_ANNOTATION:
            outputs = h.Any
            requires_completion = True
        else:
            requires_completion = False
        hint = type_t.NewForHint(outputs)
        if (hint.type is tuple) and (
            (hint.elements.__len__() != 2)
            or (hint.elements[1].type is not EllipsisType)
        ):
            hints = hint.elements
        else:
            hints = (hint,)

        assert hints.__len__() == self.outputs.__len__(), (
            self.name,
            hints,
            self.outputs,
        )
        for name, hint in zip(self.outputs, hints):
            self.outputs[name] = hint

        return requires_completion

    def AsStr(
        self,
        /,
        *,
        bold: tuple[str, str] = ("<b>", "</b>"),
        italic: tuple[str, str] = ("<i>", "</i>"),
        space: str = "&nbsp;",
        newline: str = "<br/>",
    ) -> str:
        """"""
        output = [
            f"{bold[0]}{self.name}{bold[1]}",
            "",
            f"Keywords:{10*space}{self.keywords}",
            f"Short description: {self.keywords}",
            f"Long description:{2*space}{self.keywords}",
            "",
        ]

        if self.documentation is None:
            documentation = "No documentation available."
        else:
            documentation = filter(
                lambda _elm: not _elm.startswith("_"), self.documentation.splitlines()
            )
            documentation = newline.join(documentation)
        output.append(
            f"{bold[0]}DOCUMENTATION{bold[1]}{newline}{newline}{documentation}"
        )

        output.append(f"{newline}{bold[0]}Input(s):{bold[1]}")
        if self.intakes.__len__() > 0:
            max_name_length = max(
                map(
                    len,
                    (
                        _elm
                        for _elm in self.intakes.keys()
                        if _elm != UNIQUE_NAME_INTAKE
                    ),
                )
            )
            max_type_length = max(
                map(
                    len,
                    map(
                        str,
                        (
                            _elm.type
                            for _nme, _elm in self.intakes.items()
                            if _nme != UNIQUE_NAME_INTAKE
                        ),
                    ),
                )
            )
            for name, intake in self.intakes.items():
                if name != UNIQUE_NAME_INTAKE:
                    type_as_str = str(intake.type)
                    padding_name = (max_name_length - name.__len__() + 1) * space
                    padding_type = (max_type_length - type_as_str.__len__() + 1) * space
                    output.append(
                        f"{4*space}{name}:{padding_name}"
                        f"{italic[0]}{type_as_str}{italic[1]}{padding_type}= "
                        f"{intake.default_value}"
                    )
            if self.wants_unique_name:
                output.append(f"{4*space}{italic[0]}+ Unique name{italic[1]}")

        output.append(f"{bold[0]}Output(s):{bold[1]}")
        if self.outputs.__len__() > 0:
            max_name_length = max(map(len, self.outputs.keys()))
            for name, output_ in self.outputs.items():
                padding = (max_name_length - name.__len__() + 1) * space
                output.append(
                    f"{4*space}{name}:{padding}{italic[0]}{output_.type}{italic[1]}"
                )

        if self.requires_completion:
            output.append(f"{newline}{italic[0]}Requires completion{italic[1]}")

        output.append(f"{newline}Installation type: {self.installation_type.name}")
        if self.proxy is self.actual:
            proxy = "Actual"
        else:
            proxy = self.proxy
        for stripe, n_spaces, function in (
            ("Actual", 1, self.actual),
            ("Proxy", 2, proxy),
        ):
            if isinstance(function, _function_t):
                output.append(
                    f"{stripe}:{n_spaces * space}{function.name} @ {function.path}"
                )
            else:
                output.append(f"{stripe}:{n_spaces * space}{function}")

        return newline.join(output)

    def __str__(self) -> str:
        """"""
        return self.AsStr(
            bold=("", ""),
            italic=("", ""),
            space=" ",
            newline="\n",
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
