# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""moritz-cli: Moritz from the command line, for scripts, build pipelines and AI agents.

`moritz-cli.exe` (next to moritz.exe) runs this file with Moritz's own Python. It has two modes:

- Headless (the default): each command starts a background Moritz (`moritz.exe -b`), runs, and
  quits: info, render, convert, run, test, command.
- Live (`--connect`): the same commands in the running Moritz, through the Moritz MCP add-on's
  socket (Preferences > System > Moritz MCP), so you see what they do and can undo it.

`command list` / `command run` give the whole command set the Moritz MCP server has (Create,
the modifier stack, Edit Poly, Utilities, Scene Explorer ...). `--json` prints JSON for scripts.

This file does not import bpy: it runs outside Moritz.
"""

import argparse
import json
import os
import socket
import subprocess
import sys

DEFAULT_PORT = 9877
_MARK = "__MORITZ_CLI__"
_TIMEOUT = 3600.0

# The failure markers of Moritz's test scripts (see moritz/tests).
_TEST_FAILED = ("FAILURES 1", "FAILURES 2", "FAILURES 3", "FAILURES 4", "FAILURES 5", "FAILURES 6",
                "FAILURES 7", "FAILURES 8", "FAILURES 9", "Traceback", "EXCEPTION_ACCESS_VIOLATION")


class CLIError(Exception):
    pass


def moritz_exe():
    """moritz.exe: MORITZ_PATH, else the one this file ships with (<moritz>/<version>/scripts/modules)."""
    path = os.environ.get("MORITZ_PATH")
    if path:
        return path
    here = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    exe = os.path.join(folder, "moritz.exe" if os.name == "nt" else "moritz")
    if not os.path.isfile(exe):
        raise CLIError("moritz.exe not found next to moritz-cli; set MORITZ_PATH")
    return exe


# ------------------------------------------------------------------------------
# Running code in Moritz

def _command_code(name, params):
    return "from moritz_mcp import commands\nresult = commands.run({!r}, {!r})\n".format(name, params)


def run_live(code, port):
    """Run `code` in the running Moritz; returns its `result` dict."""
    request = json.dumps({"type": "execute", "code": code, "strict_json": False}) + "\0"
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=_TIMEOUT) as sock:
            sock.sendall(request.encode("utf-8"))
            buf = bytearray()
            while b"\0" not in buf:
                chunk = sock.recv(65536)
                if not chunk:
                    break
                buf.extend(chunk)
    except ConnectionRefusedError:
        raise CLIError("No Moritz is listening on port {:d}. Start Moritz and turn on Preferences > System > "
                       "Moritz MCP > Allow AI Assistants and moritz-cli".format(port)) from None
    except OSError as ex:
        raise CLIError("Can't reach Moritz on port {:d}: {:s}".format(port, str(ex))) from None
    response = json.loads(bytes(buf).partition(b"\0")[0].decode("utf-8"))
    if response.get("stdout"):
        sys.stderr.write(response["stdout"])
    if response.get("status") != "ok":
        raise CLIError(response.get("message", "Moritz reported an error"))
    return response.get("result", {})


def run_headless(code, blend_file="", factory=False, empty=False, timeout=_TIMEOUT):
    """Run `code` in a background Moritz (opening `blend_file`); returns its `result` dict."""
    wrapper = (
        "import json, sys, traceback\n"
        "try:\n"
        "    if {empty!r}:\n"
        "        import bpy\n"
        "        bpy.ops.wm.read_homefile(use_empty=True)\n"
        "    _ns = {{'result': {{}}}}\n"
        "    exec({code!r}, _ns)\n"
        "    _out = {{'status': 'ok', 'result': _ns['result']}}\n"
        "except Exception:\n"
        "    _out = {{'status': 'error', 'message': traceback.format_exc()}}\n"
        "print({mark!r} + json.dumps(_out, default=repr), flush=True)\n"
    ).format(empty=empty, code=code, mark=_MARK)
    args = [moritz_exe(), "-b"]
    if factory:
        args.append("--factory-startup")
    if blend_file:
        args.append(blend_file)
    args += ["--python-exit-code", "1", "--python-expr", wrapper]
    try:
        proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout, stdin=subprocess.DEVNULL, check=False)
    except subprocess.TimeoutExpired:
        raise CLIError("Moritz timed out after {:.0f} s".format(timeout)) from None
    for line in proc.stdout.splitlines():
        if line.startswith(_MARK):
            response = json.loads(line[len(_MARK):])
            if response["status"] != "ok":
                raise CLIError(response["message"])
            return response["result"]
    raise CLIError("Moritz ended without a result (exit code {:d}):\n{:s}".format(
        proc.returncode, (proc.stdout + proc.stderr)[-3000:]))


class Session:
    """Where commands run: the running Moritz (live) or a background one per call (headless)."""

    def __init__(self, args):
        self.live = args.connect
        self.port = args.port
        self.factory = args.factory_startup

    def run(self, code, blend_file="", empty=False):
        if self.live:
            if blend_file:
                self.command("open", {"path": os.path.abspath(blend_file)})
            return run_live(code, self.port)
        return run_headless(code, os.path.abspath(blend_file) if blend_file else "", self.factory, empty)

    def command(self, name, params, blend_file="", empty=False):
        result = self.run(_command_code(name, params), blend_file, empty)
        if isinstance(result, dict) and result.get("status") == "error":
            raise CLIError(result.get("message", "{:s} failed".format(name)))
        if isinstance(result, dict):
            result.pop("status", None)
        return result


# ------------------------------------------------------------------------------
# Output

def _print_human(value, indent=0):
    pad = "  " * indent
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (dict, list)) and item:
                print("{:s}{:s}:".format(pad, str(key)))
                _print_human(item, indent + 1)
            else:
                print("{:s}{:s}: {:s}".format(pad, str(key), json.dumps(item) if not isinstance(item, str) else item))
    elif isinstance(value, list):
        if all(not isinstance(v, (dict, list)) for v in value):
            print(pad + ", ".join(str(v) for v in value))
            return
        for item in value:
            if isinstance(item, dict) and "name" in item:
                print("{:s}- {:s}".format(pad, str(item["name"])))
                _print_human({k: v for k, v in item.items() if k != "name"}, indent + 1)
            else:
                print(pad + "-")
                _print_human(item, indent + 1)
    else:
        print(pad + str(value))


def output(args, result):
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_human(result)


def _parse_params(items):
    """`key=value` pairs (value as JSON when it parses, else text), or one JSON object."""
    if len(items) == 1 and items[0].lstrip().startswith("{"):
        return json.loads(items[0])
    params = {}
    for item in items:
        key, sep, value = item.partition("=")
        if not sep:
            raise CLIError("Parameters are key=value (or one JSON object): {!r}".format(item))
        try:
            params[key] = json.loads(value)
        except json.JSONDecodeError:
            params[key] = value
    return params


# ------------------------------------------------------------------------------
# Commands

def cmd_info(args, session):
    output(args, session.command("info", {}, args.file or ""))


def cmd_open(args, session):
    if not session.live:
        raise CLIError("`open` opens a file in the running Moritz: use --connect (or `info <file>` headless)")
    output(args, session.command("open", {"path": os.path.abspath(args.file)}))


def cmd_render(args, session):
    params = {"path": os.path.abspath(args.output), "camera": args.camera or ""}
    if args.frames:
        start, _sep, end = args.frames.partition("-")
        params["frame"], params["end_frame"] = int(start), int(end or start)
    elif args.frame is not None:
        params["frame"] = args.frame
    output(args, session.command("render", params, args.file))


def cmd_convert(args, session):
    source = os.path.abspath(args.input)
    target = os.path.abspath(args.output)
    if source.lower().endswith(".blend"):
        result = session.command("export", {"path": target, "selected_only": False}, source)
    else:
        code = ("from moritz_mcp import commands\n"
                "_imp = commands.run('import', {{'path': {!r}}})\n"
                "result = _imp if _imp['status'] != 'ok' else commands.run('export', {{'path': {!r}}})\n"
                ).format(source, target)
        if session.live:
            raise CLIError("convert with a non-.blend input runs headless only (it starts from an empty scene)")
        result = session.run(code, empty=True)
        if result.get("status") == "error":
            raise CLIError(result["message"])
        result.pop("status", None)
    output(args, result)


def cmd_run(args, session):
    script = os.path.abspath(args.script)
    code = ("import sys\nsys.argv = [{!r}] + {!r}\n"
            "from moritz_mcp import commands\n"
            "_r = commands.run('run_python', {{'path': {!r}}})\n"
            "result = _r\n").format(script, args.script_args, script)
    result = session.run(code, args.file or "")
    if result.get("status") == "error":
        raise CLIError(result["message"])
    output(args, result.get("result", {}))


def cmd_test(args, _session):
    """Run test scripts (test_*.py) each in a fresh background Moritz."""
    files = []
    for path in args.paths or ["."]:
        if os.path.isdir(path):
            files += sorted(os.path.join(path, f) for f in os.listdir(path)
                            if f.startswith("test_") and f.endswith(".py"))
        else:
            files.append(path)
    if not files:
        raise CLIError("No test_*.py files found")
    exe = moritz_exe()
    failed = []
    results = []
    for path in files:
        try:
            proc = subprocess.run([exe, "--factory-startup", "-b", "--python", path], capture_output=True,
                                  text=True, encoding="utf-8", errors="replace", timeout=args.timeout,
                                  stdin=subprocess.DEVNULL, check=False)
            log = proc.stdout + proc.stderr
            ok = not any(mark in log for mark in _TEST_FAILED) and \
                not any(line.startswith("FAIL") or " FAIL " in line for line in log.splitlines())
        except subprocess.TimeoutExpired:
            ok, log = False, "timed out"
        results.append({"name": os.path.basename(path), "ok": ok})
        if not ok:
            failed.append(path)
            if args.verbose:
                sys.stderr.write(log[-4000:] + "\n")
        if not args.json:
            print("{:s} {:s}".format("ok  " if ok else "FAIL", path), flush=True)
    summary = {"scripts": len(files), "failed": len(failed), "failures": [os.path.basename(f) for f in failed]}
    if args.json:
        print(json.dumps({"results": results, **summary}, indent=2))
    else:
        print("{:d} scripts, {:d} failed".format(len(files), len(failed)))
    return 1 if failed else 0


def cmd_command(args, session):
    if args.action == "list":
        result = session.run("from moritz_mcp import commands\nresult = {'commands': commands.describe()}\n")
        if args.json:
            output(args, result)
            return
        for cmd in result["commands"]:
            props = cmd["input_schema"]["properties"]
            required = set(cmd["input_schema"]["required"])
            sig = " ".join(("{:s}=<{:s}>" if p in required else "[{:s}=<{:s}>]").format(p, props[p]["type"])
                           for p in props)
            print("{:s} {:s}".format(cmd["name"], sig).rstrip())
            print("    " + cmd["description"])
        return
    if not args.name:
        raise CLIError("command run <name> [key=value ...]")
    output(args, session.command(args.name, _parse_params(args.params), args.file or ""))


def cmd_serve(args, _session):
    """A background Moritz that MCP clients and `--connect` can use (no window)."""
    exe = moritz_exe()
    cmd = [exe, "-b"] + ([args.file] if args.file else []) + ["-c", "moritz_mcp", "--port", str(args.port)]
    return subprocess.call(cmd)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="moritz-cli",
        description="Moritz from the command line. Headless by default (a background Moritz per command); "
                    "--connect works in the running Moritz.")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    parser.add_argument("--connect", action="store_true",
                        help="Use the running Moritz (Preferences > System > Moritz MCP must be on)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("MORITZ_MCP_PORT") or DEFAULT_PORT),
                        help="Moritz MCP port (default %(default)s)")
    parser.add_argument("--factory-startup", action="store_true",
                        help="Headless: ignore your preferences and add-ons")
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="<command>")

    p = sub.add_parser("info", help="Objects, modifier stacks, missing files of a .blend (or the open scene)")
    p.add_argument("file", nargs="?")
    p.set_defaults(fn=cmd_info)

    p = sub.add_parser("open", help="Open a .blend in the running Moritz (--connect)")
    p.add_argument("file")
    p.set_defaults(fn=cmd_open)

    p = sub.add_parser("render", help="Render a still or frames")
    p.add_argument("file", nargs="?", default="", help=".blend (headless); the open scene with --connect")
    p.add_argument("-o", "--output", required=True, help="Output file, #### for frame numbers")
    p.add_argument("-f", "--frame", type=int, help="Frame (default: the current one)")
    p.add_argument("--frames", help="Range, e.g. 1-100")
    p.add_argument("--camera", help="Camera object")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("convert", help="Convert between .blend, FBX, OBJ, glTF/GLB, USD, Alembic, STL, PLY "
                                       "(and .mxscene from 3ds Max)")
    p.add_argument("input")
    p.add_argument("output")
    p.set_defaults(fn=cmd_convert)

    p = sub.add_parser("run", help="Run a Python script in Moritz (bpy); assign a dict to `result` to print it")
    p.add_argument("script")
    p.add_argument("--file", default="", help=".blend to open first")
    p.add_argument("script_args", nargs=argparse.REMAINDER, help="After --: arguments for the script (sys.argv)")
    p.set_defaults(fn=cmd_run)

    p = sub.add_parser("test", help="Run test_*.py scripts, each in a fresh background Moritz")
    p.add_argument("paths", nargs="*", help="Folders or files (default: the current folder)")
    p.add_argument("--timeout", type=float, default=600.0, help="Seconds per script")
    p.add_argument("-v", "--verbose", action="store_true", help="Print the log of failed scripts")
    p.set_defaults(fn=cmd_test)

    p = sub.add_parser("command", help="Moritz's command set (the same as the Moritz MCP server's tools)")
    p.add_argument("action", choices=("list", "run"))
    p.add_argument("name", nargs="?")
    p.add_argument("params", nargs="*", help="key=value (values as JSON) or one JSON object")
    p.add_argument("--file", help="Headless: .blend to open first")
    p.set_defaults(fn=cmd_command)

    p = sub.add_parser("serve", help="Start a background Moritz that MCP clients and --connect can use")
    p.add_argument("file", nargs="?")
    p.set_defaults(fn=cmd_serve)
    return parser


# Options that work anywhere on the command line (before a script's `--`).
_GLOBAL_FLAGS = ("--json", "--connect", "--factory-startup")


def _globals_first(argv):
    """Move the global options to the front, so `moritz-cli info x.blend --json` works too."""
    end = argv.index("--") if "--" in argv else len(argv)
    head, rest, tail = [], [], argv[end:]
    i = 0
    while i < end:
        arg = argv[i]
        if arg in _GLOBAL_FLAGS or arg.startswith("--port="):
            head.append(arg)
        elif arg == "--port" and i + 1 < end:
            head += argv[i:i + 2]
            i += 1
        else:
            rest.append(arg)
        i += 1
    return head + rest + tail


def main(argv=None):
    argv = _globals_first(list(sys.argv[1:] if argv is None else argv))
    args = build_parser().parse_args(argv)
    if getattr(args, "script_args", None) and args.script_args[:1] == ["--"]:
        args.script_args = args.script_args[1:]
    try:
        code = args.fn(args, Session(args))
    except CLIError as ex:
        if args.json:
            print(json.dumps({"status": "error", "message": str(ex)}))
        else:
            sys.stderr.write("moritz-cli: {:s}\n".format(str(ex)))
        return 1
    return code or 0


if __name__ == "__main__":
    sys.exit(main())
