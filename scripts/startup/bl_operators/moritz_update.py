# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Moritz's updater: checks GitHub Releases for a newer Moritz, downloads it in the background,
checks its SHA-256 and installs it when Moritz quits.

- Only with Allow Online Access on, only over HTTPS from GitHub, only this repository's releases,
  and only files listed in the release's SHA256SUMS.txt.
- Windows: the per-user MSI (msiexec /passive). Linux: the tar.xz is unpacked next to the program
  folder and swapped in. macOS: Moritz.app is copied from the dmg. A copy Moritz can't replace (the
  portable zip, a folder without write access) only gets a notice with the download page.
- Installing waits for Moritz to quit (after asking to save); automatic updates install at the next
  quit, never during a session.

Settings live in <config>/moritz_update.json, shown in Preferences > System > Updates.
"""

import atexit
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator

REPOSITORY = "cyberhirsch/moritz"
API_URL = "https://api.github.com/repos/{:s}/releases".format(REPOSITORY)
PAGE_URL = "https://github.com/{:s}/releases".format(REPOSITORY)
SUMS_NAME = "SHA256SUMS.txt"
ALLOWED_HOSTS = {"api.github.com", "github.com", "objects.githubusercontent.com",
                 "release-assets.githubusercontent.com"}
DAY = 24 * 60 * 60



def _test_server():
    """Tests point the updater at a local server (plain HTTP, 127.0.0.1 only)."""
    return os.environ.get("MORITZ_UPDATE_TEST_SERVER", "")


# ------------------------------------------------------------------------------
# Settings

_DEFAULTS = {"check_on_startup": True, "auto_install": False, "prereleases": False,
             "last_check": 0.0, "skipped": ""}


def _settings_path():
    return os.path.join(bpy.utils.user_resource('CONFIG'), "moritz_update.json")


def settings():
    data = dict(_DEFAULTS)
    try:
        with open(_settings_path(), encoding="utf-8") as f:
            data.update(json.load(f))
    except (OSError, ValueError):
        pass
    return data


def _save(**changes):
    data = settings()
    data.update(changes)
    try:
        os.makedirs(os.path.dirname(_settings_path()), exist_ok=True)
        with open(_settings_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1)
    except OSError:
        pass


def _setting_prop(key, name, description):
    return BoolProperty(name=name, description=description,
                        get=lambda _self: bool(settings()[key]),
                        set=lambda _self, value: _save(**{key: bool(value)}),
                        options={'SKIP_SAVE'})


# ------------------------------------------------------------------------------
# Versions and assets

def current_version():
    return getattr(bpy.app, "moritz_version_string", "0.0.0")


def parse_version(text):
    """A comparable key for "v0.3.1", "0.3.1-beta" (a pre-release sorts before its release)."""
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?(.*)", text or "")
    if not match:
        return None
    major, minor, patch, rest = match.groups()
    rest = rest.strip(" -_.").lower()
    return (int(major), int(minor), int(patch or 0), 0 if rest else 1, rest)


def install_kind():
    """How this copy is updated: 'MSI', 'FOLDER' (Linux), 'APP' (macOS) or 'NOTICE' (portable, read-only)."""
    exe = os.path.realpath(bpy.app.binary_path)
    folder = os.path.dirname(exe)
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Moritz") as key:
                installed = winreg.QueryValueEx(key, "InstallDir")[0]
            if os.path.normcase(os.path.normpath(installed)) == os.path.normcase(os.path.normpath(folder)):
                return 'MSI'
        except OSError:
            pass
        return 'NOTICE'
    if sys.platform == "darwin":
        app = os.path.dirname(os.path.dirname(folder))
        if app.endswith(".app") and os.access(os.path.dirname(app), os.W_OK):
            return 'APP'
        return 'NOTICE'
    if os.access(folder, os.W_OK) and os.access(os.path.dirname(folder), os.W_OK):
        return 'FOLDER'
    return 'NOTICE'


def asset_suffix(kind=None):
    """The end of this platform's package name, or None where only a notice is given."""
    kind = kind or install_kind()
    arch = {"x86_64": "x64", "amd64": "x64", "arm64": "arm64", "aarch64": "arm64"}.get(
        platform.machine().lower(), platform.machine().lower())
    return {'MSI': "-windows-x64.msi", 'FOLDER': "-linux-{:s}.tar.xz".format(arch),
            'APP': "-macos-{:s}.dmg".format(arch)}.get(kind)


