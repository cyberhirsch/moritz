# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Moritz: the modifier list, Max names and search keywords.

Each entry adds a Blender modifier (with preset settings for Max's variants: Bend, Taper, Twist
and Stretch are Simple Deform) or runs an add-on's operator. The Add Modifier menu shows Max's names
in the Max and Moritz name schemes (the Maximize add-on sets `name_scheme`), and a new modifier is
named after its list entry. Search Modifiers matches the Max name, the Blender name and a few words
for what the modifier does, so "bend" finds Simple Deform and "solidify" finds Shell.

Only modifier names change, so files open in stock Blender unchanged.
"""

import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

# (Max label, Blender modifier type or None, preset settings, keywords). The Blender label comes
# from the modifier type. Entries without a Max name in the list keep Blender's.
MAX_ENTRIES = (
    ("Array", 'ARRAY', {}, "copies duplicate repeat linear"),
    ("Attribute Transfer", 'DATA_TRANSFER', {}, "copy data normals weights uv"),
    ("Bend", 'SIMPLE_DEFORM', {"deform_method": 'BEND'}, "curve arc deform"),
    ("Boolean", 'BOOLEAN', {}, "union subtract intersect difference cut"),
    ("Camera Map", 'UV_PROJECT', {}, "uv projection projector"),
    ("Cap Holes", 'CAP_HOLES', {}, "fill close holes borders quad grid"),
    ("Chamfer", 'BEVEL', {}, "bevel round edges fillet"),
    ("Conform", 'SHRINKWRAP', {}, "shrinkwrap project snap surface"),
    ("Displace", 'DISPLACE', {}, "height map texture offset"),
    ("Edit Normals", 'NORMAL_EDIT', {}, "custom normals"),
    ("FFD", 'LATTICE', {}, "lattice free form deformation cage box"),
    ("Lathe", 'SCREW', {}, "screw revolve spin turn helix spring thread"),
    ("Lattice", 'WIREFRAME', {}, "wireframe struts edges"),
    ("Linked XForm", 'HOOK', {}, "hook control object"),
    ("Mesh Clean", 'MESH_CLEAN', {}, "cleanup weld straight loose degenerate merge"),
    ("Mirror", 'MIRROR', {}, "symmetry flip"),
    ("Normal", 'MAX_NORMAL', {}, "flip unify recalculate face direction"),
    ("Path Deform", 'CURVE', {}, "curve follow spline"),
    ("Point Cache", 'MESH_CACHE', {}, "cache alembic mdd pc2 animation"),
    ("ProOptimizer", 'PRO_OPTIMIZER', {}, "decimate reduce optimize polygons collapse"),
    ("Push", 'DISPLACE', {"direction": 'NORMAL', "strength": 0.0}, "inflate normals offset"),
    ("Quadify Mesh", 'QUADIFY_MESH', {}, "quads remesh quadriflow retopo"),
    ("Relax", 'LAPLACIANSMOOTH', {}, "smooth laplacian soften"),
    ("Retopology", 'REMESH', {}, "remesh quads voxel retopo"),
    ("Ripple", 'WAVE', {}, "wave radial rings water"),
    ("Shell", 'SOLIDIFY', {}, "solidify thickness"),
    ("Skin", 'ARMATURE', {}, "armature bones rig skinning deform"),
    ("Skin Wrap", 'SURFACE_DEFORM', {}, "surface deform cage bind"),
    ("Spherify", 'CAST', {}, "cast sphere round"),
    ("Stretch", 'SIMPLE_DEFORM', {"deform_method": 'STRETCH'}, "squash scale deform"),
    ("Subdivide", 'SUBSURF', {"subdivision_type": 'SIMPLE'}, "tessellate split simple"),
    ("Symmetry", 'MIRROR', {"use_bisect_axis": (True, False, False)}, "mirror bisect half"),
    ("Taper", 'SIMPLE_DEFORM', {"deform_method": 'TAPER'}, "scale cone narrow deform"),
    ("TurboSmooth", 'SUBSURF', {}, "subdivision surface meshsmooth opensubdiv nurms catmull"),
    ("Twist", 'SIMPLE_DEFORM', {"deform_method": 'TWIST'}, "rotate spiral deform"),
    ("VertexPaint", 'VERTEX_PAINT', {}, "vertex colors color attribute paint"),
    ("UVW Xform", 'UV_WARP', {}, "uv warp offset scale rotate"),
    ("Vertex Weld", 'WELD', {}, "weld merge distance"),
    ("Wave", 'WAVE', {}, "ripple linear water"),
    ("Weighted Normals", 'WEIGHTED_NORMAL', {}, "custom normals face area"),
)

# In the Max schemes, Blender's modifiers whose name Max uses for another one.
MAX_RENAMES = {
    'SKIN': "Skin (Blender)",
    'SMOOTH': "Smooth (Blender)",
}

# Entries that run an operator: (Max label, Blender label, operator, keywords, object types).
OPERATOR_ENTRIES = (
    ("Smooth", "Smooth by Angle", "object.shade_auto_smooth", "auto smooth angle sharp edges smoothing groups",
     ('MESH',)),
)

# Keywords for Blender's modifiers that have no Max entry above.
BLENDER_KEYWORDS = {
    'BUILD': "grow appear animate",
    'EDGE_SPLIT': "sharp hard edges split",
    'MASK': "delete hide vertex group",
    'MULTIRES': "sculpt subdivision multires",
    'SKIN': "skeleton edges thickness envelope",
    'TRIANGULATE': "triangles tris",
    'LAPLACIANDEFORM': "deform anchors",
    'LATTICE': "ffd free form deformation cage",
    'MESH_DEFORM': "cage deform",
    'CORRECTIVE_SMOOTH': "relax smooth corrective",
    'WARP': "deform pull",
    'EXPLODE': "shatter break particles",
    'OCEAN': "water waves sea",
    'NODES': "geometry nodes",
    'DECIMATE': "reduce optimize polygons collapse planar",
}

# Add-on entries (Max label, operator idname, keywords, object types), from `register_entry`.
_addon_entries = []


def name_scheme():
    """'BLENDER', 'MAX' or 'MORITZ'; the Maximize add-on replaces this."""
    return 'BLENDER'


def register_entry(label, operator, keywords="", object_types=('MESH',)):
    """An add-on's own modifier (it adds it with `operator`) in the list and the search."""
    unregister_entry(operator)
    _addon_entries.append((label, operator, keywords, tuple(object_types)))


