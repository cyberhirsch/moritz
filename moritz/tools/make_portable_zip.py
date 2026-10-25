# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Pack a built Moritz into a portable zip.

    python moritz/tools/make_portable_zip.py <bin/Release> [<Maximize repo>] [<out dir>]

The zip holds the program folder as built, with the Maximize add-on copied in as real files
(a junction in the build folder would otherwise end up empty or dangling) and without debug
symbols. A `portable` folder next to moritz.exe would keep settings beside the program; it is
left out so the zip uses %APPDATA%\\Moritz like an installed copy.
"""

import os
import re
import sys
import zipfile

SKIP_SUFFIXES = (".pdb", ".ilk", ".exp", ".lib")
# Build tools that land in the program folder.
SKIP_NAMES = {"datatoc.exe", "makesdna.exe", "makesrna.exe", "msgfmt.exe", "datatoc_icon.exe"}


def version(release):
    for name in os.listdir(release):
        if re.fullmatch(r"\d+\.\d+", name) and os.path.isdir(os.path.join(release, name)):
            return name
    raise SystemExit("no version folder in " + release)


def add_tree(zf, root, arc_root, skip_dirs=()):
    for dirpath, dirnames, filenames in os.walk(root):
        # Junctions and links are not followed; the add-on is added from its repository.
        dirnames[:] = [d for d in dirnames
                       if not os.path.islink(os.path.join(dirpath, d)) and
                       not _is_junction(os.path.join(dirpath, d)) and
                       os.path.join(dirpath, d) not in skip_dirs and d != "__pycache__"]
        for name in filenames:
            if name.endswith(SKIP_SUFFIXES) or name in SKIP_NAMES:
                continue
            path = os.path.join(dirpath, name)
            zf.write(path, os.path.join(arc_root, os.path.relpath(path, root)))


def _is_junction(path):
    is_junction = getattr(os.path, "isjunction", None)
    return bool(is_junction and is_junction(path))


def main():
    release = os.path.abspath(sys.argv[1])
    maximize = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else None
    out_dir = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else os.getcwd()
    ver = version(release)
    top = "moritz-{}-windows-x64".format(ver)
    out = os.path.join(out_dir, top + ".zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        add_tree(zf, release, top, skip_dirs=(os.path.join(release, "portable"),))
        if maximize:
            add_tree(zf, os.path.join(maximize, "maximize"),
                     os.path.join(top, ver, "scripts", "addons_core", "maximize"))
    print(out, round(os.path.getsize(out) / 1e6), "MB")


if __name__ == "__main__":
    main()