def newest_release(releases, current, prereleases, suffix):
    """The newest release above `current`, as a dict, or None."""
    best = None
    for rel in releases:
        if rel.get("draft") or (rel.get("prerelease") and not prereleases):
            continue
        key = parse_version(rel.get("tag_name") or rel.get("name"))
        if key is None or key <= parse_version(current):
            continue
        if best is not None and key <= best["key"]:
            continue
        assets = {a.get("name", ""): a.get("browser_download_url", "") for a in rel.get("assets", ())}
        asset = next((n for n in assets if suffix and n.endswith(suffix)), None)
        best = {
            "key": key,
            "version": (rel.get("tag_name") or "").lstrip("vV"),
            "notes": rel.get("body") or "",
            "page": rel.get("html_url") or PAGE_URL,
            "prerelease": bool(rel.get("prerelease")),
            "asset": asset,
            "asset_url": assets.get(asset, "") if asset else "",
            "sums_url": assets.get(SUMS_NAME, ""),
        }
    return best


# ------------------------------------------------------------------------------
# Network (worker threads only)

def _allowed(url):
    parts = urllib.parse.urlsplit(url)
    test = _test_server()
    if test and url.startswith(test) and parts.scheme == "http" and parts.hostname == "127.0.0.1":
        return True
    return parts.scheme == "https" and parts.hostname in ALLOWED_HOSTS


class _SafeRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _allowed(newurl):
            raise urllib.error.URLError("redirect to an unexpected address: " + newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _open(url, timeout):
    if not _allowed(url):
        raise urllib.error.URLError("not a GitHub address: " + url)
    request = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "Moritz-Updater/" + current_version()})
    return urllib.request.build_opener(_SafeRedirects).open(request, timeout=timeout)


