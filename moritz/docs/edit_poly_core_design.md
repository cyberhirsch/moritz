# Edit Poly modifier in core: design note

Status: stages 0-2 implemented (see the end of this note); stages 3-5 open. Based on reading the Moritz tree (Blender 5.3) and the
add-on prototype `G:\Code\Maximize\maximize\edit_poly.py`.

## 0. The prototype in one paragraph

A Geometry Nodes group reads two hidden helper objects: **Base** (the modifier input at the last
edit) and **Edited** (the edited result, with an int point attribute `mx_orig` = index of the base
vertex each vertex came from, -1 for new ones). If the input vertex count equals Base's, each
edited vertex is offset by `input[orig] - base[orig]`; otherwise the edit is frozen and
`mx_topology_changed` is stored for the panel warning. Editing re-bases (Base := current input,
Edited := current result) and swaps the object for the Edited stand-in in Edit Mode.

Weak points a native modifier fixes: two helper objects per modifier, a full extra copy of the
base mesh, vertex-count-only topology check, the object swap (selection, outliner, transform,
other modes all see a different object), and re-evaluation of the stack by toggling
`show_viewport`.

## 1. Where `eModifierType_EditPoly` plugs in

Facts from the tree:
- `DNA_modifier_defaults.h` / `dna_defaults.cc` no longer exist in this fork. Defaults are C++
  default member initializers in `DNA_modifier_types.h`, applied by `init_data` with
  `INIT_DEFAULT_STRUCT_AFTER(md, modifier)` (see `MOD_correctivesmooth.cc:init_data`).
- `BKE_modifier.cc:modifier_types[NUM_MODIFIER_TYPES]` is a sparse pointer array;
  `BKE_modifier_get_info` and `space_buttons.cc` (panel registration loop) both tolerate null
  entries, so a gap in the enum is safe.

Files to change:
- `makesdna/DNA_modifier_types.h`
  - `enum ModifierType`: add `eModifierType_EditPoly`. Use a **high, fixed value** (e.g. 200,
    with a comment "Moritz only") rather than 87, so a future upstream type cannot collide.
    `NUM_MODIFIER_TYPES` then follows it.
  - new `struct EditPolyModifierData` (see section 2) and its flag enum.
  - optional new `ModifierFlag` bit `eModifierFlag_MxEditing` (session marker, section 3).
- `modifiers/intern/MOD_edit_poly.cc` (new): `ModifierTypeInfo modifierType_EditPoly`, layout as
  in `MOD_correctivesmooth.cc` (idname, name, struct_name, struct_size, srna, type, flags, icon,
  then the callback list ending in `blend_write`, `blend_read`, `foreach_cache`,
  `foreach_working_space_color`). Needed callbacks: `init_data`, `copy_data`, `free_data`,
  `modify_mesh`, `required_data_mask` (keep `CD_ORIGINDEX`), `foreach_ID_link` (if a Mesh ID is
  used), `update_depsgraph`, `free_runtime_data`, `panel_register`, `blend_write`, `blend_read`.
  - `type = ModifierTypeType::Constructive`; flags `AcceptsMesh | SupportsMapping |
    SupportsEditmode | EnableInEditmode`.
- `modifiers/MOD_modifiertypes.hh`: `extern ModifierTypeInfo modifierType_EditPoly;`
- `modifiers/intern/MOD_util.cc:modifier_type_init`: `INIT_TYPE(EditPoly);`
- `modifiers/CMakeLists.txt`: add `intern/MOD_edit_poly.cc`.
- `makesrna/intern/rna_modifier.cc`
  - `rna_enum_object_modifier_type_items[]`: `{eModifierType_EditPoly, "EDIT_POLY", ICON_..., "Edit Poly", ""}` under the Edit group.
  - new `rna_def_modifier_edit_poly(brna)`, called from `RNA_def_modifier`. `rna_Modifier_refine`
    needs no change (it uses `mti->srna`). `RNA_EditPolyModifier` comes from the generated
    `RNA_prototypes.hh`.
