# Run: moritz.exe --factory-startup -b --python moritz/tests/test_modifier_stack.py
# Max-style stack: only the selected modifier open, Copy / Paste Instanced / Make Unique, Off in Renderer.
import bpy
def check(n, ok, *i): print("MXST", "OK" if ok else "FAIL", n, *i, flush=True)
ctx = bpy.context
a = bpy.data.objects["Cube"]
bpy.ops.mesh.primitive_uv_sphere_add()
b = ctx.active_object
ctx.view_layer.objects.active = a
m1 = a.modifiers.new("Bevel", 'BEVEL')
m2 = a.modifiers.new("Wave", 'WAVE')
a.moritz_modifier_stack_index = 0
check("only selected expanded", m1.show_expanded and not m2.show_expanded)
a.modifiers.active = m1
with ctx.temp_override(object=a, active_object=a):
    bpy.ops.object.moritz_modifier_copy()
ctx.view_layer.objects.active = b
with ctx.temp_override(object=b, active_object=b):
    r = bpy.ops.object.moritz_modifier_paste(instanced=True)
check("paste", r == {'FINISHED'} and len(b.modifiers) == 1 and b.modifiers[0].type == 'BEVEL', [m.name for m in b.modifiers])
check("linked", "mx_modifier_links" in a and "mx_modifier_links" in b)
m1.width = 0.37
ctx.view_layer.update()
import bl_operators.moritz_modifier_stack as st
st._sync_links(ctx.scene)
check("synced", abs(b.modifiers[0].width - 0.37) < 1e-6, b.modifiers[0].width)
with ctx.temp_override(object=b, active_object=b):
    bpy.ops.object.moritz_modifier_make_unique()
check("unique", "mx_modifier_links" not in b and "mx_modifier_links" not in a)
m1.width = 0.1
st._sync_links(ctx.scene)
check("not synced after unique", abs(b.modifiers[0].width - 0.37) < 1e-6)
with ctx.temp_override(object=a, active_object=a):
    bpy.ops.object.moritz_modifier_toggle(target='RENDER')
check("off in renderer", not a.modifiers.active.show_render)
print("MXST DONE")
