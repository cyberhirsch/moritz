# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Copy Moritz's Max icons (16 px SVGs drawn with CSS classes) into Blender's icon sheet.

Blender reads icons with NanoSVG, which ignores <style> rules: each element's classes are written
out as its own `style` attribute. The icons keep their own colors (white and grey on dark), so
they are color icons (`DEF_ICON_COLOR`), named `MX_<NAME>`.

    python moritz/tools/import_icons.py <folder with the SVGs> [...]

Then rebuild. Prints the lines to add to `UI_icons.hh` and `editors/datafiles/CMakeLists.txt`
when they are not there yet (and adds them).
"""

import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
ICONS = os.path.join(ROOT, "release", "datafiles", "icons_svg")
UI_ICONS = os.path.join(ROOT, "source", "blender", "editors", "include", "UI_icons.hh")
CMAKE = os.path.join(ROOT, "source", "blender", "editors", "datafiles", "CMakeLists.txt")
ANCHOR = "DEF_ICON_COLOR(TAB_UTILITIES)"
CMAKE_ANCHOR = "      tab_utilities\n"


def inline_styles(svg):
    """Move <style> class rules onto the elements that use them."""
    rules = {}
    for block in re.findall(r"<style[^>]*>(.*?)</style>", svg, re.S):
        for names, body in re.findall(r"([^{}]+)\{([^}]*)\}", block):
            for name in names.split(","):
                name = name.strip()
                if name.startswith("."):
                    rules[name[1:]] = rules.get(name[1:], "") + body.strip().rstrip(";") + ";"
    svg = re.sub(r"<style[^>]*>.*?</style>", "", svg, flags=re.S)

    def element(match):
        tag = match.group(0)
        classes = re.search(r'\sclass="([^"]*)"', tag)
        if not classes:
            return tag
        style = "".join(rules.get(c, "") for c in classes.group(1).split())
        tag = tag.replace(classes.group(0), "")
        own = re.search(r'\sstyle="([^"]*)"', tag)
        if own:
            # The element's own style comes last, so it wins over the class.
            return tag.replace(own.group(0), ' style="{}{}"'.format(style, own.group(1)))
        return re.sub(r"^<(\w+)", lambda m: '<{} style="{}"'.format(m.group(1), style), tag)

    return re.sub(r"<\w+[^>]*>", element, svg)


def main(folders):
    names = []
    for folder in folders:
        for file in sorted(os.listdir(folder)):
            if not file.endswith(".svg"):
                continue
            name = "mx_" + file[:-4].lower()
            with open(os.path.join(folder, file), encoding="utf-8") as f:
                svg = inline_styles(f.read())
            # Blender rasterizes icons as a 1600-unit canvas (`blf_glyph.cc`): scale the drawing's
            # size up, its viewBox keeps the coordinates.
            svg = re.sub(r'(<svg\b[^>]*?)\bwidth="16" height="16"', r'\1width="1600" height="1600"',
                         svg, count=1)
            with open(os.path.join(ICONS, name + ".svg"), "w", encoding="utf-8", newline="\n") as f:
                f.write(svg)
            names.append(name)
    names.sort()
    with open(UI_ICONS, encoding="utf-8") as f:
        header = f.read()
    new = [n for n in names if "DEF_ICON_COLOR({})".format(n.upper()) not in header]
    if new:
        header = header.replace(ANCHOR, ANCHOR + "".join("\nDEF_ICON_COLOR({})".format(n.upper()) for n in new), 1)
        with open(UI_ICONS, "w", encoding="utf-8", newline="\n") as f:
            f.write(header)
    with open(CMAKE, encoding="utf-8") as f:
        cmake = f.read()
    new = [n for n in names if "      {}\n".format(n) not in cmake]
    if new:
        cmake = cmake.replace(CMAKE_ANCHOR, CMAKE_ANCHOR + "".join("      {}\n".format(n) for n in new), 1)
        with open(CMAKE, "w", encoding="utf-8", newline="\n") as f:
            f.write(cmake)
    print(len(names), "icons:", " ".join(names))


if __name__ == "__main__":
    main(sys.argv[1:])
