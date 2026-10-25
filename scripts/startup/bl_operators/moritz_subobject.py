# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

# Moritz: Max's sub-object levels (keys 1-6) without the Maximize add-on. The add-on's
# `maximize.subobject` replaces this in the Max keymap when it is enabled (it adds Border and
# Element picking and Edit Poly modifiers); here Border works as Edge and Element as Polygon,
# because Blender has no such select modes.

import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

_SELECT_MODE = {
    'VERTEX': 'VERT',
    'EDGE': 'EDGE',
    'BORDER': 'EDGE',
    'POLYGON': 'FACE',
    'ELEMENT': 'FACE',
}


def _current_level(context, ob):
    if ob.mode != 'EDIT':
        return 'OBJECT'
    if ob.type != 'MESH':
        return 'VERTEX'
    vert, edge, face = context.tool_settings.mesh_select_mode
    return 'VERTEX' if vert else 'EDGE' if edge else 'POLYGON' if face else 'OBJECT'


class OBJECT_OT_subobject_level(Operator):
    """Go to a sub-object level as in Max: 1 Vertex, 2 Edge, 3 Border, 4 Polygon, 5 Element, """ \
        """6 back to the object; the key of the current level also goes back"""
    bl_idname = "object.subobject_level"
    bl_label = "Sub-Object Level"
    bl_options = {'REGISTER', 'UNDO'}

    level: EnumProperty(
        name="Level",
        items=(
            ('VERTEX', "Vertex", ""),
            ('EDGE', "Edge", ""),
            ('BORDER', "Border", "Edge selection (open borders need the Maximize add-on)"),
            ('POLYGON', "Polygon", ""),
            ('ELEMENT', "Element", "Face selection (whole elements need the Maximize add-on)"),
            ('OBJECT', "Object", "Back to the object"),
        ),
    )

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob is not None and ob.type in {'MESH', 'CURVE'} and ob.mode in {'OBJECT', 'EDIT'}

    def execute(self, context):
        ob = context.active_object
        level = self.level
        # The key of the level you are at takes you back to the object, as in Max.
        if level != 'OBJECT' and ob.mode == 'EDIT' and _current_level(context, ob) == level and \
                level not in {'BORDER', 'ELEMENT'}:
            level = 'OBJECT'
        if level == 'OBJECT':
            if ob.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            return {'FINISHED'}
        if ob.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
        if ob.type == 'MESH':
            bpy.ops.mesh.select_mode(type=_SELECT_MODE[level])
        return {'FINISHED'}


classes = (
    OBJECT_OT_subobject_level,
)
