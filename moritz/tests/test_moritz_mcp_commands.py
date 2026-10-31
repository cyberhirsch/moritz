# Run: moritz.exe --factory-startup -b --python moritz/tests/test_moritz_mcp_commands.py
# Moritz MCP (Seb, 2026-10-31: "make an mcp and cli for moritz too"): the add-on is built in and
# its bridge is off until turned on; the command set the MCP server and moritz-cli share works
# through Max's tools: Create with parameters, the stack by Max and Blender names, Edit Poly,
# Utilities, layers, selection sets, settings and export.
import json
import os
import tempfile

import addon_utils
import bpy

failures = []


def check(name, ok, *info):
    print("MXMC", "OK" if ok else "FAIL", name, *info, flush=True)
    if not ok:
        failures.append(name)


check("built in", addon_utils.is_builtin("moritz_mcp") and "moritz_mcp" in bpy.context.preferences.addons)
addon_utils.disable("moritz_mcp", default_set=True)
check("the user cannot disable it", "moritz_mcp" in bpy.context.preferences.addons)

import moritz_mcp  # noqa: E402
from moritz_mcp import commands, mcp_to_blender_server  # noqa: E402

prefs = bpy.context.preferences.addons["moritz_mcp"].preferences
check("the bridge is off by default", not prefs.use_server and not mcp_to_blender_server.is_running())
check("it listens on this computer only", moritz_mcp.HOST == "127.0.0.1")
check("its settings are in Preferences > System", hasattr(bpy.types, "USERPREF_PT_moritz_mcp") and
      bpy.types.USERPREF_PT_moritz_mcp.bl_context == "system")

described = commands.describe()
check("every command is described", all(c["description"] and c["input_schema"]["type"] == "object"
                                        for c in described), [c["name"] for c in described if not c["description"]])
json.dumps(described)


def run(_cmd, **params):
    result = commands.run(_cmd, params)
    if result["status"] != "ok":
        print("MXMC", _cmd, result, flush=True)
    return result


box = run("create", type="Box", position=[1, 2, 0], parameters={"Length": 2, "Height": 0.5})
check("create a Box with Max parameters", box["status"] == "ok" and box["object"]["name"].startswith("Box") and
      box["object"]["parameters"]["Length"] == 2.0 and box["object"]["location"] == [1.0, 2.0, 0.0],
      box.get("object", {}).get("parameters"))
name = box["object"]["name"]
check("its geometry counts", box["object"]["vertices"] == 8, box["object"]["vertices"])
check("Teapot and Suzanne", run("create", type="Teapot")["status"] == "ok" and
      run("create", type="Suzanne", name="Monkey")["object"]["name"] == "Monkey")
check("a shape", run("create", type="Circle", parameters={"Radius": 0.7})["object"]["type"] == "CURVE")
check("an unknown type is an error", run("create", type="Nope")["status"] == "error")
check("set_parameters", run("set_parameters", object=name, parameters={"Width": 3})["parameters"]["Width"] == 3.0)

run("add_modifier", object=name, modifier="Bend", settings={"angle": 1.0})
run("add_modifier", object=name, modifier="Subdivision Surface")
stack = [e["name"] for e in run("stack", object=name)["stack"]]
obj = bpy.data.objects[name]
check("the stack by Max and Blender names, top first", stack[-1] == "Box" and len(stack) == 3 and
      obj.modifiers[-1].type == 'SUBSURF' and obj.modifiers[-2].deform_method == 'BEND', stack)
mods = [m["name"] for m in run("modifier_list", object="Monkey")["modifiers"]]
check("the modifier list has the Max names", {"Bend", "Shell", "TurboSmooth", "Edit Poly"} <= set(mods))
check("set_modifier", run("set_modifier", object=name, modifier=obj.modifiers[-1].name,
                          settings={"levels": 2})["settings"]["levels"] == 2)
check("collapse", run("collapse", object=name)["stack"] == ["Editable Poly"] and not obj.modifiers)

check("Polygon level", run("edit_poly_level", object=name, level="4")["mode"] == 'EDIT_MESH')
sel = run("edit_poly_select", indices=[0])
check("select a polygon by index", sel["selected_polygons"] == [0], sel.get("selected_polygons"))
before = len(obj.data.polygons)
tool = run("edit_poly_tool", tool="Smart Extrude", settings={"distance": 0.3})
check("Smart Extrude", tool["status"] == "ok" and tool["polygons"] > 0, tool)
check("an unknown tool is an error", run("edit_poly_tool", tool="Teleport")["status"] == "error")
check("back to Object level", run("edit_poly_level", object=name, level="Object")["mode"] == 'OBJECT')

moved = run("transform", objects=["Monkey"], mode="MOVE", absolute=[0, 0, 3])
check("Transform Type-In", moved["objects"][0]["location"] == [0.0, 0.0, 3.0])
aligned = run("align", objects=["Monkey"], target=name, position=[True, False, False],
              current_point="PIVOT", target_point="PIVOT")
check("Align", abs(aligned["objects"][0]["location"][0] - obj.location.x) < 1e-5, aligned["objects"][0]["location"])
check("Array", len(run("array", objects=["Monkey"], count=3)["created"]) == 2)

run("move_to_layer", objects=["Monkey"], layer="Heads")
layers = run("scene_explorer")["layers"]
check("layers", any(c["name"] == "Heads" and c["objects"][0]["name"] == "Monkey" for c in layers["layers"]))
run("freeze", objects=["Monkey"])
check("freeze", bpy.data.objects["Monkey"].hide_select)
run("selection_set_create", name="Boxes", objects=[name])
check("selection sets", run("selection_sets")["sets"] == {"Boxes": [name]} and
      run("selection_set_select", name="Boxes")["selected"] == [name])

set_result = run("set_settings", keymap="Max", name_scheme="MAX")
check("keymap and names", set_result["keymap"] == "Max" and set_result["names_in_use"] == "MAX", set_result)
run("set_settings", keymap="Moritz", name_scheme="AUTO")

out = os.path.join(tempfile.mkdtemp(), "scene.obj")
check("export by extension", run("export", path=out)["status"] == "ok" and os.path.getsize(out) > 0)
max_result = run("import", path="missing.max")
try:
    bpy.ops.import_scene.max.get_rna_type()
    max_importer = True
except KeyError:
    max_importer = False
check(".max goes to the .max importer", max_importer and commands._IMPORTERS[".max"] == "import_scene.max" and
      max_result["message"].startswith("There is no file"), max_result)
check("unknown command and parameters", run("nope")["status"] == "error" and
      run("create", type="Box", colour="red")["status"] == "error")

print("MXMC FAILURES", len(failures), failures, flush=True)