- `scripts/startup/bl_ui/properties_data_modifier.py:OBJECT_MT_modifier_add_edit`:
  `self.operator_modifier_add(layout, 'EDIT_POLY')` (or let the Maximize add-on draw it).
- `blenkernel/intern/modifier.cc`
  - `modifier_struct_size` and `BKE_modifier_blend_read_data`: compatibility stub handling
    (section 6).
- `blenkernel/intern/mesh_data_update.cc:editbmesh_calc_modifiers` and
  `blenkernel/intern/modifier.cc:BKE_modifiers_get_cage_index`: session-aware stack start
  (section 3).
- `editors/mesh/editmesh_utils.cc:EDBM_mesh_load_ex`, `editors/object/object_edit.cc`
  (`ED_object_editmode_enter_ex`, `editmode_load_free_ex`): session enter/exit (section 3).
- `editors/object/object_modifier.cc`: operators `OBJECT_OT_edit_poly_rebase`,
  `OBJECT_OT_edit_poly_edit` (enter session) or keep them in the add-on calling RNA functions.
- `editors/undo/ed_undo.cc:ED_undo_object_editmode_restore_helper` (section 5).
- `BKE_moritz_version.h`: bump for the versioning hook.

## 2. How to store the edit

Options:
- **A. Prototype layout**: full base mesh + full edited mesh with `mx_orig`. Two meshes, base
  only used for its positions and counts.
- **B. Proposed delta**: moved positions keyed by original vertex index, plus a stored result
  mesh once topology is edited.
- **C. Recommended hybrid** (B, made concrete):

```
struct EditPolyModifierData {
  ModifierData modifier;
  EditPolyModifierMode mode;   /* DEFORM or TOPOLOGY */
  int flag;                    /* e.g. topology-changed (runtime mirror), show-end-result */
  /* Fingerprint of the input at the last re-base. */
  int base_verts_num, base_edges_num, base_faces_num, base_corners_num;
  uint64_t base_topology_hash;
  /* DEFORM mode: per input-vertex offset, length base_verts_num. */
  float (*offsets)[3];  const ImplicitSharingInfoHandle *offsets_sharing_info;
  /* TOPOLOGY mode: input positions at re-base (length base_verts_num) + result mesh. */
  float (*base_positions)[3];  const ImplicitSharingInfoHandle *base_positions_sharing_info;
  Mesh *result;                /* Mesh ID, carries int point attribute "mx_orig". */
  void *_pad_runtime;          /* use ModifierData.runtime for caches */
};
```

- **DEFORM mode** (no topology edits yet, the common Max case "move some verts"): output is the
  input mesh with `positions[i] += offsets[i]`. All input attributes (UVs, weights, attributes
  from GN below) stay live. Costs one float3 array.
- **TOPOLOGY mode** (any vert/edge/face added, removed or reconnected): output is `result`, with
  `pos[i] += input_pos[orig[i]] - base_positions[orig[i]]` for `orig[i] >= 0` while the
  fingerprint matches. Same math as the prototype, but the base is only a float3 array, not a
  mesh.
- Store `result` as a **Mesh ID** referenced by the modifier, not as embedded CustomData:
  reuses Mesh read/write/undo, the attribute API and Python access; it needs `foreach_ID_link`
  (user count) and a depsgraph relation (`DEG_add_generic_id_relation`, as `MOD_nodes.cc` does
  for its IDs). Name it `"<object> Edit Poly"`; mark it so UI lists can hide it. Embedded
  CustomData (as `MOD_meshdeform` / `MOD_surfacedeform` do with bind arrays) is possible later
  but means re-implementing mesh IO for four domains.
- Store arrays with implicit sharing (`writer->write_shared` / `BLO_read_shared`,
  `implicit_sharing::copy_shared_pointer` in `copy_data`), exactly like
  `MOD_correctivesmooth.cc:blend_write/blend_read/copy_data`. The CoW copy and memfile undo then
  share the data instead of copying it.
- Switch DEFORM -> TOPOLOGY at session exit when the edited BMesh is not the input topology
  (section 4). Never switch back automatically.

