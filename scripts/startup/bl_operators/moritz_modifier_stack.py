# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Moritz: Max's modifier stack operations for the Modify tab: Copy / Paste, Paste Instanced,
Make Unique, Off in Renderer.

Paste Instanced links modifiers on any objects: changing one changes all. The links are kept in
each object's "mx_modifier_links" custom property ({modifier name: link id}); the modifiers
themselves are plain, so stock Blender sees independent copies.
"""

import bpy
from bpy.app.handlers import persistent
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator

LINKS = "mx_modifier_links"
# Native Moritz modifiers keep their edits outside RNA; they can't be linked by copying properties.
_NOT_LINKABLE = {'EDIT_POLY', 'EDIT_SPLINE'}
_SKIP = {"rna_type", "name", "type", "show_expanded", "is_active", "is_override_data",
         "persistent_uid", "use_pin_to_last", "execution_time"}

# The modifier clipboard: (object name, modifier name) pairs.
_clipboard = []


def _active(context):
    ob = context.object
    return ob, (ob.modifiers.active if ob else None)


def _values(mod):
    out = []
    for prop in mod.bl_rna.properties:
        if prop.identifier in _SKIP or prop.is_readonly or prop.type == 'COLLECTION':
            continue
        value = getattr(mod, prop.identifier)
        if getattr(prop, "is_array", False):
            value = tuple(value)
        out.append((prop.identifier, value))
    if mod.type == 'NODES':
        for key in mod.keys():
            value = mod[key]
            out.append(("[" + key + "]", tuple(value) if hasattr(value, "__len__") and
                        not isinstance(value, str) else value))
    return tuple(out)


def _apply_values(mod, values):
    for key, value in values:
        try:
            if key.startswith("["):
                mod[key[1:-1]] = value
            else:
                setattr(mod, key, value)
        except (AttributeError, TypeError, ValueError):
            pass


def link_of(ob, mod):
    links = ob.get(LINKS)
    return links.get(mod.name) if links else None


def _set_link(ob, mod, link):
    links = dict(ob.get(LINKS, {}))
    if link is None:
        links.pop(mod.name, None)
    else:
        links[mod.name] = link
    if links:
        ob[LINKS] = links
    elif LINKS in ob:
        del ob[LINKS]


def _linked(link):
    for ob in bpy.data.objects:
        links = ob.get(LINKS)
        if not links:
            continue
        for name, value in links.items():
            if value == link:
                mod = ob.modifiers.get(name)
                if mod is not None:
                    yield ob, mod


def _paste(context, target, src_ob, src_mod):
    """Copy one modifier onto the target, above its active modifier. Returns the new modifier."""
    above = target.modifiers.active
    names = set(m.name for m in target.modifiers)
    with context.temp_override(object=src_ob, active_object=src_ob, selected_objects=[target],
                               selected_editable_objects=[target]):
        bpy.ops.object.modifier_copy_to_selected(modifier=src_mod.name)
    new = next((m for m in target.modifiers if m.name not in names), None)
    if new is None:
        return None
    if above is not None and above != new:
        index = list(target.modifiers).index(above) + 1
        with context.temp_override(object=target, active_object=target):
            bpy.ops.object.modifier_move_to_index(modifier=new.name, index=index)
    target.modifiers.active = new
    return new


class OBJECT_OT_moritz_modifier_copy(Operator):
    """Copy the selected modifier (Max's stack Copy)"""
    bl_idname = "object.moritz_modifier_copy"
    bl_label = "Copy Modifier"

    @classmethod
    def poll(cls, context):
        return _active(context)[1] is not None

    def execute(self, context):
        ob, mod = _active(context)
        _clipboard[:] = [(ob.name, mod.name)]
        return {'FINISHED'}


class OBJECT_OT_moritz_modifier_paste(Operator):
    """Paste the copied modifier above the selected one; Instanced keeps it linked to the copied
    modifier, so changing one changes both (Max's Paste Instanced)"""
    bl_idname = "object.moritz_modifier_paste"
    bl_label = "Paste Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    instanced: BoolProperty(name="Instanced", default=False)

    @classmethod
    def poll(cls, context):
        return context.object is not None and bool(_clipboard) and context.mode == 'OBJECT'

    def execute(self, context):
        target = context.object
        for ob_name, mod_name in _clipboard:
            src_ob = bpy.data.objects.get(ob_name)
            src_mod = src_ob.modifiers.get(mod_name) if src_ob else None
            if src_mod is None:
                self.report({'WARNING'}, "The copied modifier no longer exists")
                return {'CANCELLED'}
            if self.instanced and src_mod.type in _NOT_LINKABLE:
                self.report({'WARNING'}, f"{src_mod.name} can't be instanced; pasted as a copy")
            new = _paste(context, target, src_ob, src_mod)
            if new is None:
                self.report({'WARNING'}, "This object type can't take that modifier")
                return {'CANCELLED'}
            if self.instanced and src_mod.type not in _NOT_LINKABLE:
                link = link_of(src_ob, src_mod)
                if link is None:
                    link = "%s/%s" % (src_ob.name, src_mod.name)
                    _set_link(src_ob, src_mod, link)
                _set_link(target, new, link)
                _snapshots[link] = _values(src_mod)
        return {'FINISHED'}


class OBJECT_OT_moritz_modifier_make_unique(Operator):
    """Make Unique: the selected modifier stops being linked to its instances"""
    bl_idname = "object.moritz_modifier_make_unique"
    bl_label = "Make Unique"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ob, mod = _active(context)
        return mod is not None and link_of(ob, mod) is not None

    def execute(self, context):
        ob, mod = _active(context)
        link = link_of(ob, mod)
        _set_link(ob, mod, None)
        rest = list(_linked(link))
        if len(rest) == 1:
            _set_link(rest[0][0], rest[0][1], None)
        return {'FINISHED'}


class OBJECT_OT_moritz_modifier_toggle(Operator):
    """Turn the selected modifier off or on in the viewport or the renderer"""
    bl_idname = "object.moritz_modifier_toggle"
    bl_label = "Toggle Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    target: EnumProperty(items=(('VIEWPORT', "Viewport", ""), ('RENDER', "Renderer", "")))

    @classmethod
    def poll(cls, context):
        return _active(context)[1] is not None

    def execute(self, context):
        mod = _active(context)[1]
        prop = "show_viewport" if self.target == 'VIEWPORT' else "show_render"
        setattr(mod, prop, not getattr(mod, prop))
        return {'FINISHED'}


class OBJECT_OT_moritz_modifier_delete(Operator):
    """Delete the modifier under the mouse, or the one selected in the stack (Max's Delete key)"""
    bl_idname = "object.moritz_modifier_delete"
    bl_label = "Delete Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return (space is not None and space.type == 'PROPERTIES' and space.context == 'MODIFIER' and
                _active(context)[1] is not None)

    def invoke(self, context, _event):
        # Over a modifier panel, Blender's own delete takes that panel's modifier.
        if 'FINISHED' in bpy.ops.object.modifier_remove('INVOKE_DEFAULT'):
            return {'FINISHED'}
        return self.execute(context)

    def execute(self, context):
        ob, mod = _active(context)
        with context.temp_override(object=ob):
            return bpy.ops.object.modifier_remove(modifier=mod.name)


