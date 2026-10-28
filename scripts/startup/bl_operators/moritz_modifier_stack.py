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
from bpy.props import BoolProperty, EnumProperty, StringProperty
from bpy.types import Operator

LINKS = "mx_modifier_links"
# Native Moritz modifiers keep their edits outside RNA; they can't be linked by copying properties.
_NOT_LINKABLE = {'EDIT_POLY', 'EDIT_SPLINE'}
_SKIP = {"rna_type", "name", "type", "show_expanded", "is_active", "is_override_data",
         "persistent_uid", "use_pin_to_last", "execution_time"}

# The modifier clipboard: (object name, modifier name) pairs.
_clipboard = []


def _active(context):
    """The object and its selected modifier: None when the base is selected in the stack (no
    active modifier, or the modifier an add-on marks as the base's own settings)."""
    ob = context.object
    mod = ob.modifiers.active if ob else None
    hook = getattr(bpy.types.DATA_PT_modifiers, "moritz_base_entry", None)
    if mod is not None and hook is not None and hook(ob)[0] == mod:
        mod = None
    return ob, mod


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


class OBJECT_OT_moritz_modifier_select_base(Operator):
    """Select the base object in the stack: its settings show instead of a modifier's"""
    bl_idname = "object.moritz_modifier_select_base"
    bl_label = "Select Base Object"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        ob = context.object
        # No active modifier is the base (Max shows one entry's settings at a time).
        ob.modifiers.active = None
        for mod in ob.modifiers:
            mod.show_expanded = False
        return {'FINISHED'}


# Stack entries open to show their sub-object levels: (object name, modifier name or "" for the
# base). Not saved, as in Max.
_open_entries = set()


def is_entry_open(ob, mod):
    return (ob.name, mod.name if mod is not None else "") in _open_entries


def _select_entry(ob, name):
    """Select a stack entry by modifier name ("" for the base object)."""
    if name:
        ob.moritz_modifier_stack_index = ob.modifiers.find(name)
    else:
        bpy.ops.object.moritz_modifier_select_base()


class OBJECT_OT_moritz_modifier_select(Operator):
    """Select this entry of the modifier stack: its settings show below"""
    bl_idname = "object.moritz_modifier_select"
    bl_label = "Select Stack Entry"
    bl_options = {'INTERNAL'}

    modifier: StringProperty(name="Modifier", description="Modifier name, empty for the base object")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        ob = context.object
        if self.modifier and self.modifier not in ob.modifiers:
            return {'CANCELLED'}
        from bl_ui.properties_data_modifier import _base_selected
        current = "" if _base_selected(ob) else ob.modifiers.active.name
        if current != self.modifier and context.mode != 'OBJECT':
            # Another entry: leave the sub-object level of this one first, as Max does.
            _set_level(context, 'OBJECT')
        _select_entry(ob, self.modifier)
        return {'FINISHED'}


def _set_level(context, level):
    if hasattr(bpy.types, "MAXIMIZE_OT_subobject"):
        return bpy.ops.maximize.subobject(level=level)
    if level in {'SEGMENT', 'SPLINE'}:
        level = 'VERTEX'
    return bpy.ops.object.subobject_level(level=level)


class OBJECT_OT_moritz_stack_expand(Operator):
    """Show or hide this entry's sub-object levels"""
    bl_idname = "object.moritz_stack_expand"
    bl_label = "Expand Stack Entry"
    bl_options = {'INTERNAL'}

    modifier: StringProperty(name="Modifier", description="Modifier name, empty for the base object")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        key = (context.object.name, self.modifier)
        if key in _open_entries:
            _open_entries.discard(key)
        else:
            _open_entries.add(key)
        if context.area is not None:
            context.area.tag_redraw()
        return {'FINISHED'}


class OBJECT_OT_moritz_stack_level(Operator):
    """Edit this entry at this sub-object level (click again to go back to the object)"""
    bl_idname = "object.moritz_stack_level"
    bl_label = "Sub-Object Level"
    bl_options = {'REGISTER', 'UNDO'}

    modifier: StringProperty(name="Modifier", description="Modifier name, empty for the base object")
    level: StringProperty(name="Level")

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob is not None and ob.type in {'MESH', 'CURVE'}

    def execute(self, context):
        bpy.ops.object.moritz_modifier_select(modifier=self.modifier)
        _set_level(context, self.level)
        return {'FINISHED'}


class OBJECT_OT_moritz_modifier_rename(Operator):
    """Rename the selected modifier"""
    bl_idname = "object.moritz_modifier_rename"
    bl_label = "Rename Modifier"
    bl_options = {'REGISTER', 'UNDO'}

    name: StringProperty(name="Name")

    @classmethod
    def poll(cls, context):
        return _active(context)[1] is not None

    def invoke(self, context, _event):
        self.name = _active(context)[1].name
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        ob, mod = _active(context)
        old = mod.name
        mod.name = self.name
        # Keep the Paste Instanced links under the new name.
        links = ob.get(LINKS)
        if links and old in links:
            links[mod.name] = links[old]
            del links[old]
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
    OBJECT_OT_moritz_modifier_select_base,
    OBJECT_OT_moritz_modifier_delete,
    OBJECT_OT_moritz_modifier_select,
    OBJECT_OT_moritz_stack_expand,
    OBJECT_OT_moritz_stack_level,
    OBJECT_OT_moritz_modifier_rename,
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
