# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Moritz: the Utilities tab of the Command Panel, as in 3ds Max (Align, Array, Spacing Tool,
Object Paint)."""

from bpy.types import Panel


class PROPERTIES_PT_utilities(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "utilities"
    bl_label = "Utilities"
    bl_options = {'HIDE_HEADER'}

    # Moritz: `utilities_draw(layout, context)`, set by an add-on to draw its tools (Maximize:
    # Align, Array, Spacing Tool, Object Paint). Without it, Blender's nearest commands.
    utilities_draw = None

    def draw(self, context):
        layout = self.layout
        utilities_draw = PROPERTIES_PT_utilities.utilities_draw
        if utilities_draw is not None:
            utilities_draw(layout, context)
            return
        layout.operator_context = 'INVOKE_REGION_WIN'
        col = layout.column(align=True)
        col.operator("object.origin_set", text="Set Origin").type = 'ORIGIN_GEOMETRY'
        col.operator("object.transform_apply", text="Apply Transforms")
        col.operator("object.modifier_add", text="Array Modifier").type = 'ARRAY'


classes = (
    PROPERTIES_PT_utilities,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
