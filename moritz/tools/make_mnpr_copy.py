# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Copy EEVEE into the mNPR engine, renaming every name that would clash.

    python moritz/tools/make_mnpr_copy.py [--force]

Writes source/blender/draw/engines/mnpr from source/blender/draw/engines/eevee. EEVEE is only
read. Run once to start mNPR; with --force it overwrites an existing copy (losing mNPR's own
changes), which is only meant for the first prototype.
"""

import os
import re
import shutil
import sys

SOURCE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(SOURCE, "source", "blender", "draw", "engines", "eevee")
DST = os.path.join(SOURCE, "source", "blender", "draw", "engines", "mnpr")

# Not copied: GPU unit-test shaders and the shader lint target.
SKIP = re.compile(r"^(eevee_test_.*|CMakeLists\.txt|bsl_shader_linting\.cc)$")

RULES = [
    # Names generated from create-info names.
    (re.compile(r"\b(CREATE_INFO_RES_\w+?_)eevee_"), r"\1mnpr_"),
    (re.compile(r"\bDRW_engine_viewport_eevee_type\b"), "DRW_engine_viewport_mnpr_type"),
    (re.compile(r"\bGPU_MAT_EEVEE\b"), "GPU_MAT_MNPR"),
    # Files, shader and create-info names, functions.
    (re.compile(r"\beevee_"), "mnpr_"),
    # Macros, except the render pass and denoising enums that belong to DNA.
    (re.compile(r"\bEEVEE_(?!RENDER_PASS_|DENOISING_)"), "MNPR_"),
    # C++ and shader namespaces.
    (re.compile(r"\bnamespace eevee\b"), "namespace mnpr"),
    (re.compile(r"\bblender::eevee\b"), "blender::mnpr"),
    (re.compile(r"\beevee::"), "mnpr::"),
    (re.compile(r"ingroup eevee\b"), "ingroup mnpr"),
    # The engine's own identity.
    (re.compile(r'"BLENDER_EEVEE"'), '"MORITZ_MNPR"'),
    (re.compile(r'N_\("EEVEE"\)'), 'N_("mNPR")'),
    (re.compile(r'return "EEVEE";'), 'return "mNPR";'),
    (re.compile(r'CLG_LogRef Instance::log = \{"eevee"\}'), 'CLG_LogRef Instance::log = {"mnpr"}'),
]


def convert(text):
    for pattern, repl in RULES:
        text = pattern.sub(repl, text)
    return text


def main():
    if os.path.exists(DST):
        if "--force" not in sys.argv:
            raise SystemExit(DST + " exists; pass --force to overwrite")
        # Empty it but keep the folder: a shell may have it as its current directory.
        for entry in os.scandir(DST):
            if entry.is_dir():
                shutil.rmtree(entry.path)
            else:
                os.remove(entry.path)
    for dirpath, _dirnames, filenames in os.walk(SRC):
        rel = os.path.relpath(dirpath, SRC)
        out_dir = os.path.normpath(os.path.join(DST, rel))
        os.makedirs(out_dir, exist_ok=True)
        for name in filenames:
            if SKIP.match(name):
                continue
            with open(os.path.join(dirpath, name), encoding="utf-8", newline="") as f:
                text = f.read()
            out_name = re.sub(r"^eevee_", "mnpr_", name)
            with open(os.path.join(out_dir, out_name), "w", encoding="utf-8", newline="") as f:
                f.write(convert(text))
    print("wrote", DST)


if __name__ == "__main__":
    main()
