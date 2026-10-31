# Run: moritz.exe --factory-startup --python moritz/tests/test_moritz_mcp_live.py
# (with the interface: the bridge only serves the running Moritz)
# Moritz MCP live: turning on Preferences > System > Moritz MCP starts the bridge on 127.0.0.1;
# `moritz-cli --connect` runs a command in the running Moritz; one undo takes it back; turning the
# setting off stops the bridge.
import json
import os
import socket
import subprocess
import sys

import bpy

failures = []


def say(*a): print("MXML", " ".join(str(x) for x in a), flush=True)


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)
    if not ok:
        failures.append(name)


def win(): return bpy.context.window_manager.windows[0]


def cli(*args):
    """moritz-cli.exe next to moritz.exe, or the script with Moritz's Python before it is built."""
    folder = os.path.dirname(bpy.app.binary_path)
    exe = os.path.join(folder, "moritz-cli.exe")
    if os.path.isfile(exe):
        return [exe, *args]
    version = "{:d}.{:d}".format(*bpy.app.version[:2])
    return [os.path.join(folder, version, "python", "bin", "python.exe"), "-I",
            os.path.join(folder, version, "scripts", "modules", "moritz_cli.py"), *args]


P = {}


def listening(port):
    with socket.socket() as sock:
        sock.settimeout(1.0)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def s_on():
    from moritz_mcp import mcp_to_blender_server
    P['prefs'] = bpy.context.preferences.addons["moritz_mcp"].preferences
    check("off at the start", not mcp_to_blender_server.is_running())
    # Its own port, away from any other Moritz serving on the default one.
    P['prefs'].port = 9879
    P['prefs'].use_server = True
    check("the setting starts the bridge", mcp_to_blender_server.is_running() and listening(P['prefs'].port))
    P['before'] = set(bpy.data.objects.keys())
    with bpy.context.temp_override(window=win()):
        bpy.ops.ed.undo_push(message="Before the CLI")
    P['proc'] = subprocess.Popen(cli("--connect", "--port", "9879", "--json", "command", "run", "create", "type=Box",
                                     "parameters={\"Height\": 2}"),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    say("cli", P['proc'].args[0])


def s_wait():
    # The bridge answers from Moritz's main loop: keep returning to it until the CLI is done.
    if P['proc'].poll() is None:
        return 'WAIT'
    out, err = P['proc'].communicate()
    try:
        P['result'] = json.loads(out)
    except json.JSONDecodeError:
        P['result'] = {}
        say("cli output", out, err)
    return None


def s_check():
    result = P['result']
    new = set(bpy.data.objects.keys()) - P['before']
    check("moritz-cli --connect created a Box in the running Moritz", P['proc'].returncode == 0 and
          len(new) == 1 and result.get("object", {}).get("parameters", {}).get("Height") == 2.0, sorted(new), result)
    with bpy.context.temp_override(window=win()):
        bpy.ops.ed.undo()
    check("one undo takes it back", set(bpy.data.objects.keys()) == P['before'],
          sorted(set(bpy.data.objects.keys()) - P['before']))


def s_off():
    from moritz_mcp import mcp_to_blender_server
    P['prefs'] = bpy.context.preferences.addons["moritz_mcp"].preferences
    P['prefs'].use_server = False
    check("turning it off stops the bridge", not mcp_to_blender_server.is_running() and not listening(P['prefs'].port))
    say("FAILURES", len(failures), failures)
    bpy.ops.wm.quit_blender()


steps = [s_on, s_wait, s_check, s_off]


def run():
    try:
        if steps[0]() != 'WAIT':
            steps.pop(0)
    except Exception as ex:
        import traceback
        traceback.print_exc()
        say("ERR", repr(ex))
        steps.pop(0)
    return 0.3 if steps else None


bpy.app.timers.register(run, first_interval=2.0)
sys.stdout.flush()