def unregister_entry(operator):
    _addon_entries[:] = [e for e in _addon_entries if e[1] != operator]


def _type_items():
    return {it.identifier: it for it in bpy.types.Modifier.bl_rna.properties["type"].enum_items}


# Modifier types that work on more than meshes (Blender's own check is in C).
_CURVE_TYPES = {
    'ARRAY', 'BEVEL', 'BOOLEAN', 'BUILD', 'DECIMATE', 'EDGE_SPLIT', 'NODES', 'MASK', 'MIRROR',
    'REMESH', 'SCREW', 'SOLIDIFY', 'SUBSURF', 'TRIANGULATE', 'WELD', 'WIREFRAME', 'ARMATURE',
    'CAST', 'CURVE', 'DISPLACE', 'HOOK', 'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP', 'SIMPLE_DEFORM',
    'SMOOTH', 'WARP', 'WAVE', 'EDIT_SPLINE', 'MESH_CACHE', 'UV_PROJECT', 'UV_WARP', 'WEIGHTED_NORMAL',
}
_LATTICE_TYPES = {'ARMATURE', 'CAST', 'CURVE', 'HOOK', 'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP',
                  'SIMPLE_DEFORM', 'WARP', 'WAVE', 'MESH_CACHE', 'NODES'}
_SKIP_TYPES = {'PARTICLE_SYSTEM', 'COLLISION', 'SURFACE', 'FLUID', 'SOFT_BODY', 'CLOTH',
               'DYNAMIC_PAINT', 'PARTICLE_INSTANCE'}


def _supports(ob, mtype):
    if mtype.startswith("GREASE_PENCIL") or mtype == 'LINEART':
        return ob.type == 'GREASEPENCIL'
    if mtype in {'EDIT_POLY'}:
        return ob.type == 'MESH'
    if mtype in {'VOLUME_DISPLACE', 'VOLUME_TO_MESH'}:
        return ob.type == 'VOLUME'
    if ob.type == 'MESH':
        return mtype not in {'EDIT_SPLINE'}
    if ob.type in {'CURVE', 'FONT', 'SURFACE'}:
        return mtype in _CURVE_TYPES
    if ob.type == 'LATTICE':
        return mtype in _LATTICE_TYPES
    if ob.type == 'CURVES':
        return mtype == 'NODES'
    return False


