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


SOURCE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def moritz_version():
    """Moritz's own version (the package names), not Blender's (the version folder)."""
    path = os.path.join(SOURCE, "source", "blender", "blenkernel", "BKE_moritz_version.h")
    with open(path, encoding="utf-8") as f:
        match = re.search(r'#define MORITZ_VERSION_STRING "([^"]+)"', f.read())
    return match.group(1).replace(" ", "-").lower()


def record_checksum(path):
    """Add (or replace) the package's line in SHA256SUMS.txt next to it; Moritz's updater installs
    only files listed there."""
    import hashlib
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    name = os.path.basename(path)
    sums = os.path.join(os.path.dirname(path), "SHA256SUMS.txt")
    lines = []
    if os.path.isfile(sums):
        with open(sums, encoding="utf-8") as f:
            lines = [line for line in f.read().splitlines() if line.split()[-1:] != [name]]
    lines.append("{}  {}".format(digest.hexdigest(), name))
    with open(sums, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(sorted(lines, key=lambda line: line.split()[-1])) + "\n")


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
    top = "moritz-{}-windows-x64".format(moritz_version())
    out = os.path.join(out_dir, top + ".zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        add_tree(zf, release, top, skip_dirs=(os.path.join(release, "portable"),))
        if maximize:
            add_tree(zf, os.path.join(maximize, "maximize"),
                     os.path.join(top, ver, "scripts", "addons_core", "maximize"))
    record_checksum(out)
    print(out, round(os.path.getsize(out) / 1e6), "MB")


if __name__ == "__main__":
    main()
