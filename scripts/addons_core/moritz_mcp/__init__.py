# SPDX-FileCopyrightText: 2026 Blender Authors
# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Moritz MCP: lets AI assistants (through the Moritz MCP server) and moritz-cli drive the running
Moritz.

A fork of Blender Lab's MCP add-on (projects.blender.org/lab/blender_mcp, GPL-3.0-or-later):
the same socket bridge, built into Moritz, plus Moritz's own command set (`commands.py`) that the
MCP server and moritz-cli share. The bridge runs any Python it receives, so it is off until it is
turned on in Preferences > System > Moritz MCP, and it only listens on this computer (127.0.0.1).
"""

__all__ = (
    "register",
    "unregister",
)

bl_info = {
    "name": "Moritz MCP",
    "author": "Moritz Authors, Blender Lab",
    "version": (1, 0, 0),
    "blender": (5, 3, 0),
    "location": "Preferences > System > Moritz MCP",
    "description": "Lets AI assistants and moritz-cli drive Moritz",
    "category": "System",
}

import bpy  # pylint: disable=import-error
from bpy.props import (
    BoolProperty,
    IntProperty,
)  # pylint: disable=import-error

from . import mcp_to_blender_server

# Only this computer: the bridge runs any Python it is sent.
HOST = "127.0.0.1"
# Next to Blender Lab's 9876, so Blender's MCP and Moritz's can run at the same time.
DEFAULT_PORT = 9877

_PORT_MIN = 1024
_PORT_MAX = 65535

# Seconds after start-up before the server starts, to stay out of Moritz's start-up.
_AUTOSTART_DELAY = 1.0

_TIMER_ACTIVE = 0.25
_TIMER_IDLE = 1.0
_TIMER_IDLE_DELAY = 5.0

# Store the CLI handle, only for correct register/unregister.
_cli_commands: list[object] = []


class _State:
    """Runtime state, not saved."""
    error: str = ""


def _prefs(context: bpy.types.Context | None = None) -> "MoritzMCPPreferences | None":
    addon = (context or bpy.context).preferences.addons.get(__package__)
    return addon.preferences if addon else None


def server_start(port: int) -> str:
    """Start the bridge on `port`; returns an error message, empty when it runs."""
    from . import execute_interactive

    if mcp_to_blender_server.is_running():
        return ""
    mcp_to_blender_server.timer_internal_vars_calc(
        active=_TIMER_ACTIVE, idle=_TIMER_IDLE, idle_delay=_TIMER_IDLE_DELAY)
    prefs = _prefs()
    mcp_to_blender_server.use_log = bool(prefs and prefs.use_log)
    try:
        mcp_to_blender_server.start(HOST, port)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        _State.error = str(ex)
        return _State.error
    _State.error = ""
    bpy.app.timers.register(
        execute_interactive.run,
        first_interval=mcp_to_blender_server.TIMER_INTERVAL_ACTIVE,
        persistent=True)
    return ""


def server_stop() -> None:
    from . import execute_interactive

    mcp_to_blender_server.stop()
    if bpy.app.timers.is_registered(execute_interactive.run):
        bpy.app.timers.unregister(execute_interactive.run)


def _update_server(self: "MoritzMCPPreferences", _context: bpy.types.Context) -> None:
    if bpy.app.background:
        return
    server_stop()
    if self.use_server:
        server_start(self.port)


def _update_use_log(self: "MoritzMCPPreferences", _context: bpy.types.Context) -> None:
    mcp_to_blender_server.use_log = self.use_log


class MoritzMCPPreferences(bpy.types.AddonPreferences):  # type: ignore[misc]
    bl_idname = __package__

    use_server: BoolProperty(  # type: ignore[valid-type]
        name="Allow AI Assistants and moritz-cli",
        description=(
            "Listen for the Moritz MCP server and moritz-cli on this computer (127.0.0.1).\n"
            "They can run any Python in Moritz, so turn this on only while you use them"
        ),
        default=False,
        update=_update_server,
    )
    port: IntProperty(  # type: ignore[valid-type]
        name="Port",
        description="The port the Moritz MCP server and moritz-cli --connect use (MORITZ_MCP_PORT)",
        default=DEFAULT_PORT,
        min=_PORT_MIN,
        max=_PORT_MAX,
        update=_update_server,
    )
    use_log: BoolProperty(  # type: ignore[valid-type]
        name="Log Requests",
        description="Print every request and response to the console",
        default=False,
        update=_update_use_log,
    )

    def draw(self, context: bpy.types.Context) -> None:
        draw_settings(self.layout, context)


def draw_settings(layout: bpy.types.UILayout, context: bpy.types.Context) -> None:
    prefs = _prefs(context)
    if prefs is None:
        return
    layout.use_property_split = True
    layout.use_property_decorate = False
    col = layout.column()
    col.prop(prefs, "use_server")
    sub = col.column()
    sub.prop(prefs, "port")
    sub.prop(prefs, "use_log")
    if mcp_to_blender_server.is_running():
        col.label(text="Listening on {:s}:{:d}".format(HOST, prefs.port), icon='CHECKMARK')
    elif _State.error:
        col.label(text=_State.error, icon='ERROR')


class USERPREF_PT_moritz_mcp(bpy.types.Panel):  # type: ignore[misc]
    bl_space_type = 'PREFERENCES'
    bl_region_type = 'WINDOW'
    bl_context = "system"
    bl_label = "Moritz MCP"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: bpy.types.Context) -> None:
        draw_settings(self.layout, context)


def _autostart_timer() -> None:
    prefs = _prefs()
    if prefs is not None and prefs.use_server:
        server_start(prefs.port)


def _cli_execute_handler(argv: list[str]) -> int:
    """`moritz -b file.blend -c moritz_mcp [--port N]`: serve in a background Moritz."""
    from .cli import cli_execute
    return cli_execute(argv)


_classes = (
    MoritzMCPPreferences,
    USERPREF_PT_moritz_mcp,
)


def register() -> None:
    for cls in _classes:
        bpy.utils.register_class(cls)
    _cli_commands.append(bpy.utils.register_cli_command("moritz_mcp", _cli_execute_handler))
    if not bpy.app.background:
        bpy.app.timers.register(_autostart_timer, first_interval=_AUTOSTART_DELAY, persistent=True)


def unregister() -> None:
    for cmd in _cli_commands:
        bpy.utils.unregister_cli_command(cmd)
    _cli_commands.clear()
    if bpy.app.timers.is_registered(_autostart_timer):
        bpy.app.timers.unregister(_autostart_timer)
    server_stop()
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
