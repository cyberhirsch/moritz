# SPDX-FileCopyrightText: 2026 Blender Authors
# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
CLI command handler for running the MCP server in background mode.

Started via ``moritz --background file.blend --command moritz_mcp``.
"""

__all__ = (
    "cli_execute",
)

import argparse

from . import execute_blocking
from . import mcp_to_blender_server


def cli_execute(argv: list[str]) -> int:
    """
    Block and serve MCP requests until interrupted.
    """
    from . import DEFAULT_PORT, HOST

    parser = argparse.ArgumentParser(
        prog="moritz_mcp",
        description=(
            "Serve Moritz MCP requests on {:s} from this background Moritz. "
            "Deferred responses are not supported in background mode; "
            "each request must complete before returning.".format(HOST)
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Port to listen on.",
    )
    args = parser.parse_args(argv)

    try:
        mcp_to_blender_server.start(HOST, args.port)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        print("Error: {:s}".format(str(ex)))
        return 1

    print("Moritz MCP listening on {:s}:{:d}, press Ctrl+C to exit.".format(HOST, args.port))

    try:
        execute_blocking.run()
    finally:
        mcp_to_blender_server.stop()
    return 0
