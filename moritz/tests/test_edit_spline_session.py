# Run: moritz.exe --factory-startup -b --python moritz/tests/test_edit_spline_session.py
# Edit Spline stage 2: Edit Mode on the object itself edits the modifier's result; leaving writes
# the edit into the modifier, and the object's own splines stay as they were.
import bpy
from mathutils import Vector


def say(*a): print("MXSS", " ".join(str(x) for x in a), flush=True)


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)


def evaluated(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    geometry = obj.evaluated_get(dg).evaluated_geometry()
    curves = geometry.curves
    return [Vector(d.vector) for d in curves.attributes["position"].data] if curves else []


def copy_curves(src, name):
    dst = bpy.data.hair_curves.new(name)
    dst.add_curves([c.points_length for c in src.curves])
    dst.set_types(type='BEZIER')
    for attr in src.attributes:
        if attr.name.startswith(".") or attr.name == "curve_type":
            continue
        key = {"FLOAT_VECTOR": ("vector", 3), "FLOAT": ("value", 1), "INT": ("value", 1),
               "INT8": ("value", 1), "BOOLEAN": ("value", 1)}.get(attr.data_type)
        if key is None:
            continue
        target = dst.attributes.get(attr.name) or dst.attributes.new(attr.name, attr.data_type, attr.domain)
        values = [0] * (len(attr.data) * key[1])
        attr.data.foreach_get(key[0], values)
        target.data.foreach_set(key[0], values)
    return dst


for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)

curve = bpy.data.curves.new("shape", 'CURVE')
sp = curve.splines.new('BEZIER')
sp.bezier_points.add(2)
for bp, co in zip(sp.bezier_points, ((0, 0, 0), (1, 0, 0), (2, 1, 0))):
    bp.co = co
    bp.handle_left_type = bp.handle_right_type = 'FREE'
    bp.handle_left = Vector(co) - Vector((0.25, 0, 0))
    bp.handle_right = Vector(co) + Vector((0.25, 0, 0))
obj = bpy.data.objects.new("shape", curve)
bpy.context.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
mod = obj.modifiers.new("Edit Spline", 'EDIT_SPLINE')

# Begin a session with the current result (the input itself, knots mapped by index).
dg = bpy.context.evaluated_depsgraph_get()
dg.update()
geo = obj.evaluated_get(dg).evaluated_geometry()
input_curves = copy_curves(geo.curves, "input")
edited = copy_curves(geo.curves, "edited")
edited.attributes.new("mx_orig", 'INT', 'POINT').data.foreach_set("value", [0, 1, 2])
check("session begin", mod.session_begin(input=input_curves, edited=edited) and mod.is_editing)

bpy.ops.object.mode_set(mode='EDIT')
pts = curve.splines[0].bezier_points
check("edit mode shows the result", len(pts) == 3 and (pts[2].co - Vector((2, 1, 0))).length < 1e-6)
# Move knot 1 up; add a knot as a new spline.
for name in ("co", "handle_left", "handle_right"):
    setattr(pts[1], name, getattr(pts[1], name) + Vector((0, 0, 1)))
extra = curve.splines.new('POLY')
extra.points[0].co = (5, 5, 0, 1)
check("edit mode evaluates the edit", any(abs(p.z - 1) < 1e-6 for p in evaluated(obj)))
bpy.ops.object.mode_set(mode='OBJECT')

check("session ended", not mod.is_editing)
check("object's own splines unchanged", len(curve.splines) == 1 and abs(curve.splines[0].bezier_points[1].co.z) < 1e-6,
      len(curve.splines))
out = evaluated(obj)
check("result has the edit", len(out) == 4 and abs(out[1].z - 1) < 1e-6 and (out[3] - Vector((5, 5, 0))).length < 1e-6,
      [tuple(p) for p in out])
orig = [d.value for d in mod.result.attributes["mx_orig"].data]
check("knots mapped, the new one not", orig == [0, 1, 2, -1], orig)

# The splines below change: the edited knots follow, the new knot stays.
curve.splines[0].bezier_points[2].co.x += 1
obj.update_tag()
out = evaluated(obj)
check("follows below", abs(out[2].x - 3) < 1e-6 and abs(out[1].z - 1) < 1e-6 and
      (out[3] - Vector((5, 5, 0))).length < 1e-6, [tuple(p) for p in out])

# Sessions need Object Mode.
bpy.ops.object.mode_set(mode='EDIT')
try:
    ok = mod.session_begin(input=input_curves, edited=edited)
except RuntimeError:
    ok = False
check("no session from Edit Mode", not ok)
bpy.ops.object.mode_set(mode='OBJECT')
say("DONE")
