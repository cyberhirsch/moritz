# Moritz: a copy of `maximize/keymap_max.py` from the Maximize add-on
# (github.com/cyberhirsch/maximize), the single source of the Max and Moritz keys. Keep the two
# in sync; bindings to Maximize's operators are skipped while the add-on is not enabled.
# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""The Max keymap: Blender's Industry Compatible keymap with 3ds Max's default keys on top.

Loaded through the keyconfig presets that `keymaps.py` writes, so they show up in the splash screen
and in Preferences > Keymap like Blender's own keymaps. Moritz is Max with Blender's
selection ideas where Max has nothing comparable; see `docs/shortcut_plan.md`, "Selection presets". Keys follow 3ds Max 2026 defaults; see
`docs/shortcuts.md` in the Maximize repository.
"""

MODS = ("ctrl", "shift", "alt", "oskey")

# Keymaps that are active in the 3D Viewport. A viewport-wide Max key removes the same key from
# all of them; otherwise the mode keymaps, which take priority, would still win.
VIEWPORT_KEYMAPS = (
    "3D View", "3D View Generic", "Object Mode", "Object Non-modal", "Mesh", "Curve", "Curves",
    "Armature", "Pose", "Metaball", "Lattice", "Font", "Point Cloud", "Particle", "Sculpt",
    "Weight Paint", "Vertex Paint", "Image Paint", "Frames", "Grease Pencil",
)


def _event(type, value='PRESS', ctrl=False, shift=False, alt=False, **extra):
    ev = {"type": type, "value": value}
    for mod, on in (("ctrl", ctrl), ("shift", shift), ("alt", alt)):
        if on:
            ev[mod] = True
    ev.update(extra)
    return ev


def _same_event(a, b):
    if a.get("type") != b.get("type"):
        return False
    va, vb = a.get("value", 'PRESS'), b.get("value", 'PRESS')
    if va != vb and {va, vb} != {'PRESS', 'CLICK'}:
        return False
    if a.get("any") or b.get("any"):
        return True
    for mod in MODS:
        ma, mb = a.get(mod, False), b.get(mod, False)
        if ma == -1 or mb == -1:
            continue
        if bool(ma) != bool(mb):
            return False
    return a.get("key_modifier") == b.get("key_modifier")


class KeymapPatcher:
    def __init__(self, keyconfig_data, available=None):
        self.items = {name: content["items"] for name, _args, content in keyconfig_data}
        # `available(idname, props)`: False skips a binding whose operator or menu is missing (Moritz
        # without the Maximize add-on), so the key keeps its Industry Compatible meaning.
        self.available = available or (lambda _idname, _props: True)

    def strip(self, ev, keymaps):
        for name in keymaps:
            items = self.items.get(name)
            if items is not None:
                items[:] = [it for it in items if not _same_event(it[1], ev)]

    def remove(self, keymap, idname, ev):
        items = self.items[keymap]
        items[:] = [it for it in items if not (it[0] == idname and _same_event(it[1], ev))]

    def bind(self, keymap, idname, ev, props=None, viewport=False):
        """Bind a key, replacing whatever used it in that keymap (or in the whole viewport)."""
        if not self.available(idname, props or {}):
            return
        self.strip(ev, VIEWPORT_KEYMAPS if viewport else (keymap,))
        self.items[keymap].append((idname, ev, {"properties": list(props.items())} if props else None))

    def view(self, idname, ev, props=None):
        self.bind("3D View", idname, ev, props, viewport=True)

    def append(self, keymap, idname, ev, props=None):
        """Add a key without replacing others (an operator that passes the event on)."""
        if self.available(idname, props or {}):
            self.items[keymap].append((idname, ev, {"properties": list(props.items())} if props else None))


def apply(km, moritz=False, maya_navigation=False):
    # --------------------------------------------------------------------------
    # Navigation: MMB pan, Alt+MMB orbit, Ctrl+Alt+MMB zoom, wheel zoom.
    km.remove("3D View", "view3d.rotate", _event('LEFTMOUSE', alt=True))
    km.remove("3D View", "view3d.zoom", _event('RIGHTMOUSE', alt=True))
    km.view("view3d.move", _event('MIDDLEMOUSE'))
    # Industry Compatible copies the active tool's left-drag to the middle mouse (Maya), and tool
    # keymaps come first: the middle mouse would move the selection instead of panning. Max always
    # pans with it.
    for name, items in km.items.items():
        if name.startswith("3D View Tool:"):
            items[:] = [it for it in items if not (it[1].get("type") == 'MIDDLEMOUSE' and not any(
                it[1].get(mod) for mod in ("ctrl", "shift", "alt", "oskey")))]
    km.view("view3d.rotate", _event('MIDDLEMOUSE', alt=True))
    km.view("view3d.zoom", _event('MIDDLEMOUSE', ctrl=True, alt=True))
    km.view("view3d.zoom", _event('LEFT_BRACKET', repeat=True), {"delta": 1})
    km.view("view3d.zoom", _event('RIGHT_BRACKET', repeat=True), {"delta": -1})
    km.view("view3d.zoom_border", _event('W', ctrl=True))

    # Zoom Extents.
    km.view("view3d.view_selected", _event('Z'), {"use_all_regions": False})
    km.view("view3d.view_all", _event('Z', ctrl=True, alt=True), {"center": False})
    km.view("view3d.view_all", _event('Z', ctrl=True, shift=True), {"use_all_regions": True, "center": False})

    # Views.
    for key, view in (('T', 'TOP'), ('B', 'BOTTOM'), ('F', 'FRONT'), ('L', 'LEFT')):
        km.view("view3d.view_axis", _event(key), {"type": view})
    km.view("maximize.view_projection", _event('P'), {"projection": 'PERSP'})
    km.view("maximize.view_projection", _event('U'), {"projection": 'ORTHO'})
    km.view("view3d.view_camera", _event('C'))
    km.view("maximize.camera_from_view", _event('C', ctrl=True))
    km.view("maximize.viewport_maximize", _event('W', alt=True))
    # Max's V: the Point-of-View menu of the viewport under the mouse. Only in the 3D View keymap,
    # so Edit Mode keeps Blender's V (Rip, handle types).
    km.bind("3D View", "wm.call_menu", _event('V'), {"name": "MAXIMIZE_MT_point_of_view"})
    km.view("view3d.localview", _event('Q', alt=True))

    # Display.
    km.view("maximize.see_through_objects", _event('X', alt=True))
    km.view("wm.context_toggle_enum", _event('F3'),
            {"data_path": "space_data.shading.type", "value_1": 'WIREFRAME', "value_2": 'SOLID'})
    km.view("wm.context_toggle", _event('F4'), {"data_path": "space_data.overlay.show_wireframes"})
    km.view("wm.context_toggle", _event('G'), {"data_path": "space_data.overlay.show_floor"})
    km.view("wm.context_toggle", _event('SEVEN'), {"data_path": "space_data.overlay.show_stats"})
    for key, kind in (('C', "camera"), ('L', "light"), ('G', "mesh"), ('H', "empty")):
        km.view("wm.context_toggle", _event(key, shift=True),
                {"data_path": "space_data.show_object_viewport_" + kind})

    # Snaps, search, tools.
    km.view("wm.context_toggle", _event('S'), {"data_path": "tool_settings.use_snap"})
    km.view("maximize.angle_snap", _event('A'))
    km.view("wm.search_menu", _event('X'))
    # Tab toggles Object / Edit Mode as in Blender, beside Max's 1-6 levels (Seb, both keymaps);
    # Industry Compatible's search on Tab moves to X, Max's own Search Actions key.
    km.remove("3D View", "wm.search_menu", _event('TAB'))
    km.bind("Object Non-modal", "object.mode_set", _event('TAB'), {"mode": 'EDIT', "toggle": True})
    km.view("maximize.transform_typein", _event('F12'))
    km.view("maximize.affect_pivot_only", _event('INSERT'))
    km.view("maximize.material_editor", _event('M'))
    # Quad menu in Object Mode and Edit Poly; other modes keep their own context menus.
    for mode_km in ("Object Mode", "Mesh"):
        km.bind(mode_km, "wm.call_panel", _event('RIGHTMOUSE'), {"name": "MAXIMIZE_PT_quad", "keep_open": False})

    # Selection: Ctrl+click adds, Alt+click removes (Shift is not a selection key in Max). In Moritz,
    # Ctrl+click on a selected object removes it again.
    items = km.items["3D View"]
    items[:] = [it for it in items if not (it[0] == "view3d.select" and it[1].get("type") == 'LEFTMOUSE'
                                           and it[1].get("value") == 'CLICK')]
    km.bind("3D View", "view3d.select", _event('LEFTMOUSE', 'CLICK'), {"deselect_all": True})
    km.bind("3D View", "view3d.select", _event('LEFTMOUSE', 'CLICK', ctrl=True),
            {"toggle": True} if moritz else {"extend": True})
    km.bind("3D View", "view3d.select", _event('LEFTMOUSE', 'CLICK', alt=True), {"deselect": True})
    km.bind("3D View", "view3d.select", _event('LEFTMOUSE', 'CLICK', ctrl=True, shift=True),
            {"toggle": True, "enumerate": True})
    if not maya_navigation:
        # With Maya navigation, Alt+LMB orbits and the tools keep Shift/Ctrl.
        _max_tool_selection(km)

    # --------------------------------------------------------------------------
    # Objects.
    om = "Object Mode"
    km.bind(om, "object.select_all", _event('D', ctrl=True), {"action": 'DESELECT'})
    km.bind(om, "maximize.select_by_name", _event('H'))
    km.bind(om, "maximize.align", _event('A', alt=True))
    km.bind(om, "maximize.clone", _event('V', ctrl=True))
    km.bind(om, "maximize.clone_drag", _event('LEFTMOUSE', 'CLICK_DRAG', shift=True))
    # Shift+drag on a move, rotate or scale gizmo handle: clone first, then the gizmo drags the clones.
    for gizmo_km in ("Generic Gizmo Maybe Drag", "Generic Gizmo Drag"):
        if gizmo_km in km.items and km.available("maximize.clone_gizmo", {}):
            km.items[gizmo_km][:0] = [
                ("maximize.clone_gizmo", _event('LEFTMOUSE', 'CLICK_DRAG', shift=True), None),
                ("maximize.smart_extrude_drag", _event('LEFTMOUSE', 'CLICK_DRAG', shift=True),
                 {"properties": [("gizmo", True)]}),
                ("gizmogroup.gizmo_tweak", _event('LEFTMOUSE', 'CLICK_DRAG', shift=True), None),
            ]
    km.bind(om, "object.hide_view_set", _event('H', alt=True), {"unselected": False})
    km.bind(om, "object.hide_view_set", _event('I', alt=True), {"unselected": True})
    km.bind(om, "object.hide_view_clear", _event('U', alt=True))
    km.bind(om, "anim.keyframe_insert", _event('K'))
    # Double-click an object: select it and its children.
    km.bind(om, "object.select_grouped", _event('LEFTMOUSE', 'DOUBLE_CLICK'),
            {"type": 'CHILDREN_RECURSIVE', "extend": True})
    # Without the add-on, the core's `object.subobject_level` (Border as Edge, Element as Polygon).
    level_op = "maximize.subobject" if km.available("maximize.subobject", {}) else "object.subobject_level"
    for key, level in (('ONE', 'VERTEX'), ('TWO', 'EDGE'), ('THREE', 'BORDER'),
                       ('FOUR', 'POLYGON'), ('FIVE', 'ELEMENT')):
        km.bind(om, level_op, _event(key), {"level": level})
        km.bind("Mesh", level_op, _event(key), {"level": level})
    km.bind("Mesh", level_op, _event('SIX'), {"level": 'OBJECT'})
    # Editable Spline: 1 vertex, 2 segment, 3 spline (one Edit Mode in Blender), 6 back to the object.
    if "Curve" in km.items:
        for key, level in (('ONE', 'VERTEX'), ('TWO', 'EDGE'), ('THREE', 'BORDER'), ('SIX', 'OBJECT')):
            km.bind("Curve", level_op, _event(key), {"level": level})
        # Segment and Spline levels: a click picks a whole segment or spline; Delete works per level.
        for mods, props in (({}, {}), ({"ctrl": True}, {"extend": True}), ({"alt": True}, {"deselect": True})):
            km.append("Curve", "maximize.spline_pick", _event('LEFTMOUSE', 'CLICK', **mods), props)
        km.bind("Curve", "maximize.spline_level_delete", _event('DEL'))
        # Lock Handles: a drag on a selected vertex's handle (passes through when off).
        km.append("Curve", "maximize.spline_lock_handles_drag", _event('LEFTMOUSE', 'CLICK_DRAG'))
    # Border and Element have no Blender select mode: clicks there pick a whole border or element
    # (the operator passes the click through at the other levels).
    for mods, props in (({}, {}), ({"ctrl": True}, {"extend": True}), ({"alt": True}, {"deselect": True})):
        km.append("Mesh", "maximize.subobject_pick", _event('LEFTMOUSE', 'CLICK', **mods), props)
        # Loop / Ring mode: a click picks the whole loop or ring (passes on when off).
        km.append("Mesh", "maximize.loop_mode_pick", _event('LEFTMOUSE', 'CLICK', **mods), props)

    # --------------------------------------------------------------------------
    # Edit Poly.
    me = "Mesh"
    km.bind(me, "mesh.select_all", _event('D', ctrl=True), {"action": 'DESELECT'})
    # Shift+drag of polygons with the Move tool: Smart Extrude (passes on with other tools).
    km.bind(me, "maximize.smart_extrude_drag", _event('LEFTMOUSE', 'CLICK_DRAG', shift=True))
    km.bind(me, "mesh.select_edge_loop_multi", _event('L', alt=True))
    km.bind(me, "mesh.select_edge_ring_multi", _event('R', alt=True))
    # Double-click an edge: select its loop.
    km.bind(me, "mesh.loop_select", _event('LEFTMOUSE', 'DOUBLE_CLICK'), {"extend": True})
    if moritz:
        km.bind(me, "mesh.edgering_select", _event('LEFTMOUSE', 'DOUBLE_CLICK', ctrl=True, alt=True),
                {"extend": True})
        km.bind(me, "mesh.shortest_path_pick", _event('LEFTMOUSE', 'CLICK', ctrl=True, shift=True))
    km.bind(me, "mesh.select_more", _event('PAGE_UP', ctrl=True))
    km.bind(me, "mesh.select_less", _event('PAGE_DOWN', ctrl=True))
    km.bind(me, "mesh.extrude_context_move", _event('E', shift=True))
    km.bind(me, "maximize.chamfer", _event('C', ctrl=True, shift=True))
    km.bind(me, "maximize.bevel_poly", _event('B', ctrl=True, shift=True))
    km.bind(me, "maximize.connect", _event('E', ctrl=True, shift=True))
    km.bind(me, "mesh.knife_tool", _event('C', alt=True))
    km.bind(me, "mesh.loopcut_slide", _event('ONE', alt=True))
    km.bind(me, "mesh.merge", _event('W', ctrl=True, shift=True), {"type": 'LAST'})
    km.bind(me, "mesh.merge", _event('C', ctrl=True, alt=True), {"type": 'COLLAPSE'})
    km.bind(me, "mesh.dissolve_mode", _event('BACK_SPACE'))
    km.bind(me, "maximize.delete_subobject", _event('DEL'))
    km.bind(me, "mesh.hide", _event('H', alt=True), {"unselected": False})
    km.bind(me, "mesh.hide", _event('I', alt=True), {"unselected": True})
    km.bind(me, "mesh.reveal", _event('U', alt=True))
    km.bind(me, "maximize.select_by_name", _event('H'))

    # --------------------------------------------------------------------------
    # Global: undo/redo, repeat, render, animation.
    km.bind("Screen", "ed.redo", _event('Y', ctrl=True, repeat=True))
    km.bind("Screen", "screen.repeat_last", _event('SEMI_COLON'))
    # Hold / Fetch, everywhere but editors with their own Ctrl+H (the Text Editor's Replace).
    for idname, ev in (("maximize.hold", _event('H', ctrl=True)), ("maximize.fetch", _event('F', ctrl=True, alt=True))):
        km.strip(ev, VIEWPORT_KEYMAPS)
        km.bind("Window", idname, ev)
    km.bind("Screen Editing", "render.render", _event('F9'), {"use_viewport": True})
    km.bind("Screen Editing", "render.render", _event('Q', shift=True), {"use_viewport": True})
    km.bind("Screen Editing", "maximize.render_setup", _event('F10'))
    fr = "Frames"
    km.strip(_event('SLASH'), VIEWPORT_KEYMAPS)
    km.bind(fr, "screen.animation_play", _event('SLASH'))
    km.strip(_event('PERIOD'), VIEWPORT_KEYMAPS)
    km.strip(_event('COMMA'), VIEWPORT_KEYMAPS)
    km.bind(fr, "screen.frame_offset", _event('PERIOD', repeat=True), {"delta": 1})
    km.bind(fr, "screen.frame_offset", _event('COMMA', repeat=True), {"delta": -1})
    km.strip(_event('HOME'), VIEWPORT_KEYMAPS)
    km.strip(_event('END'), VIEWPORT_KEYMAPS)
    km.bind(fr, "screen.frame_jump", _event('HOME'), {"end": False})
    km.bind(fr, "screen.frame_jump", _event('END'), {"end": True})
    km.strip(_event('N'), VIEWPORT_KEYMAPS)
    km.bind(fr, "wm.context_toggle", _event('N'), {"data_path": "scene.tool_settings.use_keyframe_insert_auto"})


def _max_tool_selection(km):
    """In selection tools, Ctrl adds and Alt subtracts, as in Max."""
    for name, items in km.items.items():
        if not name.startswith("3D View Tool:"):
            continue
        for i, (idname, ev, props) in enumerate(items):
            if not (idname.endswith(".select") or ".select_" in idname):
                continue
            prop_list = dict((props or {}).get("properties", []) or [])
            mods = {m for m in MODS if ev.get(m)}
            new_ev = None
            if mods == {"ctrl"} and (prop_list.get("mode") == 'SUB' or prop_list.get("deselect")):
                new_ev = {k: v for k, v in ev.items() if k != "ctrl"} | {"alt": True}
            elif mods == {"shift"} and (prop_list.get("mode") == 'ADD' or prop_list.get("extend") or
                                        prop_list.get("toggle")):
                new_ev = {k: v for k, v in ev.items() if k != "shift"} | {"ctrl": True}
            if new_ev is not None:
                items[i] = (idname, new_ev, props)


def _max_keys(km):
    """Max 2026 keys that the coverage check (`tools/check_max_keymap.py`) found missing or taken."""
    om, me = "Object Mode", "Mesh"
    # Conflicts: Max's meaning wins.
    km.bind(om, "object.select_grouped", _event('A', ctrl=True, shift=True))
    km.bind(me, "mesh.select_similar", _event('A', ctrl=True, shift=True))
    km.bind(om, "maximize.spacing", _event('I', shift=True))
    km.strip(_event('S', shift=True), VIEWPORT_KEYMAPS)
    km.view("wm.context_toggle", _event('S', shift=True), {"data_path": "space_data.show_object_viewport_curve"})
    km.strip(_event('UP_ARROW'), VIEWPORT_KEYMAPS)
    km.view("view3d.walk", _event('UP_ARROW'))
    # Views, cameras, render.
    km.view("maximize.camera_from_view", _event('C', shift=True, alt=True))
    km.view("maximize.camera_from_view", _event('C', ctrl=True, shift=True, alt=True))
    km.view("view3d.localview", _event('Q', ctrl=True, alt=True))
    km.view("view3d.zoom", _event('EQUAL', ctrl=True, repeat=True), {"delta": 1})
    km.view("view3d.zoom", _event('MINUS', ctrl=True, repeat=True), {"delta": -1})
    km.view("wm.context_cycle_enum", _event('FIVE', shift=True, alt=True),
            {"data_path": "tool_settings.transform_pivot_point", "wrap": True})
    km.bind("Screen Editing", "render.render", _event('F9', shift=True), {"use_viewport": True})
    # Hierarchy selection.
    km.strip(_event('PAGE_UP'), VIEWPORT_KEYMAPS)
    km.strip(_event('PAGE_DOWN'), VIEWPORT_KEYMAPS)
    km.bind(om, "object.select_hierarchy", _event('PAGE_UP'), {"direction": 'PARENT', "extend": False})
    km.bind(om, "object.select_hierarchy", _event('PAGE_DOWN'), {"direction": 'CHILD', "extend": False})
    km.bind(om, "object.select_grouped", _event('PAGE_DOWN', shift=True), {"type": 'CHILDREN_RECURSIVE'})
    # Edit Poly.
    km.bind(me, "mesh.extrude_context_move", _event('E', shift=True, alt=True))
    km.bind(me, "mesh.select_more", _event('UP_ARROW', ctrl=True))
    km.bind(me, "mesh.select_less", _event('DOWN_ARROW', ctrl=True))
    for keymap in (om, me):
        km.bind(keymap, "wm.context_toggle", _event('B', shift=True),
                {"data_path": "tool_settings.use_proportional_edit"})
    km.bind(me, "maximize.attach_edit", _event('D', shift=True, alt=True))
    km.bind(me, "mesh.split", _event('R', shift=True))
    km.bind(me, "maximize.cap", _event('P', alt=True))
    km.bind(me, "maximize.detach", _event('D', ctrl=True, alt=True))
    km.bind(me, "maximize.make_planar", _event('M', alt=True))
    km.bind(me, "mesh.subdivide", _event('M', ctrl=True), {"smoothness": 1.0})
    km.bind(me, "maximize.quickslice", _event('Q', ctrl=True, shift=True))
    # Edit Poly keys that map onto Blender tools: Insert Loop, Spin Edge.
    km.bind(me, "mesh.loopcut_slide", _event('THREE', alt=True))
    km.bind(me, "mesh.edge_rotate", _event('FIVE', alt=True), {"use_ccw": False})
    # Ignore Backfacing: select through (X-ray), Safe Frames, light view.
    km.view("view3d.toggle_xray", _event('X', shift=True, alt=True))
    km.view("wm.context_toggle", _event('F', shift=True), {"data_path": "scene.camera.data.show_safe_areas"})
    km.view("view3d.object_as_camera", _event('FOUR', shift=True))
    # Show End Result, viewport undo / redo.
    for keymap in (om, me):
        km.bind(keymap, "maximize.show_end_result", _event('ACCENT_GRAVE', alt=True))
    km.view("maximize.view_history", _event('Z', shift=True), {"redo": False})
    km.view("maximize.view_history", _event('Y', shift=True), {"redo": True})
    # F5 / F6 / F7 constrain the transform to X / Y / Z, F8 to the planes, as in Max.
    tm = "Transform Modal Map"
    if tm in km.items:
        for key, axis in (('F5', 'AXIS_X'), ('F6', 'AXIS_Y'), ('F7', 'AXIS_Z'), ('F8', 'PLANE_Z')):
            km.items[tm].append((axis, _event(key), None))


def _numpad_views(km):
    """Blender's numpad views: Max leaves the numpad free, and Blender tutorials keep working."""
    from math import pi
    km.view("view3d.view_camera", _event('NUMPAD_0'))
    for ctrl, pairs in ((False, (('NUMPAD_1', 'FRONT'), ('NUMPAD_3', 'RIGHT'), ('NUMPAD_7', 'TOP'))),
                        (True, (('NUMPAD_1', 'BACK'), ('NUMPAD_3', 'LEFT'), ('NUMPAD_7', 'BOTTOM')))):
        for key, view in pairs:
            km.view("view3d.view_axis", _event(key, ctrl=ctrl), {"type": view})
            km.view("view3d.view_axis", _event(key, ctrl=ctrl, shift=True), {"type": view, "align_active": True})
    for key, orbit, pan in (('NUMPAD_2', 'ORBITDOWN', 'PANDOWN'), ('NUMPAD_4', 'ORBITLEFT', 'PANLEFT'),
                            ('NUMPAD_6', 'ORBITRIGHT', 'PANRIGHT'), ('NUMPAD_8', 'ORBITUP', 'PANUP')):
        km.view("view3d.view_orbit", _event(key, repeat=True), {"type": orbit})
        km.view("view3d.view_pan", _event(key, ctrl=True, repeat=True), {"type": pan})
    km.view("view3d.view_roll", _event('NUMPAD_4', shift=True, repeat=True), {"type": 'LEFT'})
    km.view("view3d.view_roll", _event('NUMPAD_6', shift=True, repeat=True), {"type": 'RIGHT'})
    km.view("view3d.view_orbit", _event('NUMPAD_9'), {"angle": pi, "type": 'ORBITRIGHT'})
    km.view("view3d.view_persportho", _event('NUMPAD_5'))
    km.view("view3d.view_selected", _event('NUMPAD_PERIOD'))
    km.view("view3d.localview", _event('NUMPAD_SLASH'))


