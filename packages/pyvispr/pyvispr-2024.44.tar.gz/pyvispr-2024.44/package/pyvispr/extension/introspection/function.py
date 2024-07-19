"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import ast as prsr
import dataclasses as d
import inspect as spct
import itertools as ittl
import types as t
import typing as h
from pathlib import Path as path_t

from logger_36.instance.loggers import LOGGERS
from logger_36.logger import LogException
from pyvispr.constant.flow.node import NO_ANNOTATION, NO_INTAKE_NAME, NO_OUTPUT_NAMES
from pyvispr.extension.introspection.module import (
    M_F_FromPathAndName,
    M_F_FromPyPathAndName,
)

signature_t = spct.Signature
parameter_t = spct.Parameter

parameter_h = tuple[str, str]
parameter_w_default_h = tuple[str, str, h.Any]
parameters_h = list[parameter_h | parameter_w_default_h]
returns_h = list[parameter_h]
documentation_h = tuple[str, str, parameters_h, returns_h]


@d.dataclass(slots=True, repr=False, eq=False)
class function_t:
    module: t.ModuleType
    path: path_t | None
    pypath: str
    #
    instance: t.FunctionType
    name: str
    imports: tuple[str, ...] | None  # Limited to what annotations need.
    header_line: int
    header_intakes: dict[str, str | tuple[str, str | None]]
    header_outputs: dict[str, str] | None
    documentation: str | None
    body_line: int
    body_end_line: int

    @classmethod
    def Dummy(
        cls,
        instance: t.FunctionType,
        expected_name: str,
        module: t.ModuleType,
        path: str | None,
        pypath: str,
        /,
    ) -> h.Self:
        """"""
        header_intakes = {f"{NO_INTAKE_NAME}_0": f'"{NO_ANNOTATION}"'}
        header_outputs = {NO_OUTPUT_NAMES: f'"{NO_ANNOTATION}"'}

        return cls(
            module=module,
            path=path,
            pypath=pypath,
            instance=instance,
            name=expected_name,
            imports=None,
            header_line=-1,
            header_intakes=header_intakes,
            header_outputs=header_outputs,
            documentation=None,
            body_line=-1,
            body_end_line=-1,
        )

    @classmethod
    def NewFromInstance(
        cls, instance: t.FunctionType, expected_name: str, module: t.ModuleType, /
    ) -> h.Self:
        """"""
        path = getattr(module, "__file__", None)
        pypath = module.__name__

        try:
            source = spct.getsource(instance)
        except (OSError, TypeError):  # See documentation.
            as_str = getattr(instance, "__name__", str(instance))
            LOGGERS.active.error(
                f"Cannot read source of {pypath}.{as_str}; Returning dummy function"
            )
            return cls.Dummy(instance, expected_name, module, path, pypath)

        imports = []
        header_intakes: dict[str, str | tuple[str, str]] = {}

        function_node = FirstFunctionAsAstNode(source)
        if function_node is None:
            LOGGERS.active.error(
                f"Function {pypath}.{instance.__name__} cannot be read; "
                f"Returning dummy function"
            )
            return cls.Dummy(instance, expected_name, module, path, pypath)

        ast_intakes = function_node.args
        positionals, keywords, keywords_defaults = _PositionalsKeywordsAndDefaults(
            ast_intakes
        )
        _AddPositionalsOrKeywords(positionals, None, source, imports, header_intakes)
        _AddVarArgs(ast_intakes, header_intakes)
        _AddPositionalsOrKeywords(
            keywords, keywords_defaults, source, imports, header_intakes
        )
        _AddKwargs(ast_intakes, header_intakes)

        if function_node.returns is None:
            header_outputs = {NO_OUTPUT_NAMES: f'"{NO_ANNOTATION}"'}
        else:
            annotation = prsr.get_source_segment(source, function_node.returns)
            if annotation == "None":
                header_outputs = None
            else:
                header_outputs = {NO_OUTPUT_NAMES: annotation}

        source_first = prsr.get_source_segment(source, function_node.body[0])
        if source_first[0].strip() == '"':
            body_line = function_node.body[1].lineno
        else:
            body_line = function_node.body[0].lineno
        source_last = prsr.get_source_segment(source, function_node.body[-1])
        body_end_line = (
            function_node.body[-1].lineno + source_last.splitlines().__len__() - 1
        )

        return cls(
            module=module,
            path=path,
            pypath=pypath,
            instance=instance,
            name=expected_name,
            imports=tuple(imports),
            header_line=function_node.lineno,
            header_intakes=header_intakes,
            header_outputs=header_outputs,
            documentation=spct.getdoc(instance),
            body_line=body_line,
            body_end_line=body_end_line,
        )

    @classmethod
    def NewFromPath(cls, path: path_t | str, /, *, name: str = None) -> h.Self | None:
        """
        name: If None, then select first function in module.
        """
        if name is None:
            assert isinstance(path, path_t)
            with open(path) as accessor:
                function = FirstFunctionAsAstNode(accessor.read())
            if function is None:
                LOGGERS.active.error(f"No proper function found in {path}")
                return None
            name = function.name

        if isinstance(path, path_t):
            ModuleAndFunction = M_F_FromPathAndName
        else:
            ModuleAndFunction = M_F_FromPyPathAndName
        module, function = ModuleAndFunction(path, name)

        return function_t.NewFromInstance(function, name, module)

    @property
    def has_outputs(self) -> bool:
        """"""
        return self.header_outputs is not None

    @property
    def output_names(self) -> str | None:
        """"""
        if self.has_outputs:
            # This is equivalent to ", ".join(self.header_outputs)
            return NO_OUTPUT_NAMES

        return None

    @property
    def header(self) -> str:
        """
        If the function name was set to the actual function name, then the following
        update might be necessary:
        import re as regx
        if "__call__" in header:
            header = regx.sub(r"\b__call__\b", expected_name, header, count=1)
        This is currently not needed because NewFromInstance uses expected_name instead.
        """
        intakes = []
        positional_s = tuple(
            (_key, _vle)
            for _key, _vle in self.header_intakes.items()
            if isinstance(_vle, str)
        )
        for name, value in positional_s:
            intakes.append(f"{name}: {value}")
        if positional_s.__len__() > 0:
            intakes.append("/")
        # Could be done more efficiently with set difference, but order would be lost.
        keywords = tuple(
            (_key, _vle)
            for _key, _vle in self.header_intakes.items()
            if isinstance(_vle, tuple)
        )
        if keywords.__len__() > 0:
            intakes.append("*")
            for name, value in keywords:
                intakes.append(f"{name}: {value[0]} = {value[1]}")

        output = f"def {self.name}(" + ", ".join(intakes) + ")"

        if self.has_outputs:
            output += f" -> {self.header_outputs[NO_OUTPUT_NAMES]}:"
        else:
            output += " -> None:"

        return output

    def ModuleWithNewHeader(self, new_header: str, /) -> str:
        """
        new_header can include documentation.
        """
        if new_header[-1] == "\n":
            new_header = new_header[:-1]

        source_lines = spct.getsource(self.module).splitlines()

        prologue = source_lines[: (self.header_line - 1)]
        if self.imports is not None:
            for import_ in self.imports:
                if import_ not in prologue:
                    prologue.append(import_)
        epilogue = source_lines[(self.body_line - 1) :]

        return "\n".join(prologue + [new_header] + epilogue + [""])


