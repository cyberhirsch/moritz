# Moritz: FBX export settings for 3ds Max (smoothing groups, scene units, no leaf bones).
import bpy
op = bpy.context.active_operator

op.use_selection = False
op.use_visible = False
op.use_active_collection = False
op.global_scale = 1.0
op.apply_unit_scale = True
op.apply_scale_options = 'FBX_SCALE_UNITS'
op.use_space_transform = True
op.bake_space_transform = False
op.object_types = {'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER'}
op.use_mesh_modifiers = True
op.mesh_smooth_type = 'SMOOTH_GROUP'
op.use_subsurf = False
op.use_mesh_edges = False
op.use_tspace = False
op.use_triangles = False
op.use_custom_props = False
op.add_leaf_bones = False
op.primary_bone_axis = 'Y'
op.secondary_bone_axis = 'X'
op.armature_nodetype = 'NULL'
op.bake_anim = True
op.path_mode = 'AUTO'
op.embed_textures = False
op.axis_forward = '-Z'
op.axis_up = 'Y'
