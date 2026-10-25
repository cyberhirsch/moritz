# Run: moritz.exe --factory-startup --python moritz/tests/test_tabs_multi.py
# Several tabs of one editor type: duplicate the Outliner as a tab, give the copy its own
# display mode, switch between the two by position, close one.
import bpy


def say(*a): print("MXTM", " ".join(str(x) for x in a), flush=True)


def check(name, ok, *info):
    say("OK" if ok else "FAIL", name, *info)


def outliner():
    return next(a for a in bpy.context.window_manager.windows[0].screen.areas if a.type == 'OUTLINER')


def run():
    w = bpy.context.window_manager.windows[0]
    area = outliner()
    with bpy.context.temp_override(window=w, area=area):
        check("duplicate", bpy.ops.screen.area_tab_duplicate() == {'FINISHED'})
    check("two outliners", [s.type for s in area.spaces][:2] == ['OUTLINER', 'OUTLINER'],
          [s.type for s in area.spaces])
    copy = area.spaces.active
    copy.display_mode = 'ORPHAN_DATA'
    first = area.spaces[1]
    check("independent spaces", first.display_mode == 'VIEW_LAYER' and copy != first,
          first.display_mode, copy.display_mode)

    with bpy.context.temp_override(window=w, area=area):
        check("activate tab 1", bpy.ops.screen.area_tab_activate(tab=1) == {'FINISHED'})
    check("first is active", area.spaces.active.display_mode == 'VIEW_LAYER',
          area.spaces.active.display_mode)
    # Drawing both after switching must not fail (regions swapped with the right space).
    with bpy.context.temp_override(window=w):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=1)
    with bpy.context.temp_override(window=w, area=area):
        bpy.ops.screen.area_tab_activate(tab=2)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=1)
    check("second is active", area.spaces.active.display_mode == 'ORPHAN_DATA')

    with bpy.context.temp_override(window=w, area=area):
        check("close tab 1", bpy.ops.screen.area_tab_close(tab=1) == {'FINISHED'})
    outl = [s for s in area.spaces if s.type == 'OUTLINER']
    check("one left", len(outl) == 1 and area.spaces.active.display_mode == 'ORPHAN_DATA',
          len(outl), area.spaces.active.display_mode)
    with bpy.context.temp_override(window=w):
        bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=1)

    # The same with the 3D view, whose regions (tool settings, sidebar) are the most involved.
    v3d = next(a for a in w.screen.areas if a.type == 'VIEW_3D')
    with bpy.context.temp_override(window=w, area=v3d):
        bpy.ops.screen.area_tab_duplicate()
    v3d.spaces.active.shading.type = 'WIREFRAME'
    with bpy.context.temp_override(window=w, area=v3d):
        bpy.ops.screen.area_tab_activate(tab=1)
        bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=1)
    check("3D views independent", v3d.spaces.active.shading.type == 'SOLID',
          v3d.spaces.active.shading.type)
    bpy.ops.wm.quit_blender()


bpy.app.timers.register(run, first_interval=2)