def fetch_releases(timeout=10):
    url = (_test_server() + "/releases") if _test_server() else API_URL
    with _open(url, timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url, path, progress=None, timeout=30):
    with _open(url, timeout) as response, open(path, "wb") as out:
        total = int(response.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = response.read(1 << 20)
            if not chunk:
                break
            out.write(chunk)
            done += len(chunk)
            if progress and total:
                progress(done / total)


def expected_sha256(sums_text, name):
    for line in sums_text.splitlines():
        parts = line.strip().split()
        if len(parts) == 2 and parts[1].lstrip("*") == name:
            return parts[0].lower()
    return None


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_verified(release, folder, progress=None, timeout=30):
    """Download the release's package and check it against SHA256SUMS.txt; the file's path."""
    if not release.get("sums_url"):
        raise ValueError("the release has no " + SUMS_NAME)
    os.makedirs(folder, exist_ok=True)
    sums = os.path.join(folder, SUMS_NAME)
    download(release["sums_url"], sums, timeout=timeout)
    with open(sums, encoding="utf-8", errors="replace") as f:
        expected = expected_sha256(f.read(), release["asset"])
    if not expected:
        raise ValueError("{:s} is not in {:s}".format(release["asset"], SUMS_NAME))
    path = os.path.join(folder, release["asset"])
    download(release["asset_url"], path, progress, timeout)
    if sha256_of(path) != expected:
        os.remove(path)
        raise ValueError("the download's checksum doesn't match; it was deleted")
    return path


# ------------------------------------------------------------------------------
# State, shared with the UI (written by the worker threads, read by the timer and the UI)

class _State:
    status = 'IDLE'  # IDLE CHECKING AVAILABLE CURRENT DOWNLOADING READY ERROR OFFLINE
    message = ""
    release = None
    progress = 0.0
    path = ""
    manual = False          # Check Now / Help menu: show the result.
    install_requested = False  # Install pressed: quit once downloaded.
    pending = False         # Install at quit.
    restart = False


state = _State()
_worker = None


def _run(target):
    global _worker
    _worker = threading.Thread(target=target, daemon=True)
    _worker.start()
    if not bpy.app.timers.is_registered(_poll):
        bpy.app.timers.register(_poll, first_interval=0.3, persistent=True)


def check(manual=False):
    """Start a check (in the background). Without online access nothing goes out."""
    if not bpy.app.online_access:
        state.status = 'OFFLINE'
        state.message = "Allow Online Access is off (Preferences > System > Network)"
        return False
    if state.status in {'CHECKING', 'DOWNLOADING'}:
        return True
    prefs = settings()
    timeout = max(bpy.context.preferences.system.network_timeout, 5)
    state.status, state.message, state.manual = 'CHECKING', "", manual
    current, suffix = current_version(), asset_suffix()

    def work():
        try:
            release = newest_release(fetch_releases(timeout), current, prefs["prereleases"], suffix)
        except Exception as ex:
            state.status, state.message = 'ERROR', "Update check failed: {!s}".format(ex)
            return
        if release is None or (not manual and release["version"] == prefs["skipped"]):
            state.status, state.release = 'CURRENT', None
        else:
            state.status, state.release = 'AVAILABLE', release
    _run(work)
    return True


def start_download():
    release = state.release
    if not release or not release.get("asset"):
        return False
    folder = os.path.join(tempfile.gettempdir(), "moritz_update", release["version"])
    timeout = max(bpy.context.preferences.system.network_timeout, 10)
    state.status, state.progress = 'DOWNLOADING', 0.0

    def progress(value):
        state.progress = value

    def work():
        try:
            state.path = download_verified(release, folder, progress, timeout)
            state.status = 'READY'
        except Exception as ex:
            state.status, state.message = 'ERROR', "Update download failed: {!s}".format(ex)
    _run(work)
    return True


def _redraw():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type in {'STATUSBAR', 'PREFERENCES'}:
                area.tag_redraw()


def _window_override():
    wm = bpy.context.window_manager
    return {"window": wm.windows[0]} if wm.windows else None


def _poll():
    """Main thread: follows the worker and acts on its result."""
    _redraw()
    if _worker is not None and _worker.is_alive():
        return 0.3
    if state.status in {'AVAILABLE', 'CURRENT'}:
        _save(last_check=time.time())
    if state.status == 'AVAILABLE':
        if settings()["auto_install"] and state.release.get("asset") and not state.manual:
            # Automatic: download now, install at the next quit.
            state.pending, state.restart = True, False
            start_download()
            return 0.3
        if state.manual:
            state.manual = False
            override = _window_override()
            if override:
                with bpy.context.temp_override(**override):
                    bpy.ops.wm.moritz_update_dialog('INVOKE_DEFAULT')
    elif state.status == 'READY' and state.install_requested:
        state.install_requested = False
        state.pending, state.restart = True, True
        override = _window_override()
        if override:
            with bpy.context.temp_override(**override):
                # Asks to save unsaved work; the install runs once Moritz has quit.
                bpy.ops.wm.quit_blender('INVOKE_DEFAULT')
    return None


def _startup_check():
    if bpy.app.background:
        return None
    prefs = settings()
    if prefs["check_on_startup"] and time.time() - prefs["last_check"] > DAY and bpy.app.online_access:
        check()
    return None


# ------------------------------------------------------------------------------
# Installing at quit

def installer_script(kind, package, pid, exe, restart):
    """(program and arguments, script text) of the helper that installs once Moritz has quit."""
    if kind == 'MSI':
        text = (
            "$ErrorActionPreference = 'SilentlyContinue'\n"
            "Wait-Process -Id {pid:d}\n"
            "Start-Process msiexec.exe -ArgumentList @('/i', '\"{pkg:s}\"', '/passive') -Wait\n"
            "{restart:s}"
        ).format(pid=pid, pkg=package, restart="Start-Process '{:s}'\n".format(exe) if restart else "")
        return ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden",
                "-File"], text, ".ps1"
    if kind == 'FOLDER':
        folder = os.path.dirname(exe)
        text = (
            "#!/bin/sh\n"
            "while kill -0 {pid:d} 2>/dev/null; do sleep 0.5; done\n"
            "set -e\n"
            "dir='{dir:s}'\n"
            "tmp=\"$(dirname \"$dir\")/.moritz-update-$$\"\n"
            "mkdir -p \"$tmp\"\n"
            "tar -xJf '{pkg:s}' -C \"$tmp\"\n"
            "new=$(find \"$tmp\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\n"
            "mv \"$dir\" \"$dir.old-$$\"\n"
            "mv \"$new\" \"$dir\"\n"
            "rm -rf \"$dir.old-$$\" \"$tmp\"\n"
            "{restart:s}"
        ).format(pid=pid, dir=folder, pkg=package,
                 restart="nohup \"$dir/moritz\" >/dev/null 2>&1 &\n" if restart else "")
        return ["/bin/sh"], text, ".sh"
    if kind == 'APP':
        app = os.path.dirname(os.path.dirname(os.path.dirname(exe)))
        text = (
            "#!/bin/sh\n"
            "while kill -0 {pid:d} 2>/dev/null; do sleep 0.5; done\n"
            "set -e\n"
            "app='{app:s}'\n"
            "mnt=$(mktemp -d)\n"
            "hdiutil attach -nobrowse -quiet -mountpoint \"$mnt\" '{pkg:s}'\n"
            "rm -rf \"$app.old\"\n"
            "mv \"$app\" \"$app.old\"\n"
            "ditto \"$mnt/Moritz.app\" \"$app\"\n"
            "hdiutil detach -quiet \"$mnt\"\n"
            "rm -rf \"$app.old\"\n"
            "{restart:s}"
        ).format(pid=pid, app=app, pkg=package, restart="open \"$app\"\n" if restart else "")
        return ["/bin/sh"], text, ".sh"
    return None