Recommendation: C. It is smaller than A for the common case, keeps live attributes in DEFORM
mode, and in TOPOLOGY mode stores one mesh plus one array instead of two meshes.

## 3. Editing the evaluated mesh in Edit Mode

What the machinery does today:
- Edit Mode always edits `ob->data`: `EDBM_mesh_make` builds the BMesh from `ob->data` and hangs
  it on `Mesh.runtime->edit_mesh`; `BKE_editmesh_from_object` returns that.
- `editbmesh_calc_modifiers` wraps the BMesh (`BKE_mesh_wrapper_from_editmesh`) and runs the
  **whole** stack (including virtual shape-key/armature modifiers from
  `BKE_modifiers_get_virtual_modifierlist`). The cage is the result at `cageIndex`
  (`BKE_modifiers_get_cage_index`: last enabled modifier with `OnCage`, stopping at the first
  one without mapping). The cage maps back to BMesh elements via `CD_ORIGINDEX`
  (`cage_mesh_or_fallback`). "On cage" only changes what is drawn and snapped to; the edited
  data is still the original mesh. There is no way today to edit a modifier's output.
- Two existing hooks help:
  - `EDBM_mesh_make_from_mesh(ob, src_mesh, ...)` builds the edit BMesh from an arbitrary mesh
    while attaching it to `ob->data` (used by `node_group_operator.cc`).
  - `EDBM_mesh_load_ex` is the single place where the BMesh is written back
    (`BM_mesh_bm_to_me`), and every load path goes through it: `editmode_load_free_ex`,
    `ED_editors_flush_edits` (save, memfile undo, render), `object_hook.cc`,
    `object_relations.cc`, `rna_object.cc`.
- Precedent for "evaluation writes to the original modifier": `MOD_correctivesmooth.cc`
  (`bind_coords_num == -1`, `DEG_is_active`, `BKE_modifier_get_original`) and
  `MOD_meshdeform.cc` (`bindfunc`). Use the same pattern to capture the input on re-base.

What must be new ("Edit Poly session"):
1. **Session marker**: `eModifierFlag_MxEditing` on the modifier (DNA, so memfile undo and save
   restore it). At most one per object.
2. **Input cache**: the evaluated Edit Poly modifier keeps its last input mesh in
   `ModifierData.runtime` (implicitly shared `GeometrySet`, cheap). Entering the session reads it
   through `BKE_modifier_get_evaluated`; no second stack evaluation, no `show_viewport` toggling.
3. **Enter** (`ED_object_editmode_enter_ex` branch): re-base (fingerprint + base positions from
   the cached input), build the current output (input + edit), add/refresh the `mx_orig` int
   layer, then `EDBM_mesh_make_from_mesh(ob, output, ...)`. The object stays the object.
4. **Evaluate** (`editbmesh_calc_modifiers` branch): if a modifier on the object has
   `MxEditing`, skip the virtual modifiers and every modifier up to and including it; start the
   loop at the next modifier with the BMesh wrapper as input. `BKE_modifiers_get_cage_index`
   gets the same start index. Modifiers above then work as today (cage, on-cage, mapping).
   A "Show end result" toggle = evaluate or skip the modifiers above.
5. **Exit / load** (`EDBM_mesh_load_ex` branch): convert the BMesh into a temporary Mesh
   (`BM_mesh_bm_to_me` with `calc_object_remap = false`, no shape keys), then write it into the
   modifier (DEFORM offsets or TOPOLOGY `result`), never into `ob->data`. Tag
   `ID_RECALC_GEOMETRY`. Clear `MxEditing` only on real exit, not on flush.
6. **Disallow in session**: shape-key editing, switching to sculpt/paint modes, multi-object
   edit with this object, modifier apply/reorder of the edited modifier and those below.

Risk: code that reads `ob->data` while in Edit Mode and assumes it matches the BMesh (shape-key
panels, `mesh.vertices` from Python, some IO exporters calling `ED_editors_flush_edits`). Because
the flush is routed through `EDBM_mesh_load_ex`, data cannot be written to the wrong place, but
such code may show stale data during a session. Audit with `grep EDBM_mesh_load\|edit_mesh`.

