# Run: moritz.exe --factory-startup -b --python moritz/tests/test_command_panel.py
# The Properties editor as Max's Command Panel: renamed labels, the Create tab with its object types,
# the Modify tab's stack list, the Maximize hooks, and a file saved on the Create tab.
import os
import tempfile

import addon_utils
import bpy

from bl_ui import properties_create


def say(*a): print("MXCMD", " ".join(str(x) for x in a), flush=True)


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)


space_types = bpy.types.Space.bl_rna.properties["type"].enum_items
check("editor renamed", space_types["PROPERTIES"].name == "Command Panel", space_types["PROPERTIES"].name)
tabs = bpy.types.SpaceProperties.bl_rna.properties["context"].enum_items_static
check("Create tab", "CREATE" in tabs.keys() and tabs["CREATE"].name == "Create")
check("Modify tab", tabs["MODIFIER"].name == "Modify", tabs["MODIFIER"].name)
check("Create filter", hasattr(bpy.types.SpaceProperties, "show_properties_create") or
      "show_properties_create" in bpy.types.SpaceProperties.bl_rna.properties.keys())

# Every object type of the Create tab is a valid operator call.
addon_utils.disable("maximize", default_set=True)
check("no hook without Maximize", bpy.types.PROPERTIES_PT_create.object_type_draw is None)
before = len(bpy.data.objects)
bad = []
for category, items in properties_create.OBJECT_TYPES.items():
    for idname, text, _icon, props in items:
        if idname == "object.empty_image_add":
            continue  # Needs an image file.
        module, name = idname.split(".")
        try:
            getattr(getattr(bpy.ops, module), name)(**props)
        except Exception as ex:
            bad.append((category, text, str(ex).splitlines()[0]))
        if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
check("object types create", not bad and len(bpy.data.objects) > before, bad)

# The Modify tab's stack: newest modifier first, the selection is the active modifier.
bpy.ops.mesh.primitive_cube_add()
ob = bpy.context.object
for kind in ('BEVEL', 'SUBSURF', 'ARRAY'):
    ob.modifiers.new(kind.title(), kind)
ob.moritz_modifier_stack_index = 0
check("stack index sets active", ob.modifiers.active == ob.modifiers[0], ob.modifiers.active.name)
ob.modifiers.active = ob.modifiers[2]
check("stack index reads active", ob.moritz_modifier_stack_index == 2)
check("stack index not stored", "moritz_modifier_stack_index" not in ob.keys())

# Maximize fills the Create tab with its parametric objects while it is enabled.
addon_utils.enable("maximize", default_set=True)
from maximize import ui as max_ui  # noqa: E402
check("hook with Maximize", bpy.types.PROPERTIES_PT_create.object_type_draw is max_ui.draw_object_types)
check("sidebar Create hidden", not max_ui.MAXIMIZE_PT_create.poll(bpy.context))
addon_utils.disable("maximize", default_set=True)
check("hook removed", bpy.types.PROPERTIES_PT_create.object_type_draw is None)

# A file saved with the Create tab open. Stock Blender falls back to the Object tab for the unknown
# tab number: open the printed file there with
# blender.exe -b <file> --python-expr "import bpy; print([a.spaces.active.context for a in bpy.data.screens['Layout'].areas if a.type == 'PROPERTIES'])"
props_space = None
for area in bpy.data.screens["Layout"].areas:
    if area.type == 'PROPERTIES':
        props_space = area.spaces.active
props_space.context = 'CREATE'
check("Create tab set", props_space.context == 'CREATE')
path = os.path.join(tempfile.gettempdir(), "moritz_command_panel.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
bpy.ops.wm.open_mainfile(filepath=path)
saved = [a.spaces.active.context for a in bpy.data.screens["Layout"].areas if a.type == 'PROPERTIES']
check("Create tab saved", saved == ['CREATE'], saved)
say("file", path)