def _install_at_exit():
    if not (state.pending and state.status == 'READY' and state.path):
        return
    script = installer_script(install_kind(), state.path, os.getpid(),
                              os.path.realpath(bpy.app.binary_path), state.restart)
    if script is None:
        return
    command, text, ext = script
    path = os.path.join(os.path.dirname(state.path), "install" + ext)
    with open(path, "w", encoding="utf-8", newline="\n" if ext == ".sh" else "\r\n") as f:
        f.write(text)
    if sys.platform == "win32":
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        subprocess.Popen(command + [path], creationflags=flags, close_fds=True)
    else:
        subprocess.Popen(command + [path], start_new_session=True, close_fds=True)


# ------------------------------------------------------------------------------
# Operators and UI

class WM_OT_moritz_update_check(Operator):
    """Look for a newer Moritz on GitHub"""
    bl_idname = "wm.moritz_update_check"
    bl_label = "Check for Updates"

    def execute(self, context):
        if state.status == 'AVAILABLE' and state.release:
            return bpy.ops.wm.moritz_update_dialog('INVOKE_DEFAULT')
        if not check(manual=True):
            self.report({'WARNING'}, "Can't check for updates: " + state.message)
            return {'CANCELLED'}
        return {'FINISHED'}


class WM_OT_moritz_update_dialog(Operator):
    """The newer Moritz: its notes, and Install / Skip This Version / Later"""
    bl_idname = "wm.moritz_update_dialog"
    bl_label = "Moritz Update"

    def invoke(self, context, _event):
        if not state.release:
            return {'CANCELLED'}
        return context.window_manager.invoke_popup(self, width=480)

    def execute(self, _context):
        return {'FINISHED'}

    def draw(self, _context):
        release = state.release
        layout = self.layout
        layout.label(text="Moritz {:s} is available (you have {:s})".format(
            release["version"], current_version()), icon='INFO', translate=False)
        notes = [line for line in release["notes"].replace("\r", "").split("\n")][:24]
        if notes:
            col = layout.box().column(align=True)
            col.scale_y = 0.8
            for line in notes:
                # GitHub's notes are Markdown: headings without their #.
                col.label(text=line.strip().lstrip("#").strip()[:110], translate=False)
        row = layout.row()
        if release.get("asset") and install_kind() != 'NOTICE':
            row.operator("wm.moritz_update_install", text="Install")
        else:
            row.operator("wm.url_open", text="Open Download Page").url = release["page"]
        row.operator("wm.moritz_update_skip", text="Skip This Version")
        row.operator("wm.moritz_update_later", text="Later")


class WM_OT_moritz_update_install(Operator):
    """Download the update and install it: Moritz quits (asking to save) and starts again"""
    bl_idname = "wm.moritz_update_install"
    bl_label = "Install Update"

    def execute(self, _context):
        if state.status == 'READY':
            state.install_requested = True
            if not bpy.app.timers.is_registered(_poll):
                bpy.app.timers.register(_poll, first_interval=0.1, persistent=True)
        elif start_download():
            state.install_requested = True
        else:
            self.report({'WARNING'}, "No package for this copy of Moritz; use the download page")
            return {'CANCELLED'}
        return {'FINISHED'}


