# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Make every UI check that accepts EEVEE accept mNPR too.

    python moritz/tools/add_mnpr_to_ui.py <file or folder> ...

Adds 'MORITZ_MNPR' next to 'BLENDER_EEVEE' in set literals (COMPAT_ENGINES and similar), and turns
`== 'BLENDER_EEVEE'` / `!= 'BLENDER_EEVEE'` into set tests. Assignments are left alone. Running it
again changes nothing.
"""

import os
import re
import sys

TOKEN = "'BLENDER_EEVEE'"
NEW = "'MORITZ_MNPR'"
CLOSE = {")": "(", "]": "[", "}": "{"}


def enclosing_bracket(text, pos):
    depth = []
    i = pos - 1
    while i >= 0:
        c = text[i]
        if c in ")]}":
            depth.append(c)
        elif c in "([{":
            if not depth:
                return c
            depth.pop()
        elif c == "\n" and text[i + 1:pos].lstrip().startswith(("class ", "def ")):
            return None
        i -= 1
    return None


def convert(text):
    text = re.sub(r"!=\s*'BLENDER_EEVEE'", "not in {'BLENDER_EEVEE', 'MORITZ_MNPR'}", text)
    text = re.sub(r"==\s*'BLENDER_EEVEE'", "in {'BLENDER_EEVEE', 'MORITZ_MNPR'}", text)
    out = []
    last = 0
    for m in re.finditer(re.escape(TOKEN), text):
        start, end = m.span()
        rest = text[end:]
        if rest.lstrip(", \t\r\n").startswith(NEW) or rest.lstrip(" \t").startswith(":"):
            continue
        if enclosing_bracket(text, start) != "{":
            continue
        out.append(text[last:end])
        line_start = text.rfind("\n", 0, start) + 1
        prefix = text[line_start:start]
        if prefix.strip() == "" and rest.startswith(","):
            # One item per line: add a line below.
            nl = "\r\n" if "\r\n" in text else "\n"
            out.append("," + nl + prefix + NEW)
        else:
            out.append(", " + NEW)
        last = end
    out.append(text[last:])
    return "".join(out)


def main():
    for arg in sys.argv[1:]:
        paths = [arg] if os.path.isfile(arg) else [
            os.path.join(d, f) for d, _, fs in os.walk(arg) for f in fs if f.endswith(".py")]
        for path in paths:
            with open(path, encoding="utf-8", newline="") as f:
                text = f.read()
            if TOKEN not in text:
                continue
            new = convert(text)
            if new != text:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new)
                print("changed", path)


if __name__ == "__main__":
    main()
