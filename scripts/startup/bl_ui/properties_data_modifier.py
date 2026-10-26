# SPDX-FileCopyrightText: 2009-2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import Panel, Menu, Operator
from bpy.app.translations import (
    pgettext_n as n_,
)


class ModifierButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "modifier"
    bl_options = {'HIDE_HEADER'}


class ModifierAddMenu:
    MODIFIER_TYPES_TO_LABELS = {
        enum_it.identifier: enum_it.name
        for enum_it in bpy.types.Modifier.bl_rna.properties["type"].enum_items_static
    }
    MODIFIER_TYPES_TO_ICONS = {
        enum_it.identifier: enum_it.icon
        for enum_it in bpy.types.Modifier.bl_rna.properties["type"].enum_items_static
    }
    MODIFIER_TYPES_I18N_CONTEXT = bpy.types.Modifier.bl_rna.properties["type"].translation_context

    @classmethod
    def operator_modifier_add(cls, layout, mod_type, text=None, no_icon=False):
        label = text if text else cls.MODIFIER_TYPES_TO_LABELS[mod_type]
        layout.operator(
            "object.modifier_add",
            text=label,
            # Although these are operators, the label actually comes from an (enum) property,
            # so the property's translation context must be used here.
            text_ctxt=cls.MODIFIER_TYPES_I18N_CONTEXT,
            icon='NONE' if no_icon else cls.MODIFIER_TYPES_TO_ICONS[mod_type],
        ).type = mod_type

    @classmethod
    def operator_modifier_add_asset(cls, layout, name, icon='NONE'):
        props = layout.operator(
            "object.modifier_add_node_group",
            text=name,
            text_ctxt=cls.MODIFIER_TYPES_I18N_CONTEXT,
            icon=icon,
        )
        props.asset_library_type = 'ESSENTIALS'
        props.asset_library_identifier = ""
        props.relative_asset_identifier = "nodes/geometry_nodes_essentials.blend/NodeTree/" + name


class DATA_PT_modifiers(ModifierButtonsPanel, Panel):
    bl_label = "Modifiers"

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob

    def draw(self, context):
        layout = self.layout
        # Moritz: one flat Add Modifier menu (as Blender before 4.x), the full one stays under "More".
        layout.operator("wm.call_menu", text="Add Modifier", icon='ADD').name = "OBJECT_MT_modifier_add_flat"
        # Moritz: Max's modifier stack, newest on top and the base object at the bottom.
        _draw_modifier_stack(layout, context)
        layout.template_modifiers()


class OBJECT_MT_modifier_add_flat(Menu):
    """Every modifier for this object type in one menu; typing filters it"""
    bl_label = "Add Modifier"
    bl_options = {'SEARCH_ON_KEY_PRESS'}

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        # The operator's own list is already filtered by the object type, with category headings.
        layout.operator_enum("object.modifier_add", "type")
        layout.separator()
        layout.menu("OBJECT_MT_modifier_add", text="More (Geometry Nodes Assets)")


_LEVEL_ICONS = {'VERT': 'VERTEXSEL', 'EDGE': 'EDGESEL', 'FACE': 'FACESEL'}


def _modifier_warning(mod):
    warnings = getattr(mod, "node_warnings", None)
    return bool(warnings) and any(w.type in {'ERROR', 'WARNING'} for w in warnings)


class MODIFIER_UL_stack(bpy.types.UIList):
    """Max's modifier stack: newest modifier first"""

    def draw_item(self, context, layout, data, item, _icon, _active_data, _active_propname, _index):
        row = layout.row(align=True)
        row.active = item.show_viewport
        row.prop(item, "show_viewport", text="", emboss=False)
        row.prop(item, "name", text="", emboss=False, icon=ModifierAddMenu.MODIFIER_TYPES_TO_ICONS[item.type])
        links = data.get("mx_modifier_links")
        if links and item.name in links:
            # Max shows instanced modifiers in italics; Blender's lists have no italics.
            row.label(text="", icon='LINKED')
        # Maximize's mid-stack Sculpt: what's below must keep its topology.
        if _modifier_warning(item) or item.name in data.get("mx_sculpt_modifiers", ()):
            row.label(text="", icon='ERROR')
        if item.is_active and context.mode == 'EDIT_MESH':
            mode = context.tool_settings.mesh_select_mode
            level = 'VERT' if mode[0] else 'EDGE' if mode[1] else 'FACE'
            row.label(text="", icon=_LEVEL_ICONS[level])

    def filter_items(self, _context, data, propname):
        count = len(getattr(data, propname))
        return [], list(reversed(range(count)))


