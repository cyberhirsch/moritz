# Run: moritz.exe --factory-startup -b --python moritz/tests/test_edit_spline_native.py
# The native Edit Spline modifier: Deform and Topology storage that follows the splines below,
# the Interpolation settings (Steps, Optimize, Adaptive), save / reload, curves only.
import os
import tempfile

import bpy
from mathutils import Vector


def say(*a): print("MXES", " ".join(str(x) for x in a), flush=True)


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)


def evaluated_curves(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    dg.update()
    geometry = obj.evaluated_get(dg).evaluated_geometry()
    return geometry, geometry.curves


def copy_curves(src, name="edited"):
    """A new Curves data-block with the points, curves and attributes of `src`."""
    dst = bpy.data.hair_curves.new(name)
    sizes = [c.points_length for c in src.curves]
    dst.add_curves(sizes)
    for attr in src.attributes:
        if attr.name.startswith("."):
            continue
        target = dst.attributes.get(attr.name) or dst.attributes.new(attr.name, attr.data_type, attr.domain)
        key = {"FLOAT_VECTOR": "vector", "FLOAT": "value", "INT": "value", "INT8": "value",
               "BOOLEAN": "value", "FLOAT_COLOR": "color"}.get(attr.data_type)
        if key is None:
            continue
        width = 3 if key == "vector" else 4 if key == "color" else 1
        values = [0] * (len(attr.data) * width)
        attr.data.foreach_get(key, values)
        target.data.foreach_set(key, values)
    return dst


def point(curves, name, i):
    return Vector(curves.attributes[name].data[i].vector)


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

mod = obj.modifiers.new("Edit Spline", 'EDIT_SPLINE')
check("added", mod is not None and mod.type == 'EDIT_SPLINE' and mod.edit_mode == 'NONE')

# Deform: knot 0 up by 1 (handles with it).
geo, inp = evaluated_curves(obj)
input_copy = copy_curves(inp, "input")
edited = copy_curves(inp)
for name in ("position", "handle_left", "handle_right"):
    edited.attributes[name].data[0].vector = point(edited, name, 0) + Vector((0, 0, 1))
# Splines are small: even a pure move keeps the edited splines (Topology), so a knot count change
# below keeps the edit visible.
check("store move", mod.store(input=input_copy, edited=edited) and mod.edit_mode == 'TOPOLOGY', mod.edit_mode)
geo, out = evaluated_curves(obj)
check("deform applied", abs(point(out, "position", 0).z - 1) < 1e-6 and abs(point(out, "handle_left", 0).z - 1) < 1e-6,
      tuple(point(out, "position", 0)))
# The splines below change: the edit follows.
sp.bezier_points[1].co.x += 0.5
obj.update_tag()
geo, out = evaluated_curves(obj)
check("deform follows below", abs(point(out, "position", 1).x - 1.5) < 1e-6 and abs(point(out, "position", 0).z - 1) < 1e-6)
sp.bezier_points[1].co.x -= 0.5
obj.update_tag()

# Topology: a new knot appended to the spline (mx_orig -1), the others mapped.
geo, inp = evaluated_curves(obj)
input_copy = copy_curves(inp, "input2")
edited = bpy.data.hair_curves.new("edited2")
edited.add_curves([4])
for name in ("position", "handle_left", "handle_right"):
    a = edited.attributes.get(name) or edited.attributes.new(name, 'FLOAT_VECTOR', 'POINT')
    for i in range(3):
        a.data[i].vector = point(inp, name, i)
    a.data[3].vector = (3, 1, 0)
edited.set_types(type='BEZIER')
for name in ("position", "handle_left", "handle_right"):
    edited.attributes[name].data[3].vector = (3, 1, 0)
orig = edited.attributes.new("mx_orig", 'INT', 'POINT')
orig.data.foreach_set("value", [0, 1, 2, -1])
check("store topology", mod.store(input=input_copy, edited=edited) and mod.edit_mode == 'TOPOLOGY', mod.edit_mode)
check("result curves", mod.result is not None and mod.result.users == 1)
geo, out = evaluated_curves(obj)
check("topology applied", len(out.points) == 4, len(out.points))
sp.bezier_points[1].co.y += 0.5
obj.update_tag()
geo, out = evaluated_curves(obj)
check("topology follows below", abs(point(out, "position", 1).y - 0.5) < 1e-6 and
      abs(point(out, "position", 3).y - 1) < 1e-6, tuple(point(out, "position", 1)))
sp.bezier_points[1].co.y -= 0.5
# A knot added below: the edit stays as it was, flagged for the add-on.
sp.bezier_points.add(1)
sp.bezier_points[-1].co = (5, 0, 0)
obj.update_tag()
geo, out = evaluated_curves(obj)
flag = out.attributes.get("mx_topology_changed")
check("frozen when knots change below", len(out.points) == 4 and flag is not None and flag.data[0].value,
      len(out.points))
curve.splines.remove(sp)
sp = curve.splines.new('BEZIER')
sp.bezier_points.add(2)
for bp, co in zip(sp.bezier_points, ((0, 0, 0), (1, 0, 0), (2, 1, 0))):
    bp.co = co
    bp.handle_left_type = bp.handle_right_type = 'FREE'
    bp.handle_left = Vector(co) - Vector((0.25, 0, 0))
    bp.handle_right = Vector(co) + Vector((0.25, 0, 0))
obj.update_tag()

# Interpolation.
mod.steps = 3
obj.update_tag()
geo, out = evaluated_curves(obj)
res = [d.value for d in out.attributes["resolution"].data] if "resolution" in out.attributes else []
check("steps", res == [4], res)
mod.steps = -1
mod.use_adaptive = True
obj.update_tag()
geo, out = evaluated_curves(obj)
res = [d.value for d in out.attributes["resolution"].data] if "resolution" in out.attributes else []
# The curved segment turns about 127 degrees: about 6 degrees per step.
check("adaptive", res and 15 <= res[0] <= 30, res)
mod.use_optimize = True
obj.update_tag()
geo, out = evaluated_curves(obj)
types = [d.value for d in out.attributes["handle_type_right"].data] if "handle_type_right" in out.attributes else []
check("optimize keeps curved segments", types and types[0] != 1, types)

# Save and reload.
path = os.path.join(tempfile.gettempdir(), "moritz_edit_spline.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)
bpy.ops.wm.open_mainfile(filepath=path)
obj = bpy.data.objects["shape"]
mod = obj.modifiers[0]
check("reload", mod.type == 'EDIT_SPLINE' and mod.edit_mode == 'TOPOLOGY' and mod.use_adaptive and
      mod.result is not None, mod.type)
geo, out = evaluated_curves(obj)
check("reload evaluates", len(out.points) == 4)

# Curves only.
bpy.ops.mesh.primitive_cube_add()
cube = bpy.context.active_object
try:
    cube.modifiers.new("x", 'EDIT_SPLINE')
    check("not on meshes", 'EDIT_SPLINE' not in [m.type for m in cube.modifiers])
except RuntimeError:
    check("not on meshes", True)
say("file", path)
say("DONE")
