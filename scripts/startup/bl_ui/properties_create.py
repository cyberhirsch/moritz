# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Moritz: the Create tab of the Command Panel, laid out like 3ds Max's Create panel."""

import bpy
from bpy.types import Panel


CATEGORIES = (
    ('GEOMETRY', "Geometry", "Meshes", 'OUTLINER_OB_MESH'),
    ('SHAPES', "Shapes", "Curves and text", 'OUTLINER_OB_CURVE'),
    ('LIGHTS', "Lights", "Lights and light probes", 'OUTLINER_OB_LIGHT'),
    ('CAMERAS', "Cameras", "Cameras", 'OUTLINER_OB_CAMERA'),
    ('HELPERS', "Helpers", "Empties", 'OUTLINER_OB_EMPTY'),
    ('SPACE_WARPS', "Space Warps", "Force fields and lattices", 'FORCE_FORCE'),
    ('SYSTEMS', "Systems", "Armatures", 'OUTLINER_OB_ARMATURE'),
)

# Object types per category: (operator, label, icon, properties).
OBJECT_TYPES = {
    'GEOMETRY': (
        ("mesh.primitive_cube_add", "Cube", 'MESH_CUBE', {}),
        ("mesh.primitive_uv_sphere_add", "UV Sphere", 'MESH_UVSPHERE', {}),
        ("mesh.primitive_ico_sphere_add", "Ico Sphere", 'MESH_ICOSPHERE', {}),
        ("mesh.primitive_cylinder_add", "Cylinder", 'MESH_CYLINDER', {}),
        ("mesh.primitive_cone_add", "Cone", 'MESH_CONE', {}),
        ("mesh.primitive_torus_add", "Torus", 'MESH_TORUS', {}),
        ("mesh.primitive_plane_add", "Plane", 'MESH_PLANE', {}),
        ("mesh.primitive_grid_add", "Grid", 'MESH_GRID', {}),
        ("mesh.primitive_circle_add", "Circle", 'MESH_CIRCLE', {}),
        ("mesh.primitive_monkey_add", "Monkey", 'MESH_MONKEY', {}),
    ),
    'SHAPES': (
        ("curve.primitive_bezier_curve_add", "Bezier", 'CURVE_BEZCURVE', {}),
        ("curve.primitive_bezier_circle_add", "Circle", 'CURVE_BEZCIRCLE', {}),
        ("curve.primitive_nurbs_curve_add", "NURBS Curve", 'CURVE_NCURVE', {}),
        ("curve.primitive_nurbs_path_add", "Path", 'CURVE_PATH', {}),
        ("object.text_add", "Text", 'OUTLINER_OB_FONT', {}),
    ),
    'LIGHTS': (
        ("object.light_add", "Point", 'LIGHT_POINT', {"type": 'POINT'}),
        ("object.light_add", "Sun", 'LIGHT_SUN', {"type": 'SUN'}),
        ("object.light_add", "Spot", 'LIGHT_SPOT', {"type": 'SPOT'}),
        ("object.light_add", "Area", 'LIGHT_AREA', {"type": 'AREA'}),
        ("object.lightprobe_add", "Light Probe", 'LIGHTPROBE_SPHERE', {"type": 'SPHERE'}),
    ),
    'CAMERAS': (
        ("object.camera_add", "Camera", 'OUTLINER_OB_CAMERA', {}),
    ),
    'HELPERS': (
        ("object.empty_add", "Plain Axes", 'EMPTY_AXIS', {"type": 'PLAIN_AXES'}),
        ("object.empty_add", "Arrows", 'EMPTY_ARROWS', {"type": 'ARROWS'}),
        ("object.empty_add", "Cube", 'CUBE', {"type": 'CUBE'}),
        ("object.empty_add", "Sphere", 'SPHERE', {"type": 'SPHERE'}),
        ("object.empty_add", "Single Arrow", 'EMPTY_SINGLE_ARROW', {"type": 'SINGLE_ARROW'}),
        ("object.empty_add", "Circle", 'MESH_CIRCLE', {"type": 'CIRCLE'}),
        ("object.empty_add", "Cone", 'CONE', {"type": 'CONE'}),
        ("object.empty_image_add", "Image", 'IMAGE_DATA', {}),
    ),
    'SPACE_WARPS': (
        ("object.effector_add", "Force", 'FORCE_FORCE', {"type": 'FORCE'}),
        ("object.effector_add", "Wind", 'FORCE_WIND', {"type": 'WIND'}),
        ("object.effector_add", "Vortex", 'FORCE_VORTEX', {"type": 'VORTEX'}),
        ("object.effector_add", "Turbulence", 'FORCE_TURBULENCE', {"type": 'TURBULENCE'}),
        ("object.effector_add", "Drag", 'FORCE_DRAG', {"type": 'DRAG'}),
        ("object.add", "Lattice (FFD)", 'OUTLINER_OB_LATTICE', {"type": 'LATTICE'}),
    ),
    'SYSTEMS': (
        ("object.armature_add", "Bones", 'OUTLINER_OB_ARMATURE', {}),
    ),
}


