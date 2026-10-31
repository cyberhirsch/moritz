# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

# mNPR render settings. The engine reads these scene properties by name
# (source/blender/draw/engines/mnpr/mnpr_pipeline.cc, `mnpr_setting`), with the same defaults.

import bpy
from bpy.props import BoolProperty, FloatProperty
from bpy.types import Panel


class RENDER_PT_mnpr_strokes(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_label = "Painted Strokes"
    bl_order = -1
    COMPAT_ENGINES = {'MORITZ_MNPR'}

    @classmethod
    def poll(cls, context):
        return context.engine in cls.COMPAT_ENGINES

    def draw_header(self, context):
        self.layout.prop(context.scene, "mnpr_use_strokes", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        scene = context.scene

        col = layout.column()
        col.active = scene.mnpr_use_strokes
        col.prop(scene, "mnpr_stroke_size", text="Size")
        col.prop(scene, "mnpr_stroke_stretch", text="Stretch")
        col.prop(scene, "mnpr_stroke_strength", text="Strength")


classes = (
    RENDER_PT_mnpr_strokes,
)


def register():
    Scene = bpy.types.Scene
    Scene.mnpr_use_strokes = BoolProperty(
        name="Painted Strokes",
        description="Shade surfaces in brush-stroke patches, each lit as one flat facet",
        default=True,
    )
    Scene.mnpr_stroke_size = FloatProperty(
        name="Stroke Size",
        description="Width of a stroke in scene units",
        default=0.1, min=0.001, soft_max=1.0, subtype='DISTANCE', unit='LENGTH',
    )
    Scene.mnpr_stroke_stretch = FloatProperty(
        name="Stroke Stretch",
        description="Length of a stroke relative to its width",
        default=3.0, min=1.0, soft_max=8.0,
    )
    Scene.mnpr_stroke_strength = FloatProperty(
        name="Stroke Strength",
        description="How flat each stroke is shaded: 0 keeps the smooth surface, 1 is fully flat",
        default=1.0, min=0.0, max=1.0, subtype='FACTOR',
    )


def unregister():
    Scene = bpy.types.Scene
    for name in ("mnpr_use_strokes", "mnpr_stroke_size", "mnpr_stroke_stretch", "mnpr_stroke_strength"):
        delattr(Scene, name)


if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
