# Run: moritz.exe --factory-startup -b --python moritz/tests/test_pro_optimizer_replay.py
# ProOptimizer's instant slider: on large meshes the collapse order is recorded once and each
# Vertex % replays part of it. The replay must match a direct decimation (a second Moritz run with
# MORITZ_PRO_OPTIMIZER_NO_CACHE), and changing the % must be fast. Blender's decimation is not
# bit-reproducible (stock Decimate flips between results a face apart, even in one process: costs
# tie on a symmetric mesh), so the match is the face count and the surface error, within 2%.
import hashlib
import os
import subprocess
import sys
import time

import bpy

DIRECT = os.environ.get("MORITZ_PRO_OPTIMIZER_NO_CACHE") is not None


def say(*a): print("MXPR", " ".join(str(x) for x in a), flush=True)


failures = []


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)
    if not ok:
        failures.append(name)


def digest(me):
    h = hashlib.sha1()
    for v in me.vertices:
        h.update(("%.5f %.5f %.5f;" % tuple(v.co)).encode())
    for p in me.polygons:
        h.update(str(tuple(p.vertices)).encode())
    return h.hexdigest()[:16]


def measure(me):
    """Face count and the mean distance from the sphere (the input's surface)."""
    error = sum(abs(v.co.length - 1.0) for v in me.vertices) / max(len(me.vertices), 1)
    return len(me.polygons), error


bpy.ops.wm.read_factory_settings(use_empty=True)
# 24576 faces: above the 20000 where the cache starts.
bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=96)
obj = bpy.context.active_object
obj.data.materials.append(bpy.data.materials.new("A"))
obj.data.materials.append(bpy.data.materials.new("B"))
for poly in obj.data.polygons:
    poly.material_index = 1 if poly.center.z > 0.3 else 0
mod = obj.modifiers.new("ProOptimizer", 'PRO_OPTIMIZER')
dg = bpy.context.evaluated_depsgraph_get()

results = {}
measures = {}
times = {}
for percent in (50.0, 30.0, 10.0, 30.0):
    mod.vertex_percent = percent
    obj.update_tag()
    start = time.perf_counter()
    dg.update()
    times.setdefault(percent, []).append(time.perf_counter() - start)
    me = obj.evaluated_get(dg).data
    results.setdefault(percent, []).append(digest(me))
    measures[percent] = measure(me)
say("FACES", len(obj.data.polygons), "TIMES", {k: [round(t, 3) for t in v] for k, v in times.items()})
print("MXPR_RESULT", *("%d:%.6f" % measures[p] for p in (50.0, 30.0, 10.0)), flush=True)

if not DIRECT:
    check("replay is fast", times[10.0][0] < 1.0 and times[30.0][1] < 1.0, times)
    check("the same % gives the same mesh again", results[30.0][0] == results[30.0][1], results[30.0])
    env = dict(os.environ, MORITZ_PRO_OPTIMIZER_NO_CACHE="1")
    out = subprocess.run([sys.argv[0], "--factory-startup", "-b", "--python", __file__], env=env,
                         capture_output=True, text=True).stdout
    line = next((l for l in out.splitlines() if l.startswith("MXPR_RESULT")), "")
    say("direct", line)
    direct = [tuple(float(x) for x in item.split(":")) for item in line.split()[1:]]
    ok = len(direct) == 3
    for (faces, error), percent in zip(direct, (50.0, 30.0, 10.0)):
        r_faces, r_error = measures[percent]
        ok &= abs(r_faces - faces) <= 0.02 * faces and abs(r_error - error) <= 0.02 * error + 1e-5
    check("replay matches direct decimation", ok, measures, line)
    say("FAILURES", len(failures), failures)