def _modifier_stack_index_get(ob):
    active = ob.modifiers.active
    return ob.modifiers.find(active.name) if active else -1


def _modifier_stack_index_set(ob, index):
    if 0 <= index < len(ob.modifiers):
        ob.modifiers.active = ob.modifiers[index]
        # Max shows one entry's settings at a time: the selected modifier's panel stays open.
        for i, mod in enumerate(ob.modifiers):
            mod.show_expanded = i == index


# Sub-object levels of a modifier, as Max expands them under its row.
_MODIFIER_LEVELS = {
    'EDIT_POLY': (('VERTEX', "Vertex"), ('EDGE', "Edge"), ('BORDER', "Border"),
                  ('POLYGON', "Polygon"), ('ELEMENT', "Element")),
    'EDIT_SPLINE': (('VERTEX', "Vertex"), ('EDGE', "Segment"), ('POLYGON', "Spline")),
}


def _draw_modifier_stack(layout, context):
    ob = context.object
    if not ob.modifiers:
        return
    col = layout.column(align=True)
    row = col.row()
    row.template_list("MODIFIER_UL_stack", "", ob, "modifiers", ob, "moritz_modifier_stack_index", rows=3)
    side = row.column(align=True)
    side.operator("object.moritz_modifier_toggle", text="", icon='HIDE_OFF').target = 'VIEWPORT'
    side.operator("object.moritz_modifier_toggle", text="", icon='RESTRICT_RENDER_OFF').target = 'RENDER'
    side.separator()
    side.menu("MODIFIER_MT_stack_context", text="", icon='DOWNARROW_HLT')
    active = ob.modifiers.active
    if active is not None:
        # The list is newest first, so up in the list is down in Blender's order.
        side.separator()
        side.operator("object.modifier_move_down", text="", icon='TRIA_UP').modifier = active.name
        side.operator("object.modifier_move_up", text="", icon='TRIA_DOWN').modifier = active.name
    box = col.box()
    box.scale_y = 0.8
    data = ob.data
    box.label(text=data.name if data else ob.name, icon='OUTLINER_DATA_' + ob.type if data else 'OBJECT_DATA')
    active = ob.modifiers.active
    levels = _MODIFIER_LEVELS.get(active.type) if active is not None else None
    if active is not None and active.name in ob.get("mx_sculpt_modifiers", ()):
        # Maximize's mid-stack Sculpt is an Edit Poly underneath, without its levels.
        levels = None
    if levels:
        row = layout.row(align=True)
        for level, text in levels:
            row.operator("object.subobject_level", text=text).level = level
    # Max's button row under the stack.
    row = layout.row(align=True)
    if hasattr(bpy.types, "MAXIMIZE_OT_show_end_result"):
        row.operator("maximize.show_end_result", text="", icon='MODIFIER_ON')
    row.operator("object.moritz_modifier_make_unique", text="Make Unique")
    if active is not None:
        row.operator("object.modifier_remove", text="", icon='TRASH').modifier = active.name


class MODIFIER_MT_stack_context(Menu):
    """Max's stack right-click menu"""
    bl_label = "Modifier Stack"

    def draw(self, context):
        _draw_stack_menu(self.layout, context)