class CreateButtonsPanel:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "create"


class PROPERTIES_PT_create_category(CreateButtonsPanel, Panel):
    bl_label = "Category"
    bl_options = {'HIDE_HEADER'}

    # Moritz: `subcategory_draw(layout, context, category) -> bool`, set by an add-on to draw a
    # sub-category choice under the icons (Maximize: Standard / Extended Primitives); False falls
    # back to the category's name.
    subcategory_draw = None

    def draw(self, context):
        # Max's row of category icons above the object types.
        row = self.layout.row(align=True)
        row.scale_y = 1.4
        category = context.window_manager.moritz_create_category
        row.prop(context.window_manager, "moritz_create_category", icon_only=True, expand=True)
        subcategory_draw = PROPERTIES_PT_create_category.subcategory_draw
        if subcategory_draw is not None and subcategory_draw(self.layout, context, category):
            return
        self.layout.label(text=context.window_manager.bl_rna.properties["moritz_create_category"].enum_items[
            context.window_manager.moritz_create_category].name)


class PROPERTIES_PT_create(CreateButtonsPanel, Panel):
    bl_label = "Object Type"

    # Moritz: `object_type_draw(layout, context, category) -> bool`, set by an add-on to draw its own
    # object types for a category (Maximize: parametric primitives and shapes); False falls back to
    # Blender's object types below.
    object_type_draw = None

    def draw(self, context):
        layout = self.layout
        category = context.window_manager.moritz_create_category
        object_type_draw = PROPERTIES_PT_create.object_type_draw
        if object_type_draw is not None and object_type_draw(layout, context, category):
            return

        layout.operator_context = 'INVOKE_REGION_WIN'
        grid = layout.grid_flow(row_major=True, columns=2, even_columns=True, align=True)
        for idname, text, icon, props in OBJECT_TYPES[category]:
            op = grid.operator(idname, text=text, icon=icon)
            for key, value in props.items():
                setattr(op, key, value)


class PROPERTIES_PT_create_name(CreateButtonsPanel, Panel):
    bl_label = "Name and Color"

    def draw(self, context):
        layout = self.layout
        ob = context.active_object
        if ob is None:
            layout.label(text="Nothing selected")
            return
        row = layout.row(align=True)
        row.prop(ob, "name", text="")
        row.prop(ob, "color", text="")


def register():
    from bpy.props import EnumProperty
    bpy.types.WindowManager.moritz_create_category = EnumProperty(
        name="Category",
        description="Kind of object to create",
        items=[(ident, name, desc, icon, i) for i, (ident, name, desc, icon) in enumerate(CATEGORIES)],
    )


def unregister():
    del bpy.types.WindowManager.moritz_create_category


classes = (
    PROPERTIES_PT_create_category,
    PROPERTIES_PT_create,
    PROPERTIES_PT_create_name,
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
