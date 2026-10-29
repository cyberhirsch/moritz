# Run: moritz.exe --factory-startup -b --python moritz/tests/test_max_mesh_native.py [-- <stock blender.exe>]
# Max's native mesh modifiers: Cap Holes, Normal, Mesh Clean, Quadify Mesh, ProOptimizer and
# VertexPaint. Each changes the mesh as Max's does, keeps its settings through save and reload, and
# survives a round trip through a stock Blender (given after `--`), which keeps them as "None".
import os
import subprocess
import sys
import tempfile

import bmesh
import bpy
from mathutils import Vector


def say(*a): print("MXMMN", " ".join(str(x) for x in a), flush=True)


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


def boundary_edges(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    n = sum(1 for e in bm.edges if e.is_boundary)
    bm.free()
    return n


def fresh(name, add, **kw):
    add(**kw)
    obj = bpy.context.active_object
    obj.name = name
    return obj


def remove_faces(obj, test):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if test(f)], context='FACES_ONLY')
    bm.to_mesh(obj.data)
    bm.free()


bpy.ops.wm.read_factory_settings(use_empty=True)
types = {it.identifier for it in bpy.types.Modifier.bl_rna.properties["type"].enum_items}
check("types exist", {'CAP_HOLES', 'MAX_NORMAL', 'MESH_CLEAN', 'QUADIFY_MESH', 'PRO_OPTIMIZER',
                      'VERTEX_PAINT'} <= types)

# Cap Holes: an open cylinder gets both ends closed, with quads or one polygon.
cyl = fresh("Cyl", bpy.ops.mesh.primitive_cylinder_add, vertices=32, end_fill_type='NOTHING')
cap = cyl.modifiers.new("Cap Holes", 'CAP_HOLES')
me = evaluated(cyl)
check("cap quads closes", boundary_edges(me) == 0, boundary_edges(me))
check("cap quads are quads", all(len(p.vertices) == 4 for p in me.polygons),
      sorted({len(p.vertices) for p in me.polygons}))
cap.use_quad_cap = False
me = evaluated(cyl)
check("cap ngon", boundary_edges(me) == 0 and len(me.polygons) == 34, len(me.polygons))

# Odd border: a 7-sided hole still closes with quads.
odd = fresh("Odd", bpy.ops.mesh.primitive_cylinder_add, vertices=7, end_fill_type='NOTHING')
odd.modifiers.new("Cap Holes", 'CAP_HOLES')
me = evaluated(odd)
check("cap odd closes", boundary_edges(me) == 0, len(me.vertices), boundary_edges(me))


def outward(me):
    c = sum((v.co for v in me.vertices), Vector()) / len(me.vertices)
    return sum(1 for p in me.polygons if p.normal.dot(p.center - c) > 0)


# Normal: Flip turns a cube inside out; Unify repairs a cube with flipped faces.
cube = fresh("NCube", bpy.ops.mesh.primitive_cube_add)
nm = cube.modifiers.new("Normal", 'MAX_NORMAL')
nm.use_unify = False
nm.use_flip = True
check("normal flip", outward(evaluated(cube)) == 0)
bm = bmesh.new()
bm.from_mesh(cube.data)
bmesh.ops.reverse_faces(bm, faces=bm.faces[:3])
bm.to_mesh(cube.data)
bm.free()
nm.use_flip = False
nm.use_unify = True
check("normal unify", outward(evaluated(cube)) == 6, outward(evaluated(cube)))

# Mesh Clean: straight two-edge vertices, doubles and a loose vertex go.
grid = fresh("Clean", bpy.ops.mesh.primitive_plane_add)
bm = bmesh.new()
bm.from_mesh(grid.data)
bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3)
bm.verts.new((5, 5, 0))
bm.verts.ensure_lookup_table()
bmesh.ops.duplicate(bm, geom=[bm.verts[0]])
bm.to_mesh(grid.data)
bm.free()
grid.modifiers.new("Mesh Clean", 'MESH_CLEAN')
me = evaluated(grid)
check("clean", len(me.vertices) == 4 and len(me.polygons) == 1, len(me.vertices))