def _draw_stack_menu(layout, context):
    ob = context.object
    active = ob.modifiers.active if ob else None
    if active is not None:
        layout.operator("object.modifier_remove", text="Delete", icon='TRASH').modifier = active.name
    layout.operator("object.moritz_modifier_copy", text="Copy", icon='COPYDOWN')
    layout.operator("object.moritz_modifier_paste", text="Paste", icon='PASTEDOWN').instanced = False
    layout.operator("object.moritz_modifier_paste", text="Paste Instanced", icon='LINKED').instanced = True
    layout.operator("object.moritz_modifier_make_unique", text="Make Unique")
    layout.separator()
    if hasattr(bpy.types, "MAXIMIZE_OT_collapse_to"):
        layout.operator("maximize.collapse_to")
        layout.operator("maximize.collapse_all")
    elif active is not None:
        layout.operator("object.modifier_apply", text="Collapse To").modifier = active.name
    layout.operator("object.moritz_modifier_toggle", text="Off in Viewport").target = 'VIEWPORT'
    layout.operator("object.moritz_modifier_toggle", text="Off in Renderer").target = 'RENDER'


def _draw_list_item_menu(self, context):
    ui_list = getattr(context, "ui_list", None)
    if ui_list is not None and ui_list.bl_idname == "MODIFIER_UL_stack":
        _draw_stack_menu(self.layout, context)


def register():
    from bpy.props import IntProperty
    # Not stored: the stack's selection is the active modifier.
    bpy.types.Object.moritz_modifier_stack_index = IntProperty(
        name="Modifier",
        get=_modifier_stack_index_get,
        set=_modifier_stack_index_set,
    )
    bpy.types.UI_MT_list_item_context_menu.append(_draw_list_item_menu)


def unregister():
    bpy.types.UI_MT_list_item_context_menu.remove(_draw_list_item_menu)
    del bpy.types.Object.moritz_modifier_stack_index


class OBJECT_MT_modifier_add(ModifierAddMenu, Menu):
    bl_label = "Add Modifier"
    bl_options = {'SEARCH_ON_KEY_PRESS'}
    bl_description = "Add a procedural operation/effect to the active object"

    def draw(self, context):
        layout = self.layout
        ob = context.object
        if not ob:
            return
        ob_type = ob.type
        geometry_nodes_supported = ob_type in {
            'EMPTY', 'MESH', 'CURVE', 'CURVES',
            'FONT', 'VOLUME', 'POINTCLOUD', 'GREASEPENCIL'
        }

        if layout.operator_context == 'EXEC_REGION_WIN':
            layout.operator_context = 'INVOKE_REGION_WIN'
            layout.operator(
                "WM_OT_search_single_menu",
                text="Search...",
                icon='VIEWZOOM',
            ).menu_idname = "OBJECT_MT_modifier_add"
            layout.separator()

        layout.operator_context = 'INVOKE_REGION_WIN'

        if ob_type in {'MESH', 'CURVE', 'CURVES', 'FONT', 'SURFACE', 'LATTICE', 'GREASEPENCIL', 'POINTCLOUD'}:
            layout.menu("OBJECT_MT_modifier_add_edit")
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'VOLUME', 'GREASEPENCIL'}:
            layout.menu("OBJECT_MT_modifier_add_generate")
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'LATTICE', 'VOLUME', 'GREASEPENCIL'}:
            layout.menu("OBJECT_MT_modifier_add_deform")
        if ob_type in {'MESH'}:
            layout.menu("OBJECT_MT_modifier_add_normals")
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'LATTICE'}:
            layout.menu("OBJECT_MT_modifier_add_physics")
        if ob_type in {'GREASEPENCIL'}:
            layout.menu("OBJECT_MT_modifier_add_color")

        if geometry_nodes_supported:
            layout.menu_contents("OBJECT_MT_modifier_add_root_catalogs")

        if geometry_nodes_supported:
            layout.separator()
            self.operator_modifier_add(layout, 'NODES')


