# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Pack a built Moritz for Linux (.tar.xz) or macOS (.dmg).

    python moritz/tools/make_unix_package.py <install dir> [<Maximize repo>] [<out dir>]

<install dir> is CMake's install folder (`build/bin`): on Linux it holds the `moritz` program, on
macOS `Moritz.app`. The Maximize add-on is copied in as real files, as for the Windows zip.

- Linux: `moritz-<version>-linux-x64.tar.xz`, the program folder with `moritz.desktop` and the
  icon, run from wherever it is unpacked.
- macOS: `moritz-<version>-macos-arm64.dmg` with `Moritz.app` and a link to Applications. The app
  is signed ad hoc (`codesign -s -`); without an Apple Developer ID it is not notarized, so on first
  start macOS asks to allow it (right-click > Open, or `xattr -cr /Applications/Moritz.app`).
"""

import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile

from make_portable_zip import moritz_version, version, record_checksum

ARCH = {"x86_64": "x64", "amd64": "x64", "arm64": "arm64", "aarch64": "arm64"}


def copy_maximize(resources, maximize):
    """Maximize into <resources>/<version>/scripts/addons_core/maximize, as real files."""
    if not maximize:
        return
    dst = os.path.join(resources, version(resources), "scripts", "addons_core", "maximize")
    if os.path.lexists(dst):
        if os.path.islink(dst):
            os.unlink(dst)
        else:
            shutil.rmtree(dst)
    shutil.copytree(os.path.join(maximize, "maximize"), dst,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def linux(install, maximize, out_dir):
    top = "moritz-{}-linux-{}".format(moritz_version(), ARCH[platform.machine().lower()])
    with tempfile.TemporaryDirectory() as tmp:
        stage = os.path.join(tmp, top)
        shutil.copytree(install, stage, symlinks=True)
        copy_maximize(stage, maximize)
        out = os.path.join(out_dir, top + ".tar.xz")
        with tarfile.open(out, "w:xz", preset=6) as tar:
            tar.add(stage, arcname=top)
    return out


def macos(install, maximize, out_dir):
    app = os.path.join(install, "Moritz.app")
    if not os.path.isdir(app):
        raise SystemExit("no Moritz.app in " + install)
    name = "moritz-{}-macos-{}".format(moritz_version(), ARCH[platform.machine().lower()])
    with tempfile.TemporaryDirectory() as tmp:
        stage = os.path.join(tmp, "Moritz")
        os.makedirs(stage)
        staged_app = os.path.join(stage, "Moritz.app")
        shutil.copytree(app, staged_app, symlinks=True)
        copy_maximize(os.path.join(staged_app, "Contents", "Resources"), maximize)
        os.symlink("/Applications", os.path.join(stage, "Applications"))
        # Ad hoc signature: Apple Silicon runs no unsigned code, and the copy changed the bundle.
        subprocess.run(["codesign", "--force", "--deep", "--sign", "-", staged_app], check=True)
        out = os.path.join(out_dir, name + ".dmg")
        if os.path.exists(out):
            os.remove(out)
        subprocess.run(["hdiutil", "create", "-volname", "Moritz", "-srcfolder", stage, "-ov",
                        "-format", "UDZO", out], check=True)
    return out


def main():
    install = os.path.abspath(sys.argv[1])
    maximize = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else None
    out_dir = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else os.getcwd()
    out = macos(install, maximize, out_dir) if sys.platform == "darwin" else linux(install, maximize, out_dir)
    record_checksum(out)
    print(out, round(os.path.getsize(out) / 1e6), "MB")


if __name__ == "__main__":
    main()
