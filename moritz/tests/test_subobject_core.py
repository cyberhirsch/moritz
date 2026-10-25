# Run: moritz.exe --factory-startup -b --python moritz/tests/test_subobject_core.py
# Max's sub-object levels without the Maximize add-on: the Max keymap binds 1-6 to the core's
# object.subobject_level, which enters Edit Mode with the matching select mode, and goes back to the
# object on 6 or on the key of the current level.
import addon_utils
import bpy

addon_utils.disable("maximize", default_set=True)


def say(*a): print("MXSUB", " ".join(str(x) for x in a), flush=True)


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)


check("add-on off", not hasattr(bpy.types, "MAXIMIZE_OT_subobject"))
kc = bpy.context.window_manager.keyconfigs
bpy.ops.preferences.keyconfig_activate(filepath=bpy.utils.preset_find("Max", "keyconfig"))
km = kc.active.keymaps.get("Object Mode")
bound = {kmi.type: kmi.properties.level for kmi in km.keymap_items if kmi.idname == "object.subobject_level"}
check("keys bound", bound.get('ONE') == 'VERTEX' and bound.get('FOUR') == 'POLYGON' and bound.get('FIVE') == 'ELEMENT',
      bound)
mesh_km = kc.active.keymaps.get("Mesh")
six = [kmi for kmi in mesh_km.keymap_items if kmi.idname == "object.subobject_level" and kmi.type == 'SIX']
check("6 back to object", bool(six) and six[0].properties.level == 'OBJECT')

obj = bpy.data.objects["Cube"]
bpy.context.view_layer.objects.active = obj
ts = bpy.context.tool_settings
bpy.ops.object.subobject_level(level='EDGE')
check("2 edge", obj.mode == 'EDIT' and tuple(ts.mesh_select_mode) == (False, True, False))
bpy.ops.object.subobject_level(level='POLYGON')
check("4 polygon", tuple(ts.mesh_select_mode) == (False, False, True))
bpy.ops.object.subobject_level(level='POLYGON')
check("same key leaves", obj.mode == 'OBJECT')
bpy.ops.object.subobject_level(level='ELEMENT')
check("5 element as polygon", obj.mode == 'EDIT' and tuple(ts.mesh_select_mode) == (False, False, True))
bpy.ops.object.subobject_level(level='OBJECT')
check("6 object", obj.mode == 'OBJECT')