def _moritz_keys(km):
    """Moritz: Space maximizes the viewport beside Alt+W (play stays on Max's /, and Space still
    plays outside the viewport)."""
    # In Frames, where Space plays: the 3D View keymap comes after it.
    km.bind("Frames", "maximize.space_key", _event('SPACE'))


def _moritz_selection(km):
    """Moritz: window or crossing by drag direction."""
    for name in ("3D View Tool: Select Box", "3D View Tool: Select Box (fallback)"):
        items = km.items.get(name)
        if items is None or not km.available("maximize.select_region", {}):
            continue
        # In front of Blender's box select, which stays for the modes the operator doesn't handle.
        new = []
        for idname, ev, props in items:
            if idname == "view3d.select_box" and ev.get("type") == 'LEFTMOUSE':
                new.append(("maximize.select_region", ev, props))
            new.append((idname, ev, props))
        items[:] = new


def _editors(km):
    """Max keys in the other editors where nothing clashes: F2 renames (Scene Explorer, Slate),
    Ctrl+A/D/I select all/none/invert, K sets a key, Ctrl+Alt+Z frames all (Track View)."""
    km.bind("Outliner", "outliner.item_rename", _event('F2'))
    # Scene Explorer: double-click selects an object and its children; rename stays on F2.
    km.bind("Outliner", "maximize.outliner_select_children", _event('LEFTMOUSE', 'DOUBLE_CLICK'))
    for keymap, prefix in (("Graph Editor", "graph"), ("Dopesheet", "action"), ("Node Editor", "node")):
        if keymap not in km.items:
            continue
        km.bind(keymap, prefix + ".select_all", _event('A', ctrl=True), {"action": 'SELECT'})
        km.bind(keymap, prefix + ".select_all", _event('D', ctrl=True), {"action": 'DESELECT'})
        km.bind(keymap, prefix + ".select_all", _event('I', ctrl=True), {"action": 'INVERT'})
        km.bind(keymap, prefix + ".duplicate_move", _event('D', shift=True))
        if keymap != "Node Editor":
            km.bind(keymap, prefix + ".keyframe_insert", _event('K'))
            km.bind(keymap, prefix + ".view_all", _event('Z', ctrl=True, alt=True))
    # Slate: H hides unused sockets, P shows the parameters, F2 renames the node.
    km.bind("Node Editor", "node.hide_socket_toggle", _event('H'))
    km.bind("Node Editor", "wm.context_toggle", _event('P'), {"data_path": "space_data.show_region_ui"})
    km.bind("Node Editor", "wm.call_panel", _event('F2'), {"name": "TOPBAR_PT_name", "keep_open": False})