# Quadify Mesh: a sphere becomes quads.
sph = fresh("Quad", bpy.ops.mesh.primitive_ico_sphere_add, subdivisions=3)
qm = sph.modifiers.new("Quadify Mesh", 'QUADIFY_MESH')
qm.quad_size = 10.0
me = evaluated(sph)
quads = sum(1 for p in me.polygons if len(p.vertices) == 4)
check("quadify", len(me.polygons) > 20 and quads / len(me.polygons) > 0.9, len(me.polygons), quads)

# ProOptimizer: half the vertices, the open border kept.
plane = fresh("Opt", bpy.ops.mesh.primitive_grid_add, x_subdivisions=20, y_subdivisions=20)
bm = bmesh.new()
bm.from_mesh(plane.data)
for v in bm.verts:
    v.co.z = 0.1 * ((v.co.x * 7.3) % 1.0) * ((v.co.y * 3.1) % 1.0)
bm.to_mesh(plane.data)
bm.free()
before = len(plane.data.vertices)
border = boundary_edges(plane.data)
po = plane.modifiers.new("ProOptimizer", 'PRO_OPTIMIZER')
po.vertex_percent = 50.0
me = evaluated(plane)
check("optimizer halves", 0.4 * before <= len(me.vertices) <= 0.6 * before, before, len(me.vertices))
check("optimizer keeps border", boundary_edges(me) == border, border, boundary_edges(me))

# VertexPaint: stores the painted colors, which outlive the mesh's own attribute.
vp_obj = fresh("Paint", bpy.ops.mesh.primitive_cube_add)
attr = vp_obj.data.color_attributes.new("Col", 'FLOAT_COLOR', 'POINT')
vp_obj.data.color_attributes.active_color = attr
for i, c in enumerate(attr.data):
    c.color = (i / 8, 0.5, 1.0 - i / 8, 1.0)
vp = vp_obj.modifiers.new("VertexPaint", 'VERTEX_PAINT')
check("vertex paint empty", not vp.has_colors)
check("vertex paint store", vp.store(mesh=vp_obj.data) and vp.has_colors)
vp_obj.data.color_attributes.remove(vp_obj.data.color_attributes["Col"])
me = evaluated(vp_obj)
out = me.color_attributes.get("VertexPaint")
check("vertex paint writes", out is not None and abs(out.data[3].color[0] - 3 / 8) < 1e-5)

# Save and reload: types and settings stay.
path = os.path.join(tempfile.gettempdir(), "mx_max_mesh_native.blend")
po.vertex_percent = 30.0
po.symmetry_axis = 'X'
bpy.ops.wm.save_as_mainfile(filepath=path)
bpy.ops.wm.open_mainfile(filepath=path)
po = bpy.data.objects["Opt"].modifiers["ProOptimizer"]
check("reload type", po.type == 'PRO_OPTIMIZER')
check("reload settings", abs(po.vertex_percent - 30.0) < 1e-4 and po.symmetry_axis == 'X')
check("reload colors", bpy.data.objects["Paint"].modifiers["VertexPaint"].has_colors)

# Stock Blender keeps them as "None" modifiers, and Moritz revives them.
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if argv:
    stock = argv[0]
    stock_path = os.path.join(tempfile.gettempdir(), "mx_max_mesh_stock.blend")
    script = os.path.join(tempfile.gettempdir(), "mx_max_mesh_stock.py")
    with open(script, "w") as f:
        f.write("import bpy\n"
                "print('MXSTOCK', [m.type for o in bpy.data.objects for m in o.modifiers])\n"
                "bpy.ops.wm.save_as_mainfile(filepath=%r)\n" % stock_path)
    out = subprocess.run([stock, "--factory-startup", "-b", path, "--python", script],
                         capture_output=True, text=True).stdout
    say("stock sees", next((l for l in out.splitlines() if l.startswith("MXSTOCK")), ""))
    bpy.ops.wm.open_mainfile(filepath=stock_path)
    got = {m.type for o in bpy.data.objects for m in o.modifiers}
    check("revived after stock", {'CAP_HOLES', 'MAX_NORMAL', 'MESH_CLEAN', 'QUADIFY_MESH',
                                  'PRO_OPTIMIZER', 'VERTEX_PAINT'} <= got, got)
    po = bpy.data.objects["Opt"].modifiers["ProOptimizer"]
    check("settings after stock", abs(po.vertex_percent - 30.0) < 1e-4)

say("FAILURES", len(failures), failures)