# Paste Instanced sync: the last known values of each link.
_snapshots = {}


@persistent
def _sync_links(_scene, _depsgraph=None):
    groups = {}
    for ob in bpy.data.objects:
        links = ob.get(LINKS)
        if not links:
            continue
        for name, link in links.items():
            mod = ob.modifiers.get(name)
            if mod is not None:
                groups.setdefault(link, []).append(mod)
    for link, mods in groups.items():
        known = _snapshots.get(link)
        current = [_values(m) for m in mods]
        changed = next((v for v in current if v != known), None)
        if changed is None:
            continue
        for mod, values in zip(mods, current):
            if values != changed:
                _apply_values(mod, changed)
        _snapshots[link] = changed


@persistent
def _reset_snapshots(*_args):
    _snapshots.clear()


classes = (
    OBJECT_OT_moritz_modifier_copy,
    OBJECT_OT_moritz_modifier_paste,
    OBJECT_OT_moritz_modifier_make_unique,
    OBJECT_OT_moritz_modifier_toggle,
    OBJECT_OT_moritz_modifier_delete,
)

_keymap_items = []


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(_sync_links)
    bpy.app.handlers.load_post.append(_reset_snapshots)
    keyconfig = bpy.context.window_manager.keyconfigs.addon
    if keyconfig is not None:
        km = keyconfig.keymaps.new("Property Editor", space_type='PROPERTIES')
        for key in ('DEL', 'X'):
            _keymap_items.append((km, km.keymap_items.new("object.moritz_modifier_delete", key, 'PRESS')))


def unregister():
    from bpy.utils import unregister_class
    for km, item in _keymap_items:
        km.keymap_items.remove(item)
    _keymap_items.clear()
    bpy.app.handlers.load_post.remove(_reset_snapshots)
    bpy.app.handlers.depsgraph_update_post.remove(_sync_links)
    for cls in reversed(classes):
        unregister_class(cls)
