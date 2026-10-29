# Run: moritz.exe --factory-startup -b --python moritz/tests/test_retopology_native.py
# The native Retopology modifier (3ds Max's): quads near the face count, on the original surface,
# symmetric when asked, working on non-manifold input, kept through save and reload.
import os
import tempfile

import bmesh
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree


def say(*a): print("MXRT", " ".join(str(x) for x in a), flush=True)


failures = []


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)
    if not ok:
        failures.append(name)


def evaluated(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    obj.update_tag()
    dg.update()
    return obj.evaluated_get(dg).data


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1.0)
sphere = bpy.context.active_object
tree = BVHTree.FromObject(sphere, bpy.context.evaluated_depsgraph_get())
rt = sphere.modifiers.new("Retopology", 'RETOPOLOGY')
rt.face_count = 800
me = evaluated(sphere)
quads = sum(1 for p in me.polygons if len(p.vertices) == 4)
check("quads", quads / max(len(me.polygons), 1) > 0.95, len(me.polygons), quads)
check("near face count", 400 <= len(me.polygons) <= 1600, len(me.polygons))
far = max(tree.find_nearest(v.co)[3] for v in me.vertices)
check("on the surface", far < 0.01, round(far, 5))

rt.symmetry_axis = 'X'
me = evaluated(sphere)
kd = KDTree(len(me.vertices))
for i, v in enumerate(me.vertices):
    kd.insert(v.co, i)
kd.balance()
worst = max(kd.find((-v.co.x, v.co.y, v.co.z))[2] for v in me.vertices)
check("symmetric", worst < 1e-3, round(worst, 6), len(me.polygons))

# Non-manifold input: a cube with a fin (an edge with three faces).
bpy.ops.mesh.primitive_cube_add(location=(4, 0, 0))
fin = bpy.context.active_object
bm = bmesh.new()
bm.from_mesh(fin.data)
bm.verts.ensure_lookup_table()
e = next(e for e in bm.edges if all(v.co.z > 0 for v in e.verts))
a, b = e.verts
c = bm.verts.new(a.co + Vector((0, 0, 1)))
d = bm.verts.new(b.co + Vector((0, 0, 1)))
bm.faces.new((a, b, d, c))
bm.to_mesh(fin.data)
bm.free()
fr = fin.modifiers.new("Retopology", 'RETOPOLOGY')
fr.face_count = 300
me = evaluated(fin)
check("non-manifold input", len(me.polygons) > 50, len(me.polygons))

path = os.path.join(tempfile.gettempdir(), "mx_retopology.blend")
rt.face_count = 1234
bpy.ops.wm.save_as_mainfile(filepath=path)
bpy.ops.wm.open_mainfile(filepath=path)
rt = bpy.data.objects["Sphere"].modifiers["Retopology"]
check("reload", rt.type == 'RETOPOLOGY' and rt.face_count == 1234 and rt.symmetry_axis == 'X')

say("FAILURES", len(failures), failures)
