# Run: moritz.exe --factory-startup -b --python moritz/tests/test_edit_poly_native.py [-- <stock blender.exe>]
# The native Edit Poly modifier: a Deform edit and a Topology edit follow the modifiers below,
# survive save and reload, and survive a round trip through a stock Blender (given after `--`):
# stock keeps the modifier, its data and the modifiers above it, and Moritz revives it.
import os
import subprocess
import sys
import tempfile

import bmesh
import bpy


def say(*a): print("MXEPN", " ".join(str(x) for x in a), flush=True)


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)


def evaluated(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    return obj.evaluated_get(dg).data


def stack_input(obj, mod):
    """The mesh coming into `mod`: evaluate with it and everything above hidden."""
    states = [(m, m.show_viewport) for m in obj.modifiers]
    hide = False
    for m in obj.modifiers:
        hide = hide or m == mod
        if hide:
            m.show_viewport = False
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    for m, v in states:
        m.show_viewport = v
    return me


obj = bpy.data.objects["Cube"]
disp = obj.modifiers.new("Displace", 'DISPLACE')
disp.strength = 0.0
disp.direction = 'Z'
disp.mid_level = 0.0
ep = obj.modifiers.new("Edit Poly", 'EDIT_POLY')
check("added", ep.type == 'EDIT_POLY' and ep.edit_mode == 'NONE', ep.type, ep.edit_mode)
check("passthrough", len(evaluated(obj).vertices) == 8)

# Deform: move vertex 0 up by 1.
src = stack_input(obj, ep)
edited = src.copy()
edited.vertices[0].co.z += 1.0
z0 = src.vertices[0].co.z
ep.store(src, edited)
me = evaluated(obj)
check("deform stored", ep.edit_mode == 'DEFORM' and abs(me.vertices[0].co.z - (z0 + 1)) < 1e-5,
      ep.edit_mode, round(me.vertices[0].co.z, 3))
disp.strength = 2.0
me = evaluated(obj)
check("deform follows below", abs(me.vertices[0].co.z - (z0 + 3)) < 1e-5, round(me.vertices[0].co.z, 3))

# Topology: extrude the top face by 0.5, with the vertex mapping.
disp.strength = 0.0
src = stack_input(obj, ep)
bm = bmesh.new()
bm.from_mesh(src)
orig = bm.verts.layers.int.new("mx_orig")
for v in bm.verts:
    v[orig] = v.index
top = max(bm.faces, key=lambda f: f.calc_center_median().z)
ret = bmesh.ops.extrude_face_region(bm, geom=[top])
new_verts = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
bmesh.ops.translate(bm, verts=new_verts, vec=(0, 0, 0.5))
edited = bpy.data.meshes.new("edited")
bm.to_mesh(edited)
bm.free()
ep.store(src, edited)
top_z = max(v.co.z for v in src.vertices)
me = evaluated(obj)
check("topology stored", ep.edit_mode == 'TOPOLOGY' and ep.result is not None and len(me.vertices) == 12,
      ep.edit_mode, len(me.vertices))
disp.strength = 2.0
me = evaluated(obj)
check("topology follows below", abs(max(v.co.z for v in me.vertices) - (top_z + 0.5 + 2.0)) < 1e-4,
      round(max(v.co.z for v in me.vertices), 3))

# A modifier above, to see that it survives stock Blender.
obj.modifiers.new("Bevel", 'BEVEL')

# Topology change below: the edit freezes with a warning, no crash.
sub = obj.modifiers.new("Subdivision", 'SUBSURF')
with bpy.context.temp_override(object=obj):
    bpy.ops.object.modifier_move_to_index(modifier=sub.name, index=0)
me = evaluated(obj)
check("topology change below", len(me.vertices) > 0, len(me.vertices))
with bpy.context.temp_override(object=obj):
    bpy.ops.object.modifier_remove(modifier=sub.name)

# Save and reload.
path = os.path.join(tempfile.gettempdir(), "mx_edit_poly_native.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
expected = len(evaluated(bpy.data.objects["Cube"]).vertices)
bpy.ops.wm.open_mainfile(filepath=path)
obj = bpy.data.objects["Cube"]
ep = obj.modifiers.get("Edit Poly")
check("reload", ep is not None and ep.type == 'EDIT_POLY' and ep.edit_mode == 'TOPOLOGY' and
      len(evaluated(obj).vertices) == expected, [m.type for m in obj.modifiers])

# Round trip through stock Blender.
stock = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else None
if stock:
    stock_path = os.path.join(tempfile.gettempdir(), "mx_edit_poly_stock.blend")
    script = os.path.join(tempfile.gettempdir(), "mx_stock_resave.py")
    with open(script, "w") as f:
        f.write(
            "import bpy\n"
            "o = bpy.data.objects['Cube']\n"
            "print('MXSTOCK', [m.type for m in o.modifiers])\n"
            "bpy.ops.wm.save_as_mainfile(filepath=%r)\n" % stock_path)
    out = subprocess.run([stock, "--factory-startup", "-b", path, "--python", script],
                         capture_output=True, text=True).stdout
    line = next((l for l in out.splitlines() if l.startswith("MXSTOCK")), "")
    say("stock sees", line)
    check("stock keeps the stack", line.count("'") == 6 and "'BEVEL'" in line, line)
    bpy.ops.wm.open_mainfile(filepath=stock_path)
    obj = bpy.data.objects["Cube"]
    ep = obj.modifiers.get("Edit Poly")
    check("revived after stock", ep is not None and ep.type == 'EDIT_POLY' and ep.edit_mode == 'TOPOLOGY' and
          len(evaluated(obj).vertices) == expected, [m.type for m in obj.modifiers])
