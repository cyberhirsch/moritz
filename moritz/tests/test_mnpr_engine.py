# Run: moritz.exe --factory-startup -b --python moritz/tests/test_mnpr_engine.py
# mNPR is a renamed copy of EEVEE (moritz/tools/make_mnpr_copy.py) with painted strokes on top.
# With strokes off it must render what EEVEE renders; with strokes on it must differ. Every EEVEE
# panel must show for it.
# MX_SHOT=<folder> keeps the three renders there.
import os
import tempfile

import bpy

failures = []


def check(name, ok, *info):
    print("MXNPR", "OK" if ok else "FAIL", name, *info, flush=True)
    if not ok:
        failures.append(name)


scene = bpy.context.scene
# The engine enum is dynamic; in background mode its static items list only EEVEE, so set it.
scene.render.engine = 'MORITZ_MNPR'
check("engine can be chosen", scene.render.engine == 'MORITZ_MNPR', scene.render.engine)

panels = [cls for cls in bpy.types.Panel.__subclasses__()
          if "BLENDER_EEVEE" in getattr(cls, "COMPAT_ENGINES", ())]
missing = [cls.__name__ for cls in panels if "MORITZ_MNPR" not in cls.COMPAT_ENGINES]
check("EEVEE panels accept mNPR", panels and not missing, len(panels), missing[:5])

out_dir = os.environ.get("MX_SHOT") or tempfile.mkdtemp(prefix="moritz_mnpr_")
scene.render.resolution_x = 160
scene.render.resolution_y = 120
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 4
scene.render.image_settings.file_format = 'PNG'


def render(engine, name):
    scene.render.engine = engine
    path = os.path.join(out_dir, name + ".png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    pixels = list(image.pixels)
    bpy.data.images.remove(image)
    return path, pixels


def max_diff(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


check("strokes on by default", scene.mnpr_use_strokes)
eevee_path, eevee_px = render('BLENDER_EEVEE', "eevee")
scene.mnpr_use_strokes = False
plain_path, plain_px = render('MORITZ_MNPR', "mnpr_plain")
scene.mnpr_use_strokes = True
scene.mnpr_stroke_size = 0.3
stroke_path, stroke_px = render('MORITZ_MNPR', "mnpr_strokes")

check("mNPR wrote images", len(plain_px) == len(eevee_px) == len(stroke_px) and eevee_px, plain_path)
if len(plain_px) == len(eevee_px) == len(stroke_px) and eevee_px:
    lit = sum(1 for i in range(0, len(plain_px), 4) if max(plain_px[i:i + 3]) > 0.05)
    check("mNPR renders the scene", lit > 1000, lit, "lit pixels")
    check("mNPR without strokes matches EEVEE", max_diff(eevee_px, plain_px) < 0.02,
          round(max_diff(eevee_px, plain_px), 4))
    changed = sum(1 for x, y in zip(plain_px, stroke_px) if abs(x - y) > 0.02)
    check("strokes change the shading", changed > 500, changed, "channels changed")

print("MXNPR images in", out_dir)
print("MXNPR FAILURES", len(failures), failures, flush=True)