def entries(ob, scheme=None):
    """The list for `ob`: (key, label, other name, keywords) per entry, sorted by label. `key` is
    "TYPE", "TYPE:<Max label>" for a preset, or "OP:<idname>"."""
    scheme = scheme or name_scheme()
    max_names = scheme in {'MAX', 'MORITZ'}
    items = _type_items()
    out = []
    covered = set()
    by_type = {}
    for label, mtype, _preset, words in MAX_ENTRIES:
        by_type.setdefault(mtype, []).append((label, words))
    for mtype, it in items.items():
        if mtype in _SKIP_TYPES or not _supports(ob, mtype):
            continue
        blender = bpy.app.translations.pgettext_iface(it.name, "Modifier")
        rows = by_type.get(mtype, ())
        if max_names and rows:
            for label, words in rows:
                key = mtype if label == rows[0][0] else mtype + ":" + label
                out.append((key, label, it.name, words))
            covered.add(mtype)
        else:
            others = ", ".join(label for label, _w in rows if label != it.name)
            words = " ".join(w for _l, w in rows) + " " + BLENDER_KEYWORDS.get(mtype, "")
            if max_names and mtype in MAX_RENAMES:
                others, blender = blender, MAX_RENAMES[mtype]
            out.append((mtype, blender, others, words.strip()))
    for max_label, blender_label, op, words, types in OPERATOR_ENTRIES:
        if ob.type in types and _operator(op) is not None:
            label, other = (max_label, blender_label) if max_names else (blender_label, max_label)
            out.append(("OP:" + op, label, other, words))
    for label, op, words, types in _addon_entries:
        if ob.type in types and _operator(op) is not None:
            out.append(("OP:" + op, label, "", words))
    out.sort(key=lambda e: e[1].lower())
    return out


def _operator(idname):
    module, name = idname.split(".")
    op = getattr(getattr(bpy.ops, module, None), name, None)
    try:
        op.get_rna_type()
    except (AttributeError, KeyError):
        return None
    return op


def _preset(mtype, label):
    for entry_label, entry_type, preset, _words in MAX_ENTRIES:
        if entry_type == mtype and entry_label == label:
            return preset
    return {}


def add(context, key, label):
    """Add the entry `key` to the active object; returns the operator result."""
    if key.startswith("OP:"):
        op = _operator(key[3:])
        if op is None:
            return {'CANCELLED'}
        return op('INVOKE_DEFAULT')
    mtype, _sep, preset_label = key.partition(":")
    ob = context.object
    before = set(ob.modifiers)
    result = bpy.ops.object.modifier_add(type=mtype)
    if 'FINISHED' not in result:
        return result
    new = [m for m in ob.modifiers if m not in before]
    if not new:
        return result
    mod = new[0]
    preset = _preset(mtype, preset_label or label)
    for prop, value in preset.items():
        try:
            setattr(mod, prop, value)
        except (AttributeError, TypeError, ValueError):
            pass
    if name_scheme() in {'MAX', 'MORITZ'}:
        mod.name = label
    return result


def _search_items(self, context):
    ob = context.object
    if ob is None:
        return [('NONE', "No Object", "")]
    items = []
    for i, (key, label, other, words) in enumerate(entries(ob)):
        # The hint shares the popup's width with the name: the other scheme's name first, then as many
        # keywords as fit.
        hint = other
        for word in words.split():
            if len(label) + len(hint) + len(word) + 1 > 34:
                break
            if word.lower() not in hint.lower():
                hint = (hint + " " + word).strip()
        # Text after "|" is drawn grey on the right and is searched too.
        name = label + ("|" + hint if hint else "")
        items.append((key + "|" + label, name, "", i))
    _search_items.cache = items
    return items


class OBJECT_OT_moritz_modifier_search(Operator):
    """Find a modifier by its Max name, its Blender name or what it does"""
    bl_idname = "object.moritz_modifier_search"
    bl_label = "Search Modifiers"
    bl_property = "entry"
    bl_options = {'REGISTER', 'UNDO'}

    entry: EnumProperty(name="Modifier", items=_search_items)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def invoke(self, context, _event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        key, _sep, label = self.entry.partition("|")
        if key == 'NONE':
            return {'CANCELLED'}
        return add(context, key, label)


class OBJECT_OT_moritz_modifier_add_entry(Operator):
    """Add this modifier"""
    bl_idname = "object.moritz_modifier_add_entry"
    bl_label = "Add Modifier"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    key: bpy.props.StringProperty(options={'SKIP_SAVE'})
    label: bpy.props.StringProperty(options={'SKIP_SAVE'})

    @classmethod
    def description(cls, _context, props):
        key = props.key
        if key.startswith("OP:"):
            op = _operator(key[3:])
            return op.get_rna_type().description if op is not None else ""
        it = _type_items().get(key.partition(":")[0])
        if it is None:
            return ""
        text = bpy.app.translations.pgettext_tip(it.description)
        if name_scheme() == 'MORITZ' and it.name != props.label:
            text += "\nBlender: " + it.name
        return text

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        return add(context, self.key, self.label)


def draw_flat(layout, context):
    """The flat list in the Max and Moritz schemes: every entry by Max name, in columns."""
    ob = context.object
    rows = entries(ob)
    per_column = 18
    flow = layout.row()
    col = None
    for i, (key, label, _other, _words) in enumerate(rows):
        if i % per_column == 0:
            col = flow.column()
        op = col.operator("object.moritz_modifier_add_entry", text=label, translate=False)
        op.key = key
        op.label = label


classes = (
    OBJECT_OT_moritz_modifier_search,
    OBJECT_OT_moritz_modifier_add_entry,
)