class OBJECT_MT_modifier_add_edit(ModifierAddMenu, Menu):
    bl_label = "Edit"
    bl_options = {'SEARCH_ON_KEY_PRESS'}

    def draw(self, context):
        layout = self.layout
        ob_type = context.object.type
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'DATA_TRANSFER')
            self.operator_modifier_add(layout, 'EDIT_POLY')
        if ob_type == 'CURVE':
            self.operator_modifier_add(layout, 'EDIT_SPLINE')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'LATTICE'}:
            self.operator_modifier_add(layout, 'MESH_CACHE')
        if ob_type in {'MESH', 'CURVE', 'CURVES', 'FONT', 'POINTCLOUD'}:
            self.operator_modifier_add(layout, 'MESH_SEQUENCE_CACHE')
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'UV_PROJECT')
            self.operator_modifier_add(layout, 'UV_WARP')
            self.operator_modifier_add(layout, 'VERTEX_WEIGHT_EDIT')
            self.operator_modifier_add(layout, 'VERTEX_WEIGHT_MIX')
            self.operator_modifier_add(layout, 'VERTEX_WEIGHT_PROXIMITY')
        if ob_type == 'GREASEPENCIL':
            self.operator_modifier_add(layout, 'GREASE_PENCIL_TEXTURE')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_TIME')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_VERTEX_WEIGHT_PROXIMITY')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_VERTEX_WEIGHT_ANGLE')
        layout.template_modifier_asset_menu_items(catalog_path=self.bl_label)


class OBJECT_MT_modifier_add_generate(ModifierAddMenu, Menu):
    bl_label = "Generate"
    bl_options = {'SEARCH_ON_KEY_PRESS'}

    def draw(self, context):
        layout = self.layout
        ob_type = context.object.type
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
            self.operator_modifier_add_asset(layout, 'Array', icon='MOD_ARRAY')
            self.operator_modifier_add(layout, 'ARRAY', text=n_("Array (Legacy)"), no_icon=True)
            self.operator_modifier_add(layout, 'BEVEL')
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'BOOLEAN')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
            self.operator_modifier_add(layout, 'BUILD')
            self.operator_modifier_add_asset(layout, n_('Curve to Tube'), icon='MOD_CURVE_TO_TUBE')
            self.operator_modifier_add(layout, 'DECIMATE')
            self.operator_modifier_add(layout, 'EDGE_SPLIT')
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'MASK')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
            self.operator_modifier_add(layout, 'MIRROR')
        if ob_type == 'VOLUME':
            self.operator_modifier_add(layout, 'MESH_TO_VOLUME')
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'MULTIRES')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
            self.operator_modifier_add(layout, 'REMESH')
            self.operator_modifier_add_asset(layout, n_('Scatter on Surface'), icon='MOD_SCATTER_ON_SURFACE')
            self.operator_modifier_add(layout, 'SCREW')
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'SKIN')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
            self.operator_modifier_add(layout, 'SOLIDIFY')
            self.operator_modifier_add(layout, 'SUBSURF')
            self.operator_modifier_add(layout, 'TRIANGULATE')
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'VOLUME_TO_MESH')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
            self.operator_modifier_add(layout, 'WELD')
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'WIREFRAME')
        if ob_type == 'GREASEPENCIL':
            self.operator_modifier_add(layout, 'GREASE_PENCIL_ARRAY')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_BUILD')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_DASH')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_ENVELOPE')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_LENGTH')
            self.operator_modifier_add(layout, 'LINEART')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_MIRROR')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_MULTIPLY')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_OUTLINE')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_SIMPLIFY')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_SUBDIV')
        layout.template_modifier_asset_menu_items(catalog_path=self.bl_label, skip_essentials=True)


class OBJECT_MT_modifier_add_deform(ModifierAddMenu, Menu):
    bl_label = "Deform"
    bl_options = {'SEARCH_ON_KEY_PRESS'}

    def draw(self, context):
        layout = self.layout
        ob_type = context.object.type
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'LATTICE'}:
            self.operator_modifier_add(layout, 'ARMATURE')
            self.operator_modifier_add(layout, 'CAST')
            self.operator_modifier_add(layout, 'CURVE')
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'DISPLACE')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'LATTICE'}:
            self.operator_modifier_add(layout, 'HOOK')
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'LAPLACIANDEFORM')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'LATTICE'}:
            self.operator_modifier_add(layout, 'LATTICE')
            self.operator_modifier_add(layout, 'MESH_DEFORM')
            self.operator_modifier_add(layout, 'SHRINKWRAP')
            self.operator_modifier_add(layout, 'SIMPLE_DEFORM')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE'}:
            self.operator_modifier_add(layout, 'SMOOTH')
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'CORRECTIVE_SMOOTH')
            self.operator_modifier_add(layout, 'LAPLACIANSMOOTH')
            self.operator_modifier_add(layout, 'SURFACE_DEFORM')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'LATTICE'}:
            self.operator_modifier_add(layout, 'WARP')
            self.operator_modifier_add(layout, 'WAVE')
        if ob_type == 'VOLUME':
            self.operator_modifier_add(layout, 'VOLUME_DISPLACE')
        if ob_type == 'GREASEPENCIL':
            self.operator_modifier_add(layout, 'GREASE_PENCIL_ARMATURE')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_HOOK')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_LATTICE')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_NOISE')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_OFFSET')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_SHRINKWRAP')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_SMOOTH')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_THICKNESS')
        layout.template_modifier_asset_menu_items(catalog_path=self.bl_label)


