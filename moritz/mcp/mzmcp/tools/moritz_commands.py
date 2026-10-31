# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Moritz's own tools: one per command of the Moritz MCP add-on's command set (Create, the modifier
stack, Edit Poly, Utilities, Scene Explorer, settings ...), plus `command_list` / `command_run`,
the same set moritz-cli runs.

The command list comes from the add-on's `commands.py`, read without Moritz running: the
extension carries a copy (`mzmcp/moritz_commands.py`); in the source tree it is read from the
add-on itself.
"""

__all__ = (
    "register",
)

import importlib.util
import os
from types import ModuleType
from typing import Annotated, Any

from mzmcp.tools_helpers.connection import send_code
from mcp.server.fastmcp import FastMCP  # pylint: disable=import-error,no-name-in-module
from mcp.types import ToolAnnotations  # pylint: disable=import-error,no-name-in-module
from pydantic import Field  # pylint: disable=import-error

_PACKAGE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CANDIDATES = (
    os.path.join(_PACKAGE, "moritz_commands.py"),
    # The source tree: moritz/mcp/mzmcp -> scripts/addons_core/moritz_mcp.
    os.path.join(_PACKAGE, "..", "..", "..", "scripts", "addons_core", "moritz_mcp", "commands.py"),
)

_TYPES = {"string": "str", "integer": "int", "number": "float", "boolean": "bool", "array": "list",
          "object": "dict"}


def _load_commands() -> ModuleType:
    for path in _CANDIDATES:
        if os.path.isfile(path):
            spec = importlib.util.spec_from_file_location("moritz_commands", path)
            assert spec is not None and spec.loader is not None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise FileNotFoundError("Moritz's command list (moritz_commands.py) is missing")


def run_in_moritz(name: str, params: dict[str, Any]) -> dict[str, Any]:
    """Run a command in the running Moritz and return its result."""
    code = "from moritz_mcp import commands\nresult = commands.run({!r}, {!r})\n".format(name, params)
    response = send_code(code, strict_json=True)
    if response.get("status") != "ok":
        return response
    result = response.get("result")
    return result if isinstance(result, dict) else {"status": "error", "message": "No result from Moritz"}


def _make_tool(name: str, params: tuple[tuple[str, str, Any, str], ...], required: object) -> Any:
    """A function whose signature FastMCP turns into the tool's schema."""
    args = []
    for pname, ptype, default, _pdesc in params:
        annotation = "Annotated[{:s}, Field(description=_desc[{!r}])]".format(_TYPES[ptype], pname)
        if default is required:
            args.append("{:s}: {:s}".format(pname, annotation))
        else:
            args.append("{:s}: {:s} = _defaults[{!r}]".format(pname, annotation, pname))
    # Required parameters first, as Python wants.
    args.sort(key=lambda a: " = " in a)
    source = "def tool({:s}) -> dict:\n    return _run({!r}, {{{:s}}})\n".format(
        ", ".join(args), name, ", ".join("{!r}: {:s}".format(p[0], p[0]) for p in params))
    namespace: dict[str, Any] = {
        "Annotated": Annotated, "Field": Field, "_run": run_in_moritz,
        "_desc": {p[0]: p[3] for p in params},
        "_defaults": {p[0]: p[2] for p in params if p[2] is not required},
    }
    exec(source, namespace)  # pylint: disable=exec-used
    return namespace["tool"]


def register(mcp: FastMCP) -> None:
    commands = _load_commands()
    for name, cmd in commands.COMMANDS.items():
        fn = _make_tool(name, cmd["params"], commands.REQUIRED)
        mcp.add_tool(
            fn,
            name=name,
            title=cmd["label"],
            description=cmd["description"],
            annotations=ToolAnnotations(
                title=cmd["label"],
                readOnlyHint=cmd["read_only"],
                destructiveHint=not cmd["read_only"],
            ),
        )

    @mcp.tool(annotations=ToolAnnotations(title="Command List", readOnlyHint=True))
    def command_list() -> dict[str, object]:
        """
        Every Moritz command with its parameters (JSON schema). Each one is also a tool of its
        own; moritz-cli runs the same commands (`moritz-cli command run <name>`).
        """
        return {"status": "ok", "commands": commands.describe()}

    @mcp.tool(annotations=ToolAnnotations(title="Command Run", destructiveHint=True))
    def command_run(name: str, params: dict[str, object] | None = None) -> dict[str, object]:
        """
        Run a Moritz command by name with a dict of parameters (see command_list).
        """
        return run_in_moritz(name, dict(params or {}))