## 4. Topology-change detection and fallback

- Fingerprint the input at re-base: element counts plus a hash of `edge_verts` and
  `corner_verts`/`face_offsets` (`BLI_hash`/xxhash). Per evaluation, first compare the
  implicit-sharing pointers of those arrays with the ones seen last time (cached in runtime);
  only rehash when they differ. Counts-only (prototype) misses e.g. a Weld+Subdivide that keeps
  the count.
- DEFORM mode, fingerprint mismatch: if only vertex count is equal, keep applying offsets by
  index (Max is index-based too) and warn; if counts differ, apply none and warn.
- TOPOLOGY mode, mismatch: output `result` unchanged (edit frozen), no offsets,
  `BKE_modifier_set_warning(ob, md, "Topology below changed: edits kept as they were")`. This
  replaces the `mx_topology_changed` attribute.
- Recovery operator "Re-base": remap `mx_orig` to the nearest new input vertex
  (`BLI_kdtree_3d`, as the prototype's `_remap_nearest`), then rebuild the fingerprint.
- Session exit DEFORM -> TOPOLOGY test: BMesh counts equal to the base counts, `mx_orig` is the
  identity (`orig[i] == i`, no -1, no duplicates; new verts copy `mx_orig` from their source via
  CustomData interpolation, so duplicates reveal extrusions) and the edge/corner hash matches.
  Otherwise switch to TOPOLOGY.

## 5. Undo and file round trip

- Memfile (global) undo: the modifier struct, its shared arrays and the `result` Mesh ID are
  regular DNA; implicit sharing means unchanged arrays are not duplicated per step.
- Edit-mesh undo (`editmesh_undo.cc`) stores and restores the BMesh only, so it works unchanged
  inside a session. `mesh_undosys_step_decode` calls `ED_undo_object_editmode_restore_helper`,
  which enters Edit Mode on the object; that enter path must honour `MxEditing` (it will, if the
  branch lives in `ED_object_editmode_enter_ex`) and must skip the re-base (the undo step
  supplies the BMesh).
- Undo across the session boundary (undo the "enter"): the memfile step before it has
  `MxEditing` cleared, so the object comes back in Object Mode with the old edit.
- Save during a session: `ED_editors_flush_edits` -> `EDBM_mesh_load_ex` -> modifier. On load,
  `ED_editors_init` re-enters Edit Mode for objects saved in it (verify in this fork); the flag
  makes that re-entry a session again.
- Linked data / overrides: follow `MOD_correctivesmooth.cc:blend_write` (skip heavy data for
  non-local override modifiers). Editing is only allowed on local modifiers.

## 6. Stock Blender opening a file with this modifier

What stock 5.3 does (read path):
- `BKE_modifier_blend_read_data` reads the list with `BLO_read_struct_list_with_type_size`.
- If the **struct** (`EditPolyModifierData`) is not in stock SDNA, its block gets
  `SDNA_CMP_REMOVED`; `readfile.cc:read_struct` returns null, the block is never put in the
  data map, and `BLO_read_struct_list_with_type_size` hits `newdataadr_entry == nullptr` and
  **breaks**. Result: the Edit Poly modifier **and every modifier above it are silently
  dropped**; modifiers below survive. Saving then makes the loss permanent.
- If only the **type number** is unknown but the struct is known, the modifier becomes
  `eModifierType_None` (`if (mti == nullptr) md->type = eModifierType_None;`), stays in the
  list, is disabled (`MOD_none.cc:is_disabled` returns true), and `system_properties` are read
  and written back on save (`BKE_modifier_blend_write` writes them before the struct).
- A stray `result` Mesh ID would survive as an orphan until the next save.

Recommended fallback:
1. **Compatibility stub on disk** (required): `MOD_edit_poly.cc:blend_write` writes the modifier
   as a plain `ModifierData` block, with the payload as IDProperties in `md->system_properties`:
   `mx_type = "EDIT_POLY"`, `mode`, fingerprint, `offsets`/`base_positions` as float
   `IDP_ARRAY`, `result` as `IDP_ID`. Stock then keeps the stack intact (the stub reads as a
   disabled None modifier, the modifiers above still evaluate, on the unedited input), keeps the
   Mesh alive through the `IDP_ID` user, and writes everything back on save.
   - Moritz read side: `modifier_struct_size` returns `sizeof(ModifierData)` for
     `eModifierType_EditPoly`; `BKE_modifier_blend_read_data` reallocates into a full
     `EditPolyModifierData` and fills it from the properties (pattern:
     `modifier_replace_with_fluid` + `is_allocated`).
   - Revival: a `None` modifier with `system_properties["mx_type"] == "EDIT_POLY"` (file saved by
     stock) is converted back the same way.
   - Cost: float arrays go through IDProperty instead of shared raw blocks, so no implicit
     sharing on save; acceptable. For memfile undo (`writer->is_undo()`) the native struct
     layout can be written instead, since undo never leaves Moritz.
2. **"Save stock-compatible copy"** (optional, later): an add-on export that replaces each Edit
   Poly with the prototype's Geometry Nodes setup (code exists in `edit_poly.py`) or applies it,
   for files that must look right in stock Blender. Not on every save: it adds helper objects.

Without step 1, do not ship the modifier: one round trip through stock Blender destroys the
top of the stack.

## 7. Staged plan

| Stage | Content | Size (rough) | Main risk |
|---|---|---|---|
| 0 | DNA type + struct, RNA, `MOD_edit_poly.cc` passthrough, panel, add-menu entry | ~300 lines C++, 1 rebuild | none (mechanical) |
| 1 | Storage (offsets, base positions, result Mesh), `modify_mesh` for both modes, fingerprint, warning, copy/free, implicit sharing, depsgraph relation | ~500 lines | edge cases with empty/non-mesh input, `CD_ORIGINDEX` propagation |
| 2 | File compatibility stub + Moritz read/revive; test round trip through a stock 5.3 build | ~250 lines | getting `BLO_read_struct_list_with_type_size` sizes right; test with a real stock build |
| 3 | Edit session: enter/exit branches, `editbmesh_calc_modifiers` / cage index start, `EDBM_mesh_load_ex` routing, undo restore helper, mode restrictions | ~600-900 lines | highest: code assuming `ob->data` == BMesh; undo/session edge cases; crashes on flush paths |
| 4 | Add-on: convert prototype GN setups to native, hook 1-5 keys and Collapse To/All to the native modifier | ~150 lines Python | migration of existing files |
| 5 | Extras: Re-base with nearest remap, Show end result toggle, propagate selected attributes from input in TOPOLOGY mode, stock-compatible export | ~300 lines | scope creep |

Batching: stages 0-2 fit one rebuild cycle and are useful alone (the prototype's operators can
already drive a native modifier by writing its RNA data from a stand-in object). Stage 3 is a
separate cycle and should be done when stage 1-2 files exist to test against.

## Implemented (stages 0-2)

Changed from the plan above: no `EditPolyModifierData` struct. The modifier is a plain
`ModifierData` (type 200) and keeps its data as ID properties in `system_properties`
(`mx_type`, `mode`, `base_counts`, `base_hash`, `offsets` or `base_positions` + `result`). Stock
Blender knows that struct, so section 6's compatibility stub is simply the storage format: no
separate write path, no data loss, and `system_properties` ID pointers are already counted as
users. Moritz revives a stub saved by stock in `BKE_modifier_blend_read_data`.

- `source/blender/modifiers/intern/MOD_edit_poly.cc`, `MOD_edit_poly.hh`
- RNA `EditPolyModifier`: `edit_mode`, `result`, `store(input, edited)` (the add-on prototype or
  the future edit session writes the edit through it)
- Test: `moritz/tests/test_edit_poly_native.py` (deform and topology edits follow the stack
  below, save/reload, round trip through stock Blender)

Still to do: stage 3 (the edit session in Edit Mode, replacing the add-on's stand-in object) and
stage 4 (the add-on drives the native modifier).
