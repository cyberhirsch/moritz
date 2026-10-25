# Moritz: FBX import settings for files from 3ds Max (custom normals, scene units, no leaf bones).
import bpy
op = bpy.context.active_operator

op.use_manual_orientation = False
op.global_scale = 1.0
op.bake_space_transform = False
op.use_custom_normals = True
op.use_image_search = True
op.use_alpha_decals = False
op.use_anim = True
op.use_custom_props = True
op.ignore_leaf_bones = True
op.force_connect_children = False
op.automatic_bone_orientation = True
op.use_prepost_rot = True
op.axis_forward = '-Z'
op.axis_up = 'Y'
