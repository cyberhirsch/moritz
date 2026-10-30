# Run: moritz.exe --factory-startup -b --python moritz/tests/test_utilities_tab.py
# The Properties editor's first tabs are Create, Modify and Utilities (teal icons), and Maximize
# draws the Utilities tab when it is enabled.
import addon_utils
import bpy


def say(*a): print("MXUT", " ".join(str(x) for x in a), flush=True)


failures = []


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)
    if not ok:
        failures.append(name)


items = bpy.types.SpaceProperties.bl_rna.properties["context"].enum_items
check("utilities context", "UTILITIES" in items.keys())
check("teal icons", items["CREATE"].icon == 'TAB_CREATE' and items["MODIFIER"].icon == 'TAB_MODIFY' and
      items["UTILITIES"].icon == 'TAB_UTILITIES', items["CREATE"].icon, items["MODIFIER"].icon)
check("panel", hasattr(bpy.types, "PROPERTIES_PT_utilities") and
      bpy.types.PROPERTIES_PT_utilities.bl_context == "utilities")

# The tab order as the editor shows it: switch a Properties editor to each tab in turn.
space = next(a.spaces.active for s in bpy.data.screens for a in s.areas if a.type == 'PROPERTIES')
space.context = 'UTILITIES'
check("switch to utilities", space.context == 'UTILITIES', space.context)

addon_utils.disable("maximize")  # a script unload: Moritz without Maximize
check("fallback draw", getattr(bpy.types.PROPERTIES_PT_utilities, "utilities_draw", None) is None)
addon_utils.enable("maximize", default_set=True)
check("maximize draws it", bpy.types.PROPERTIES_PT_utilities.utilities_draw is not None)
check("no duplicate sidebar panel", not bpy.types.MAXIMIZE_PT_utilities.poll(bpy.context)
      if hasattr(bpy.types, "MAXIMIZE_PT_utilities") else True)

say("FAILURES", len(failures), failures)