class WM_OT_moritz_update_skip(Operator):
    """Don't offer this version again (Check for Updates still shows it)"""
    bl_idname = "wm.moritz_update_skip"
    bl_label = "Skip This Version"

    def execute(self, _context):
        if state.release:
            _save(skipped=state.release["version"])
        state.status, state.release, state.pending = 'CURRENT', None, False
        _redraw()
        return {'FINISHED'}


class WM_OT_moritz_update_later(Operator):
    """Remind me at the next check"""
    bl_idname = "wm.moritz_update_later"
    bl_label = "Later"

    def execute(self, _context):
        return {'FINISHED'}


def draw_status(self, _context):
    """The quiet status bar line."""
    layout = self.layout
    if state.status == 'AVAILABLE' and state.release:
        layout.operator("wm.moritz_update_dialog", text="Moritz {:s} is available".format(state.release["version"]),
                        icon='INFO', emboss=False, translate=False)
    elif state.status == 'DOWNLOADING':
        layout.label(text="Downloading Moritz {:s}: {:d}%".format(
            state.release["version"], int(state.progress * 100)), translate=False)
    elif state.status == 'READY' and state.pending and not state.restart:
        layout.label(text="Moritz {:s} installs when you quit".format(state.release["version"]),
                     icon='CHECKMARK', translate=False)
    elif state.status == 'ERROR' and state.message:
        layout.operator("wm.moritz_update_check", text=state.message[:80], icon='ERROR', emboss=False,
                        translate=False)


def draw_preferences(layout, context):
    """Preferences > System > Updates."""
    wm = context.window_manager
    layout.prop(wm, "moritz_update_on_startup")
    layout.prop(wm, "moritz_update_auto")
    layout.prop(wm, "moritz_update_prereleases")
    row = layout.row()
    row.operator("wm.moritz_update_check", text="Check Now")
    last = settings()["last_check"]
    text = time.strftime("Last checked %Y-%m-%d %H:%M", time.localtime(last)) if last else "Not checked yet"
    if state.status == 'CHECKING':
        text = "Checking…"
    elif state.status == 'CURRENT':
        text = "Moritz {:s} is up to date. {:s}".format(current_version(), text)
    elif state.status in {'OFFLINE', 'ERROR'}:
        text = state.message
    elif state.status in {'AVAILABLE', 'DOWNLOADING', 'READY'} and state.release:
        text = "Moritz {:s} is available".format(state.release["version"])
    row.label(text=text, translate=False)
    if install_kind() == 'NOTICE':
        layout.label(text="This copy can't update itself: newer versions are offered as a download.",
                     icon='INFO')


def _attach_status():
    header = getattr(bpy.types, "STATUSBAR_HT_header", None)
    if header is not None:
        header.remove(draw_status)
        header.append(draw_status)
    return None


classes = (
    WM_OT_moritz_update_check,
    WM_OT_moritz_update_dialog,
    WM_OT_moritz_update_install,
    WM_OT_moritz_update_skip,
    WM_OT_moritz_update_later,
)


def register():
    wm = bpy.types.WindowManager
    wm.moritz_update_on_startup = _setting_prop(
        "check_on_startup", "Check for Updates on Startup", "Look for a newer Moritz at most once a day")
    wm.moritz_update_auto = _setting_prop(
        "auto_install", "Install Updates Automatically",
        "Download a newer Moritz in the background and install it when Moritz quits")
    wm.moritz_update_prereleases = _setting_prop(
        "prereleases", "Include Pre-releases", "Offer pre-release versions too")
    # The status bar's header registers after the operators (bl_ui), so it is joined a moment later.
    bpy.app.timers.register(_attach_status, first_interval=0.0, persistent=True)
    bpy.app.timers.register(_startup_check, first_interval=5.0, persistent=True)
    atexit.register(_install_at_exit)


def unregister():
    atexit.unregister(_install_at_exit)
    for timer in (_startup_check, _attach_status):
        if bpy.app.timers.is_registered(timer):
            bpy.app.timers.unregister(timer)
    header = getattr(bpy.types, "STATUSBAR_HT_header", None)
    if header is not None:
        header.remove(draw_status)
    del bpy.types.WindowManager.moritz_update_on_startup
    del bpy.types.WindowManager.moritz_update_auto
    del bpy.types.WindowManager.moritz_update_prereleases
