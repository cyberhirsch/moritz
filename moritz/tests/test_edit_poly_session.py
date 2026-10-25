# Run: moritz.exe --factory-startup -b --python moritz/tests/test_edit_poly_session.py
# The Edit Poly Edit Mode session (stage 3): Edit Mode on the object edits the modifier's result,
# the modifiers below are not re-applied on top, the object's own mesh stays untouched, a flush
# (as on save) writes into the modifier, and leaving Edit Mode stores offsets again for a pure
# move or a result mesh for a topology edit.
import bmesh
import bpy


def say(*a): print("MXEPS", " ".join(str(x) for x in a), flush=True)


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)


class _Eval:
    """The evaluated mesh's vertices (also in Edit Mode, where it is a BMesh wrapper)."""

    def __init__(self, obj):
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        ob_eval = obj.evaluated_get(dg)
        me = ob_eval.to_mesh()
        self.vertices = [type("V", (), {"co": v.co.copy()}) for v in me.vertices]
        ob_eval.to_mesh_clear()


def evaluated(obj):
    return _Eval(obj)


def stack_input(obj, mod):
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


def begin(obj, ep):
    src = stack_input(obj, ep)
    edited = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    # Up to and including the Edit Poly (no modifiers above in this test).
    ok = ep.session_begin(src, edited=edited)
    bpy.data.meshes.remove(edited)
    return ok, src


obj = bpy.data.objects["Cube"]
bpy.context.view_layer.objects.active = obj
disp = obj.modifiers.new("Displace", 'DISPLACE')
disp.direction = 'Z'
disp.mid_level = 0.0
disp.strength = 2.0
ep = obj.modifiers.new("Edit Poly", 'EDIT_POLY')
base_z = [v.co.z for v in obj.data.vertices]

# 1. Pure move: back to offsets on exit.
ok, src = begin(obj, ep)
check("session begins", ok and ep.is_editing and ep.edit_mode == 'TOPOLOGY', ok, ep.edit_mode)
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
bm.verts.ensure_lookup_table()
check("edit-mesh is the result", abs(bm.verts[0].co.z - (base_z[0] + 2.0)) < 1e-5,
      round(bm.verts[0].co.z, 3))
bm.verts[0].co.z += 1.0
bmesh.update_edit_mesh(obj.data)
me = evaluated(obj)
# The Displace below is already in the edit-mesh: no double displacement.
check("no double stack", abs(me.vertices[0].co.z - (base_z[0] + 3.0)) < 1e-5,
      round(me.vertices[0].co.z, 3))
# A flush (save, render) writes into the modifier, not the object's mesh.
obj.update_from_editmode()
check("flush to modifier", abs(obj.data.vertices[0].co.z - base_z[0]) < 1e-6 and
      ep.result is not None and abs(ep.result.vertices[0].co.z - (base_z[0] + 3.0)) < 1e-5,
      round(obj.data.vertices[0].co.z, 3))
bpy.ops.object.mode_set(mode='OBJECT')
me = evaluated(obj)
check("exit: deform", not ep.is_editing and ep.edit_mode == 'DEFORM' and
      abs(me.vertices[0].co.z - (base_z[0] + 3.0)) < 1e-5, ep.edit_mode, round(me.vertices[0].co.z, 3))
check("object mesh untouched", [round(v.co.z, 6) for v in obj.data.vertices] == [round(z, 6) for z in base_z])
disp.strength = 4.0
me = evaluated(obj)
check("follows below", abs(me.vertices[0].co.z - (base_z[0] + 5.0)) < 1e-5, round(me.vertices[0].co.z, 3))

# 2. Topology edit: extrude, exit keeps a result mesh that follows the stack below.
ok, src = begin(obj, ep)
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
face = max(bm.faces, key=lambda f: f.calc_center_median().z)
ret = bmesh.ops.extrude_face_region(bm, geom=[face])
new_verts = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
bmesh.ops.translate(bm, verts=new_verts, vec=(0, 0, 0.5))
bmesh.update_edit_mesh(obj.data)
check("edit mode shows 12", len(evaluated(obj).vertices) == 12)
bpy.ops.object.mode_set(mode='OBJECT')
me = evaluated(obj)
check("exit: topology", ep.edit_mode == 'TOPOLOGY' and len(me.vertices) == 12 and
      len(obj.data.vertices) == 8, ep.edit_mode, len(me.vertices), len(obj.data.vertices))
top = max(v.co.z for v in me.vertices)
disp.strength = 1.0
top2 = max(v.co.z for v in evaluated(obj).vertices)
check("topology follows below", abs((top - top2) - 3.0) < 1e-5, round(top, 3), round(top2, 3))

# 3. Plain Tab on an object without a session still edits its own mesh.
check("no session left", not ep.is_editing)
bpy.ops.object.mode_set(mode='EDIT')
check("normal edit mode", len(bmesh.from_edit_mesh(obj.data).verts) == 8)
bpy.ops.object.mode_set(mode='OBJECT')

# 4. Refusals: shared mesh.
twin = obj.copy()
bpy.context.collection.objects.link(twin)
ok = False
try:
    ok, _src = begin(obj, ep)
except RuntimeError as ex:
    say("refused:", str(ex).strip().splitlines()[-1])
check("shared mesh refused", not ok and not ep.is_editing)
bpy.data.objects.remove(twin)
