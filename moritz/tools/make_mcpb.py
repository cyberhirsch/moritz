# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Pack the Moritz MCP server as a Claude extension (.mcpb).

    python moritz/tools/make_mcpb.py [<out dir>]

The extension is `moritz/mcp` (Moritz's fork of Blender Lab's MCP server) with the add-on's
command list (`scripts/addons_core/moritz_mcp/commands.py`) copied in as `mzmcp/moritz_commands.py`,
so its tools are known before Moritz runs. Its version is Moritz's. Claude runs it with `uv`.
"""

import json
import os
import sys
import zipfile

from make_portable_zip import moritz_version

SOURCE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SERVER = os.path.join(SOURCE, "moritz", "mcp")
COMMANDS = os.path.join(SOURCE, "scripts", "addons_core", "moritz_mcp", "commands.py")
SKIP = {"__pycache__", ".venv", "requirements_dev.txt", ".mypy_cache", ".ruff_cache"}


def main():
    out_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
    ver = moritz_version()
    out = os.path.join(out_dir, "moritz-mcp-{}.mcpb".format(ver))
    with open(os.path.join(SERVER, "manifest.json"), encoding="utf-8") as f:
        manifest = json.load(f)
    # A version number only ("0.2.0 Beta" is 0.2.0).
    manifest["version"] = ver.split("-")[0]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for dirpath, dirnames, filenames in os.walk(SERVER):
            dirnames[:] = [d for d in dirnames if d not in SKIP]
            for name in filenames:
                if name in SKIP or name == "manifest.json":
                    continue
                path = os.path.join(dirpath, name)
                zf.write(path, os.path.relpath(path, SERVER).replace(os.sep, "/"))
        zf.write(COMMANDS, "mzmcp/moritz_commands.py")
        zf.writestr("manifest.json", json.dumps(manifest, indent=2) + "\n")
    print(out, round(os.path.getsize(out) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