def _maya_navigation(km):
    """Preference "Maya navigation", Max's own switch: Alt+LMB orbit, Alt+MMB pan, Alt+RMB zoom,
    Shift toggles and Ctrl removes from the selection."""
    km.view("view3d.rotate", _event('LEFTMOUSE', alt=True))
    km.view("view3d.move", _event('MIDDLEMOUSE', alt=True))
    km.view("view3d.zoom", _event('RIGHTMOUSE', alt=True))
    items = km.items["3D View"]
    items[:] = [it for it in items if not (it[0] == "view3d.select" and it[1].get("type") == 'LEFTMOUSE'
                                           and it[1].get("value") == 'CLICK')]
    km.bind("3D View", "view3d.select", _event('LEFTMOUSE', 'CLICK'), {"deselect_all": True})
    km.bind("3D View", "view3d.select", _event('LEFTMOUSE', 'CLICK', shift=True), {"toggle": True})
    km.bind("3D View", "view3d.select", _event('LEFTMOUSE', 'CLICK', ctrl=True), {"deselect": True})
    km.bind("3D View", "view3d.select", _event('LEFTMOUSE', 'CLICK', ctrl=True, shift=True), {"extend": True})


def _f_frames_selection(km):
    """Preference "F frames selection" (Maya, Unreal): F frames, Ctrl+F is the front view."""
    km.view("view3d.view_selected", _event('F'), {"use_all_regions": False})
    km.view("view3d.view_axis", _event('F', ctrl=True), {"type": 'FRONT'})


def _blender_modal_keys(km):
    """Preference "Blender modal keys": Ctrl+Shift+G/R/S start Blender's free modal transforms."""
    for keymap in ("Object Mode", "Mesh"):
        for key, idname in (('G', "transform.translate"), ('R', "transform.rotate"), ('S', "transform.resize")):
            km.bind(keymap, idname, _event(key, ctrl=True, shift=True))


def generate_keymaps(industry_compatible, params, moritz=False, available=None, options=None):
    """`options`: the keymap preferences (`use_maya_navigation`, `use_f_frames_selection`,
    `use_blender_modal_keys`)."""
    options = options or {}
    keyconfig_data = industry_compatible.generate_keymaps(params)
    km = KeymapPatcher(keyconfig_data, available)
    apply(km, moritz, options.get("use_maya_navigation", False))
    _max_keys(km)
    _numpad_views(km)
    _editors(km)
    if moritz:
        _moritz_selection(km)
        _moritz_keys(km)
    if options.get("use_maya_navigation"):
        _maya_navigation(km)
    if options.get("use_f_frames_selection"):
        _f_frames_selection(km)
    if options.get("use_blender_modal_keys"):
        _blender_modal_keys(km)
    return keyconfig_data
