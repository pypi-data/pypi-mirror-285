"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2017
SEE COPYRIGHT NOTICE BELOW
"""

import typing as h
from datetime import datetime as date_time_t
from pathlib import Path as path_t

from pyvispr.config.path import CATALOG_FOLDER
from pyvispr.constant.catalog import (
    ACTUAL_SOURCE,
    FUNCTION_NAME,
    II_NAMES,
    NODE_NAME,
    OUTPUT_NAMES,
)
from pyvispr.extension.introspection.function import function_t
from pyvispr.flow.descriptive.node import installation_type_e


def FunctionSource(
    imports: str | None,
    header: str,
    /,
    *,
    node_name: str | None = None,
    actual_source: path_t | str | None = None,
    module_pypath: str | None = None,
    function_name_for_node_name: str | None = None,
    function_name: str | None = None,
    ii_names: str | None = None,
    output_names: str | None = None,
    documentation: str | None = None,
    body: str | None = None,
) -> str:
    """"""
    output = []

    if imports is not None:
        output.append(f"{imports}\n")
    output.append(f'{header}\n    """')

    if node_name is not None:
        output.append(f"    {NODE_NAME}: {node_name}")
    elif not ((module_pypath is None) or (function_name_for_node_name is None)):
        module_name = "".join(map(str.title, module_pypath.split(".")))
        output.append(
            f"    {NODE_NAME}: {module_name}{function_name_for_node_name.title()}"
        )

    if actual_source is not None:
        output.append(f"    {ACTUAL_SOURCE}: {actual_source}")

    if function_name is not None:
        output.append(f"    {FUNCTION_NAME}: {function_name}")

    if (ii_names is not None) and (ii_names.__len__() > 0):
        output.append(f"    {II_NAMES}: {ii_names}")

    if (output_names is not None) and (output_names.__len__() > 0):
        output.append(f"    {OUTPUT_NAMES}: {output_names}")

    if documentation is not None:
        output.extend(("", documentation))

    output.append('    """')

    if body is not None:
        if body[-1] == "\n":
            body = body[:-1]
        output.append(body)

    output.append("")

    return "\n".join(output)


def UpdateFunction(
    node_name: str,
    proxy_function: function_t,
    actual_function: function_t,
    header: str,
    ii_names: str | None,
    output_names: str | None,
    mode: installation_type_e,
    /,
) -> None:
    """"""
    if node_name == proxy_function.name:
        node_name = None
    if actual_function.name == proxy_function.name:
        actual_function_name = None
    else:
        actual_function_name = actual_function.name

    if mode is installation_type_e.system:
        updated = FunctionSource(
            None,
            header,
            actual_source=actual_function.pypath,
            module_pypath=actual_function.pypath,
            function_name_for_node_name=actual_function.name,
            function_name=actual_function_name,
            ii_names=ii_names,
            output_names=output_names,
        )
    elif mode is installation_type_e.referenced:
        updated = FunctionSource(
            None,
            header,
            node_name=node_name,
            actual_source=actual_function.path,
            function_name=actual_function_name,
            ii_names=ii_names,
            output_names=output_names,
        )
    else:
        updated = FunctionSource(
            None,
            header,
            node_name=node_name,
            ii_names=ii_names,
            output_names=output_names,
        )
    source = proxy_function.ModuleWithNewHeader(updated)

    with open(proxy_function.path, "w") as accessor:
        accessor.write(source)


def PathForUser(stem: str, /) -> path_t:
    """"""
    now = date_time_t.now().isoformat(sep=":", timespec="microseconds")
    now = "".join(filter(str.isdigit, now))

    return CATALOG_FOLDER / f"{stem}_{now}.py"


def PathForSystem(pypath: str, function_name: str, /) -> path_t:
    """"""
    module_path = path_t(*pypath.split("."))
    return CATALOG_FOLDER / module_path / f"{function_name}.py"


def ExistingUserPaths(stem: str, /) -> tuple[path_t, ...]:
    """"""
    return tuple(CATALOG_FOLDER.glob(f"{stem}_[0-9][0-9]*.py"))


def InstallLocalFunction(
    function: function_t,
    header: str,
    ii_names: str | None,
    output_names: str | None,
    /,
) -> None:
    """"""
    if function.imports is None:
        imports = None
    else:
        imports = "\n".join(function.imports)
    header = FunctionSource(
        imports,
        header,
        ii_names=ii_names,
        output_names=output_names,
        documentation=function.documentation,
    )
    source = function.ModuleWithNewHeader(header)

    where = PathForUser(function.name)
    with open(where) as accessor:
        accessor.write(source)


def InstallReferencedFunction(
    function: function_t,
    header: str,
    ii_names: str | None,
    output_names: str | None,
    /,
) -> None:
    """"""
    if function.imports is None:
        imports = None
    else:
        imports = "\n".join(function.imports)
    source = FunctionSource(
        imports,
        header,
        actual_source=function.path,
        ii_names=ii_names,
        output_names=output_names,
        body="    pass",
    )

    where = PathForUser(function.name)
    with open(where) as accessor:
        accessor.write(source)


def InstallSystemFunction(
    module_pypath: str,
    function_name: str,
    imports: h.Sequence[str] | None,
    header: str,
    ii_names: str | None,
    output_names: str | None,
    /,
) -> None:
    """"""
    if imports is not None:
        imports = "\n".join(imports)
    source = FunctionSource(
        imports,
        header,
        actual_source=module_pypath,
        module_pypath=module_pypath,
        function_name_for_node_name=function_name,
        function_name=function_name,
        ii_names=ii_names,
        output_names=output_names,
        body="    pass",
    )

    where = PathForSystem(module_pypath, function_name)
    where.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with open(where, "w") as accessor:
        accessor.write(source)


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