def FirstFunctionAsAstNode(source: str, /) -> prsr.FunctionDef | None:
    """"""
    output = None

    try:
        tree = prsr.parse(source)
    except Exception as exception:
        LogException(exception, logger=LOGGERS.active)
        return None

    for node in prsr.walk(tree):
        if isinstance(node, prsr.FunctionDef) and (node.name[0] != "_"):
            output = node
            break

    return output


def _PositionalsKeywordsAndDefaults(
    ast_intakes: prsr.arguments, /
) -> tuple[list[prsr.arg], list[prsr.arg], h.Sequence[h.Any]]:
    """"""
    if (n_defaults := ast_intakes.defaults.__len__()) > 0:
        n_wo_defaults = ast_intakes.args.__len__() - n_defaults
        positionals = ast_intakes.posonlyargs + ast_intakes.args[:n_wo_defaults]
        keywords = ast_intakes.args[n_wo_defaults:]
    else:
        positionals = ast_intakes.posonlyargs + ast_intakes.args
        keywords = []
    keywords += ast_intakes.kwonlyargs
    keywords_defaults = ast_intakes.defaults + ast_intakes.kw_defaults

    return positionals, keywords, keywords_defaults


def _AddPositionalsOrKeywords(
    ast_intakes: h.Sequence[prsr.arg],
    defaults: h.Sequence[h.Any] | None,
    source: str,
    imports: list[str],
    intakes: dict[str, str | tuple[str, str]],
    /,
) -> None:
    """"""
    has_defaults = defaults is not None
    if not has_defaults:
        defaults = ()

    default_source = "NO DEFAULT"
    valid_default = False
    for ast_intake, default in ittl.zip_longest(ast_intakes, defaults, fillvalue=None):
        name = ast_intake.arg
        if has_defaults:
            default_source = prsr.get_source_segment(source, default)
            # /!\ If the default value cannot be evaluated, e.g. numpy._NoValue whose
            # import seems complicated (see Numpy source code), it is ignored, turning
            # the argument into positional.
            try:
                _ = eval(default_source)
                valid_default = True
            except:
                valid_default = False

        if ast_intake.annotation is None:
            annotation = f'"{NO_ANNOTATION}"'
        else:
            annotation = prsr.get_source_segment(source, ast_intake.annotation)
            if "." in annotation:
                imports.append(f"import {annotation[:annotation.rfind('.')]}")

        if has_defaults and valid_default:
            annotation = (annotation, default_source)
        intakes[name] = annotation


def _AddVarArgs(ast_intakes: prsr.arguments, intakes: dict[str, str], /) -> None:
    """"""
    if ast_intakes.vararg is not None:
        name = f"{NO_INTAKE_NAME}_args"
        intakes[name] = f'"{NO_ANNOTATION}"'


def _AddKwargs(
    ast_intakes: prsr.arguments, intakes: dict[str, tuple[str, str | None]], /
) -> None:
    """"""
    if ast_intakes.kwarg is not None:
        name = f"{NO_INTAKE_NAME}_kwargs"
        intakes[name] = (f'"{NO_ANNOTATION}"', None)


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
