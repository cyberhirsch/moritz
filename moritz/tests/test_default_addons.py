# Run: moritz.exe --factory-startup -b --python moritz/tests/test_default_addons.py
# The .max importer is on by default (TASK.md "Bug: .max importer missing"): factory settings have
# it, and preferences without it get it at startup. Only turning it off in Preferences > Add-ons
# keeps it off.
# Runs Moritz three times with its own config folder (BLENDER_USER_CONFIG).
import os
import subprocess
import tempfile

import bpy

failures = []
MODULE = "bl_ext.system.io_scene_max"


def check(name, ok, *info):
    print("MXDA", "OK" if ok else "FAIL", name, *info, flush=True)
    if not ok:
        failures.append(name)


config = tempfile.mkdtemp(prefix="moritz_config_")
env = dict(os.environ, BLENDER_USER_CONFIG=config)


def moritz(code, factory=False):
    """Run `code` in a background Moritz with the test's config; returns its MXDA lines."""
    args = [bpy.app.binary_path, "-b"] + (["--factory-startup"] if factory else []) + ["--python-expr", code]
    out = subprocess.run(args, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                         stdin=subprocess.DEVNULL, timeout=300).stdout
    return [line[5:] for line in out.splitlines() if line.startswith("MXDA ")]


STATE = ("import bpy\n"
         "try:\n    bpy.ops.import_scene.max.get_rna_type()\n    registered = True\n"
         "except KeyError:\n    registered = False\n"
         "print('MXDA', '{:s}' in bpy.context.preferences.addons, registered, flush=True)\n").format(MODULE)

# Preferences saved without the importer (as 0.2.0 users' were, from before it was on).
lines = moritz(
    "import bpy, addon_utils\n"
    "addon_utils.disable({!r}, default_set=True)\n"
    "bpy.ops.wm.save_userpref()\n"
    "print('MXDA', 'saved', {!r} in bpy.context.preferences.addons, flush=True)\n".format(MODULE, MODULE),
    factory=True)
check("saved preferences without it", lines == ["saved False"], lines)

lines = moritz(STATE + "bpy.ops.wm.save_userpref()\n")
check("it is turned on for those preferences", lines == ["True True"], lines)

# Lost without the user turning it off (Seb's installed 0.3.0: saved by a build without the
# extension), with 0.3.0's "handed out" marker present: it comes back.
with open(os.path.join(config, "moritz_default_addons.txt"), "w", encoding="utf-8") as fh:
    fh.write(MODULE + "\n")
moritz("import bpy, addon_utils\naddon_utils.disable({!r}, default_set=True)\nbpy.ops.wm.save_userpref()\n"
       .format(MODULE))
lines = moritz(STATE)
check("lost without the user, it comes back", lines == ["True True"], lines)

# The user turns it off in Preferences > Add-ons and saves.
DISABLE = ("import bpy\nbpy.ops.preferences.addon_disable(module={!r})\nbpy.ops.wm.save_userpref()\n"
           .format(MODULE))
moritz(DISABLE)
lines = moritz(STATE)
check("turned off by the user, it stays off", lines == ["False False"], lines)
lines = moritz(STATE)
check("and stays off the next time too", lines == ["False False"], lines)

# Turned on again, then lost otherwise: handed out again.
moritz("import bpy\nbpy.ops.preferences.addon_enable(module={!r})\n".format(MODULE))
lines = moritz(STATE)
check("turned on again by the user, it is handed out again", lines == ["True True"], lines)

print("MXDA FAILURES", len(failures), failures, flush=True)
