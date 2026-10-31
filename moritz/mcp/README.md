# Moritz MCP

Lets an AI assistant (Claude or any MCP client) work in the running Moritz the way a 3ds Max
user does:

- **Create** objects from the Create tab with their Max parameters (Box, Teapot, Suzanne,
  TorusKnot, ChamferBox, Circle, Star ...). They stay editable primitives until collapsed.
- **Modify:** the modifier stack top first, adding by Max or Blender name (Bend, TurboSmooth,
  Shell, Edit Poly ...), changing and removing modifiers, Collapse / Collapse To.
- **Edit Poly:** sub-object levels 1–5, selecting by index, and the tools (Smart Extrude,
  Extrude, Chamfer, Weld, Bridge, Cap, Connect, Inset ...).
- **Utilities:** Transform Type-In, Align, Array, Spacing Tool.
- **Scene Explorer:** layers, hide, freeze, selection sets, Hold / Fetch.
- **Settings:** keymap and name scheme; screenshots; open, save, import, export, render.

Every change is one undo step, so Ctrl+Z takes back what the assistant did. Python (`bpy`) and the
Blender API and manual are there for everything else.

## Setup

1. In Moritz: **Preferences > System > Moritz MCP**, turn on **Allow AI Assistants and
   moritz-cli**. Moritz then listens on this computer only (127.0.0.1, port 9877). The
   assistant can run any Python in Moritz, so leave it off when you don't use it.
2. In Claude Desktop: **Settings > Extensions**, install `moritz-mcp-<version>.mcpb` from the
   release. It needs [uv](https://docs.astral.sh/uv/) on the PATH.

Other MCP clients: run `uv run moritz-mcp` in this folder (stdio), or
`uv run moritz-mcp --transport http --port 8000`. `MORITZ_MCP_PORT` sets the port,
`MORITZ_PATH` the moritz.exe used by the tools that start a background Moritz.

## moritz-cli

The same commands from a terminal, with `moritz-cli.exe` next to `moritz.exe`:

```
moritz-cli info scene.blend
moritz-cli convert scene.blend scene.glb
moritz-cli render scene.blend -o frame_####.png --frames 1-24
moritz-cli command run create type=Teapot parameters={"Radius":2} --connect
moritz-cli command list
```

Without `--connect` each command runs in a background Moritz; with it, in the running one.
`--json` prints JSON.

## Origin and license

A fork of Blender Lab's [Blender MCP](https://projects.blender.org/lab/blender_mcp) (commit
dbbf836, 2026-09-29), GPL-3.0-or-later; see `LICENSE`. The add-on half lives in Moritz itself
(`scripts/addons_core/moritz_mcp`), with Moritz's command set in its `commands.py`. The bundled
documentation in `mzmcp/data` is Blender's (API reference and manual).
