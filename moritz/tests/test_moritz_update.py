# Run: moritz.exe --factory-startup -b --python moritz/tests/test_moritz_update.py
# The updater (bl_operators/moritz_update.py, TASK.md "Updater") against a fake releases list on a
# local file server: newer / older / same versions, pre-releases, online access off, a good
# download and a bad checksum, the addresses it accepts, and the install helpers per platform.
# Nothing is installed, and the user's settings are not touched.
import functools
import hashlib
import http.server
import json
import os
import subprocess
import tempfile
import threading

import bpy
from bl_operators import moritz_update as m

failures = []


def check(name, ok, *info):
    print("MXUP", "OK" if ok else "FAIL", name, *info, flush=True)
    if not ok:
        failures.append(name)


root = tempfile.mkdtemp(prefix="moritz_update_test_")
m._settings_path = lambda: os.path.join(root, "moritz_update.json")


def asset(name):
    return {"name": name, "browser_download_url": SERVER + "/files/" + name}


# A local server for the releases list and the packages.
files = os.path.join(root, "files")
os.makedirs(files)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
SERVER = "http://127.0.0.1:{:d}".format(server.server_address[1])
os.environ["MORITZ_UPDATE_TEST_SERVER"] = SERVER

SUFFIX = "-windows-x64.msi"
good = b"a new Moritz" * 1000
with open(os.path.join(files, "moritz-0.4.0" + SUFFIX), "wb") as f:
    f.write(good)
with open(os.path.join(files, "moritz-0.5.0" + SUFFIX), "wb") as f:
    f.write(b"tampered")
with open(os.path.join(files, "SHA256SUMS.txt"), "w", encoding="utf-8") as f:
    f.write("{}  moritz-0.4.0{}\n".format(hashlib.sha256(good).hexdigest(), SUFFIX))
    # 0.5.0's line is for other bytes than the file has.
    f.write("{}  moritz-0.5.0{}\n".format(hashlib.sha256(b"the real one").hexdigest(), SUFFIX))

RELEASES = [
    {"tag_name": "v0.5.0-beta", "prerelease": True, "body": "beta",
     "assets": [asset("moritz-0.5.0" + SUFFIX), asset("SHA256SUMS.txt")]},
    {"tag_name": "v0.4.0", "body": "Notes for 0.4.0", "html_url": SERVER + "/page",
     "assets": [asset("moritz-0.4.0" + SUFFIX), asset("moritz-0.4.0-linux-x64.tar.xz"),
                asset("SHA256SUMS.txt")]},
    {"tag_name": "v0.6.0", "draft": True, "assets": []},
    {"tag_name": "v0.3.0", "assets": []},
    {"tag_name": "v0.2.0", "assets": []},
]
with open(os.path.join(root, "releases"), "w", encoding="utf-8") as f:
    json.dump(RELEASES, f)

# Versions.
check("a pre-release sorts before its release", m.parse_version("0.5.0-beta") < m.parse_version("v0.5.0"))
check("0.10 is newer than 0.9", m.parse_version("0.10.0") > m.parse_version("0.9.9"))

# Which release is offered.
rel = m.newest_release(RELEASES, "0.3.0", False, SUFFIX)
check("newer: 0.4.0 offered to 0.3.0, with its package and checksums",
      rel and rel["version"] == "0.4.0" and rel["asset"] == "moritz-0.4.0" + SUFFIX and rel["sums_url"],
      rel and rel["version"])
check("same version: nothing offered", m.newest_release(RELEASES, "0.4.0", False, SUFFIX) is None)
check("older: nothing offered to a newer copy", m.newest_release(RELEASES, "0.4.1", False, SUFFIX) is None)
check("drafts are never offered", all(r is None or r["version"] != "0.6.0"
                                      for r in [m.newest_release(RELEASES, "0.1.0", True, SUFFIX)]))
pre = m.newest_release(RELEASES, "0.3.0", True, SUFFIX)
check("pre-releases only when asked", pre and pre["version"] == "0.5.0-beta" and pre["prerelease"],
      pre and pre["version"])
linux = m.newest_release(RELEASES, "0.3.0", False, "-linux-x64.tar.xz")
check("the platform's package", linux["asset"] == "moritz-0.4.0-linux-x64.tar.xz")
check("no package: a notice only", m.newest_release(RELEASES, "0.3.0", False, None)["asset"] is None)