class OBJECT_MT_modifier_add_normals(ModifierAddMenu, Menu):
    bl_label = "Normals"
    bl_options = {'SEARCH_ON_KEY_PRESS'}

    def draw(self, context):
        layout = self.layout
        ob_type = context.object.type
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'NORMAL_EDIT')
            self.operator_modifier_add(layout, 'WEIGHTED_NORMAL')
        layout.template_modifier_asset_menu_items(catalog_path=self.bl_label)


class OBJECT_MT_modifier_add_physics(ModifierAddMenu, Menu):
    bl_label = "Physics"
    bl_options = {'SEARCH_ON_KEY_PRESS'}

    def draw(self, context):
        layout = self.layout
        ob_type = context.object.type
        if ob_type == 'MESH':
            self.operator_modifier_add(layout, 'CLOTH')
            self.operator_modifier_add(layout, 'COLLISION')
            self.operator_modifier_add(layout, 'DYNAMIC_PAINT')
            self.operator_modifier_add(layout, 'EXPLODE')
            self.operator_modifier_add(layout, 'FLUID')
            self.operator_modifier_add(layout, 'OCEAN')
            self.operator_modifier_add(layout, 'PARTICLE_INSTANCE')
            self.operator_modifier_add(layout, 'PARTICLE_SYSTEM')
        if ob_type in {'MESH', 'CURVE', 'FONT', 'SURFACE', 'LATTICE'}:
            self.operator_modifier_add(layout, 'SOFT_BODY')
        layout.template_modifier_asset_menu_items(catalog_path=self.bl_label)


class OBJECT_MT_modifier_add_color(ModifierAddMenu, Menu):
    bl_label = "Color"
    bl_options = {'SEARCH_ON_KEY_PRESS'}

    def draw(self, context):
        layout = self.layout
        ob_type = context.object.type
        if ob_type == 'GREASEPENCIL':
            self.operator_modifier_add(layout, 'GREASE_PENCIL_COLOR')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_OPACITY')
            self.operator_modifier_add(layout, 'GREASE_PENCIL_TINT')
        layout.template_modifier_asset_menu_items(catalog_path=self.bl_label)


class AddModifierMenu(Operator):
    bl_idname = "object.add_modifier_menu"
    bl_label = "Add Modifier"

    @classmethod
    def poll(cls, context):
        # NOTE: This operator only exists to add a poll to the add modifier shortcut in the property editor.
        space = context.space_data
        return space and space.type == 'PROPERTIES' and space.context == 'MODIFIER'

    def invoke(self, _context, _event):
        return bpy.ops.wm.call_menu(name="OBJECT_MT_modifier_add_flat")


classes = (
    DATA_PT_modifiers,
    MODIFIER_UL_stack,
    MODIFIER_MT_stack_context,
    OBJECT_MT_modifier_add_flat,
    OBJECT_MT_modifier_add,
    OBJECT_MT_modifier_add_edit,
    OBJECT_MT_modifier_add_generate,
    OBJECT_MT_modifier_add_deform,
    OBJECT_MT_modifier_add_normals,
    OBJECT_MT_modifier_add_physics,
    OBJECT_MT_modifier_add_color,
    AddModifierMenu,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)
