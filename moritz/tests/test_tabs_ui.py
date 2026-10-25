# Run: moritz.exe --factory-startup --enable-event-simulate --python moritz/tests/test_tabs_ui.py
# Dock the Timeline onto the Properties editor as a tab (dragging empty header space), check the
# tab order, then drag the Timeline tab itself out to the 3D view's right edge.
# Screenshots go to the system temp folder.
import bpy, os, tempfile
OUT = tempfile.gettempdir()
def log(*a): print("MXT", *a, flush=True)
win = None

def areas():
    return {a.type: a for a in bpy.context.window_manager.windows[0].screen.areas}

def shot(name):
    w = bpy.context.window_manager.windows[0]
    with bpy.context.temp_override(window=w):
        bpy.ops.screen.screenshot(filepath=os.path.join(OUT, name))

def header_xy(a):
    h = next(r for r in a.regions if r.type == 'HEADER')
    return h.x + int(h.width * 0.62), h.y + h.height // 2

def setup():
    global win
    win = bpy.context.window_manager.windows[0]
    bpy.ops.mesh.primitive_monkey_add(location=(2.5, 0, 0))
    m = bpy.context.active_object
    m.hide_select = True
    a = areas()['VIEW_3D']
    a.spaces.active.shading.color_type = 'OBJECT'
    for o in bpy.data.objects:
        o.color = (1, 0.2, 0.2, 1)
    log("areas", [x.type for x in win.screen.areas])
    # Close the splash, which takes the first click.
    win.event_simulate(type='MOUSEMOVE', value='NOTHING', x=200, y=600)
    win.event_simulate(type='ESC', value='PRESS', x=200, y=600)
    win.event_simulate(type='ESC', value='RELEASE', x=200, y=600)
    return None

seq = []
def drag(src, dst, steps=12):
    (x0, y0), (x1, y1) = src, dst
    seq.append(('MOUSEMOVE', 'NOTHING', x0, y0))
    seq.append(('LEFTMOUSE', 'PRESS', x0, y0))
    for i in (3, 6, 9, 12):
        seq.append(('MOUSEMOVE', 'NOTHING', x0 + i, y0))
    for i in range(1, steps + 1):
        seq.append(('MOUSEMOVE', 'NOTHING', x0 + (x1 - x0) * i // steps, y0 + (y1 - y0) * i // steps))
    seq.append(('LEFTMOUSE', 'RELEASE', x1, y1))

def plan1():
    a = areas()
    # Timeline header onto the Properties center: stacks as a tab.
    p = a['PROPERTIES']
    log("from", header_xy(a['DOPESHEET_EDITOR']))
    drag(header_xy(a['DOPESHEET_EDITOR']), (p.x + p.width // 2, p.y + p.height // 2))
    return None

def pump():
    while seq:
        t, v, x, y = seq.pop(0)
        win.event_simulate(type=t, value=v, x=x, y=y)
    return None

def check1():
    a = areas()
    p = a.get('PROPERTIES') or a.get('DOPESHEET_EDITOR')
    log("after dock", [x.type for x in win.screen.areas], [s.type for s in p.spaces])
    log("OK" if len(win.screen.areas) == 3 and len(p.spaces) == 2 else "FAIL", "docked as a tab")
    shot("ui_tabs1.png")
    return None

def plan2():
    # Drag the inactive Properties tab button off onto the 3D view right edge.
    a = areas()
    p = a.get('DOPESHEET_EDITOR') or a.get('PROPERTIES')
    h = next(r for r in p.regions if r.type == 'HEADER')
    v = a.get('VIEW_3D') or a['DOPESHEET_EDITOR']
    # The strip starts after the editor-type menu; second tab is the Timeline (newest last).
    drag((h.x + 60, h.y + h.height // 2), (v.x + v.width - 20, v.y + v.height // 2))
    return None

def hold():
    # Everything but the release, to see the drop preview.
    while len(seq) > 1:
        t, v, x, y = seq.pop(0)
        win.event_simulate(type=t, value=v, x=x, y=y)
    log("before release", seq)
    return None


def preview():
    shot("ui_tabs_preview.png")
    return None


def check2():
    state = [(x.type, len(x.spaces)) for x in win.screen.areas]
    log("after tab drag", state, [(x.type, x.x, x.y, x.width, x.height) for x in win.screen.areas])
    log("OK" if len(state) == 4 else "FAIL", "tab torn off")
    shot("ui_tabs2.png")
    bpy.ops.wm.quit_blender()

bpy.app.timers.register(setup, first_interval=2)
bpy.app.timers.register(plan1, first_interval=3)
bpy.app.timers.register(pump, first_interval=3.2)
bpy.app.timers.register(check1, first_interval=6)
bpy.app.timers.register(plan2, first_interval=6.5)
bpy.app.timers.register(hold, first_interval=6.7)
bpy.app.timers.register(preview, first_interval=7.5)
bpy.app.timers.register(pump, first_interval=8.0)
bpy.app.timers.register(check2, first_interval=9.5)
