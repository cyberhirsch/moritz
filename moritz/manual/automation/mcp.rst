##########
Moritz MCP
##########

Moritz MCP lets an AI assistant (Claude or any MCP client) work in the running Moritz: create
objects with Max parameters, use the modifier stack and Edit Poly tools, Align and Array, the
Outliner, selection sets, Hold / Fetch, settings and screenshots. Every change is one undo step.

Setup
=====

1. In Moritz: **Preferences > System > Moritz MCP**, turn on **Allow AI Assistants and
   moritz-cli**. Moritz then listens on this computer only (127.0.0.1, port 9877).
2. In Claude Desktop: **Settings > Extensions**, install ``moritz-mcp-<version>.mcpb`` from the
   release. It needs `uv <https://docs.astral.sh/uv/>`__.

Other MCP clients run ``uv run moritz-mcp`` (stdio) in the ``moritz/mcp`` folder of the source.

.. warning:: The assistant can run any Python in Moritz. Leave the setting off when you don't use
   it.

Moritz MCP is a fork of Blender Lab's Blender MCP (GPL-3.0-or-later).