# Addresses.
check("GitHub over HTTPS is allowed", m._allowed("https://api.github.com/repos/x") and
      m._allowed("https://objects.githubusercontent.com/a"))
check("plain HTTP is refused", not m._allowed("http://github.com/x"))
check("other hosts are refused", not m._allowed("https://example.com/moritz.msi"))
check("the test server only while testing", m._allowed(SERVER + "/releases"))

# Fetch and download.
fetched = m.fetch_releases(timeout=5)
check("releases fetched from the server", len(fetched) == len(RELEASES))
folder = os.path.join(root, "download")
path = m.download_verified(m.newest_release(fetched, "0.3.0", False, SUFFIX), folder, timeout=5)
with open(path, "rb") as f:
    check("a good download is kept", f.read() == good, path)
try:
    m.download_verified(m.newest_release(fetched, "0.3.0", True, SUFFIX), folder, timeout=5)
    check("a bad checksum is refused", False)
except ValueError as ex:
    check("a bad checksum is refused and the file deleted",
          "checksum" in str(ex) and not os.path.exists(os.path.join(folder, "moritz-0.5.0" + SUFFIX)), ex)
no_sums = dict(m.newest_release(fetched, "0.3.0", False, SUFFIX), sums_url="")
try:
    m.download_verified(no_sums, folder, timeout=5)
    check("no SHA256SUMS.txt, no install", False)
except ValueError:
    check("no SHA256SUMS.txt, no install", True)

# Settings, through the Preferences properties.
wm = bpy.context.window_manager
wm.moritz_update_auto = True
check("settings are kept", m.settings()["auto_install"] is True and wm.moritz_update_auto)
check("defaults: check on startup, no auto, no pre-releases",
      m._DEFAULTS["check_on_startup"] and not m._DEFAULTS["auto_install"] and not m._DEFAULTS["prereleases"])

# Install helpers (written, not run).
_cmd, ps, _ext = m.installer_script('MSI', r"C:\t\moritz.msi", 42, r"C:\M\moritz.exe", True)
check("Windows: msiexec /passive after Moritz quits, then a restart",
      "Wait-Process -Id 42" in ps and "/passive" in ps and "moritz.exe" in ps)
_cmd, sh, _ext = m.installer_script('FOLDER', "/t/m.tar.xz", 42, "/opt/moritz/moritz", False)
check("Linux: unpack next to the folder and swap it, no restart at a plain quit",
      "kill -0 42" in sh and "tar -xJf" in sh and "mv \"$new\" \"$dir\"" in sh and "nohup" not in sh)
_cmd, sh, _ext = m.installer_script('APP', "/t/m.dmg", 42, "/Applications/Moritz.app/Contents/MacOS/Moritz", True)
check("macOS: copy Moritz.app from the dmg, then open it",
      "hdiutil attach" in sh and "ditto" in sh and "/Applications/Moritz.app" in sh and "open" in sh)
check("a copy that can't update itself gets no helper", m.installer_script('NOTICE', "", 1, "", False) is None)

# The whole check, with online access on and off (a fresh Moritz each, as the flag is set at start).
code = ("import os, time\n"
        "from bl_operators import moritz_update as m\n"
        "m._settings_path = lambda: os.path.join({root!r}, 'child.json')\n"
        "m.current_version = lambda: '0.3.0'\n"
        "started = m.check(manual=True)\n"
        "m._worker and m._worker.join(10)\n"
        "print('MXUPCHILD', started, m.state.status, m.state.release and m.state.release['version'], flush=True)\n"
        ).format(root=root)
for flag, expected in (("--offline-mode", "False OFFLINE None"), ("--online-mode", "True AVAILABLE 0.4.0")):
    out = subprocess.run([bpy.app.binary_path, "-b", "--factory-startup", flag, "--python-expr", code],
                         capture_output=True, text=True, encoding="utf-8", errors="replace",
                         stdin=subprocess.DEVNULL, timeout=120, env=dict(os.environ)).stdout
    line = next((ln[10:].strip() for ln in out.splitlines() if ln.startswith("MXUPCHILD")), None)
    check("check with " + flag, line == expected, line)

server.shutdown()
print("MXUP FAILURES", len(failures), failures, flush=True)
