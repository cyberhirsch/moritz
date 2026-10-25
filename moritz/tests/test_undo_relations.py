# Run: moritz.exe --factory-startup --python moritz/tests/test_undo_relations.py
# (needs a window; with MORITZ_UNDO_TIMING=1 the undo phases are printed, including
# "relations kept" when the depsgraph relations were not rebuilt).
# Undo must give the right evaluated scene whether or not the relations are rebuilt: a move
# (relations kept), a parent change and a modifier change (relations rebuilt).
import bpy


def say(*a): print("MXUR", " ".join(str(x) for x in a), flush=True)


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)


def ev(obj):
    dg = bpy.context.evaluated_depsgraph_get()
    return obj.evaluated_get(dg)


def run():
    w = bpy.context.window_manager.windows[0]
    v = next(a for a in w.screen.areas if a.type == 'VIEW_3D')
    region = [r for r in v.regions if r.type == 'WINDOW'][0]
    with bpy.context.temp_override(window=w, area=v, region=region):
        cube = bpy.data.objects["Cube"]
        empty = bpy.data.objects.new("Pivot", None)
        bpy.context.collection.objects.link(empty)
        empty.location = (0, 0, 5)
        bpy.ops.ed.undo_push(message="setup")

        # 1. Move: relations kept.
        cube.location.x = 3.0
        bpy.ops.ed.undo_push(message="move")
        bpy.ops.ed.undo()
        cube = bpy.data.objects["Cube"]
        check("undo move", abs(ev(cube).matrix_world.translation.x) < 1e-6,
              tuple(round(c, 3) for c in ev(cube).matrix_world.translation))
        bpy.ops.ed.redo()
        cube = bpy.data.objects["Cube"]
        check("redo move", abs(ev(cube).matrix_world.translation.x - 3.0) < 1e-6)

        # 2. Parent: relations change.
        empty = bpy.data.objects["Pivot"]
        cube.parent = empty
        bpy.ops.ed.undo_push(message="parent")
        empty.location.z = 10.0
        bpy.ops.ed.undo_push(message="move parent")
        check("child follows parent", abs(ev(cube).matrix_world.translation.z - 10.0) < 1e-6,
              round(ev(cube).matrix_world.translation.z, 3))
        bpy.ops.ed.undo()
        bpy.ops.ed.undo()
        cube = bpy.data.objects["Cube"]
        empty = bpy.data.objects["Pivot"]
        check("undo parent", cube.parent is None and abs(ev(cube).matrix_world.translation.z) < 1e-6,
              cube.parent, round(ev(cube).matrix_world.translation.z, 3))
        # Moving the former parent must not move the cube: its old relation is gone.
        empty.location.z = 20.0
        bpy.ops.ed.undo_push(message="move pivot")
        check("no stale relation", abs(ev(cube).matrix_world.translation.z) < 1e-6,
              round(ev(cube).matrix_world.translation.z, 3))

        # 3. Modifier: relations and geometry change.
        n = len(ev(cube).data.vertices)
        cube.modifiers.new("Sub", 'SUBSURF')
        bpy.ops.ed.undo_push(message="modifier")
        n_sub = len(ev(cube).data.vertices)
        bpy.ops.ed.undo()
        cube = bpy.data.objects["Cube"]
        check("undo modifier", len(cube.modifiers) == 0 and len(ev(cube).data.vertices) == n, n, n_sub)
        bpy.ops.ed.redo()
        cube = bpy.data.objects["Cube"]
        check("redo modifier", len(ev(cube).data.vertices) == n_sub, n_sub)

        # 4. Many moves back and forth.
        for i in range(5):
            cube.location.y = i
            bpy.ops.ed.undo_push(message="y")
        for _ in range(4):
            bpy.ops.ed.undo()
        cube = bpy.data.objects["Cube"]
        check("undo chain", abs(ev(cube).matrix_world.translation.y) < 1e-6,
              round(ev(cube).matrix_world.translation.y, 3))
    bpy.ops.wm.quit_blender()


bpy.app.timers.register(run, first_interval=2)
