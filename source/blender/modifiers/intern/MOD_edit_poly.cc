/* SPDX-FileCopyrightText: 2026 Moritz Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup modifiers
 *
 * Moritz: Edit Poly, an edit that lives in the modifier stack and follows the modifiers below.
 *
 * The edit is stored as ID properties in #ModifierData.system_properties of a plain
 * #ModifierData, not in a struct of its own. Stock Blender knows that struct, so it keeps the
 * modifier (as a disabled "None" modifier), keeps the modifiers above it and writes the data back
 * on save; Moritz revives it on load (see #BKE_modifier_blend_read_data).
 *
 * Properties:
 * - `mx_type`: "EDIT_POLY".
 * - `mode`: #EditPolyMode.
 * - `base_counts`: vertex, edge, face and corner count of the input at the last store.
 * - `base_hash`: hash of the input's edge and corner topology at the last store.
 * - `offsets` (Deform): one float3 offset per input vertex.
 * - `base_positions` (Topology): the input positions at the last store.
 * - `result` (Topology): the edited mesh, with the int point attribute `mx_orig`.
 */

#include "BLI_math_vector_types.hh"
#include "BLI_span.hh"

#include "BLT_translation.hh"

#include "DNA_mesh_types.h"
#include "DNA_modifier_types.h"
#include "DNA_screen_types.h"

#include "BKE_attribute.hh"
#include "BKE_idprop.hh"
#include "BKE_lib_id.hh"
#include "BKE_mesh.h"
#include "BKE_mesh.hh"
#include "BKE_modifier.hh"
#include "BKE_report.hh"

#include "DEG_depsgraph_build.hh"

#include "UI_interface_layout.hh"
#include "UI_resources.hh"

#include "RNA_access.hh"
#include "RNA_prototypes.hh"

#include "MOD_edit_poly.hh"
#include "MOD_modifiertypes.hh"
#include "MOD_ui_common.hh"

namespace blender {

static const char *ORIG_ATTR = "mx_orig";

static IDProperty *prop_get(const ModifierData &md, const StringRef name)
{
  return md.system_properties ? IDP_GetPropertyFromGroup_null(md.system_properties, name) :
                                nullptr;
}

static void prop_set(ModifierData &md, std::unique_ptr<IDProperty, bke::idprop::IDPropertyDeleter> prop)
{
  if (md.system_properties == nullptr) {
    md.system_properties = bke::idprop::create_group("").release();
  }
  IDP_ReplaceInGroup(md.system_properties, prop.release());
}

static void prop_remove(ModifierData &md, const StringRef name)
{
  if (IDProperty *prop = prop_get(md, name)) {
    IDP_FreeFromGroup(md.system_properties, prop);
  }
}

EditPolyMode MOD_edit_poly_mode(const ModifierData &md)
{
  const IDProperty *prop = prop_get(md, "mode");
  return (prop && prop->type == IDP_INT) ? EditPolyMode(IDP_int_get(prop)) : EditPolyMode::None;
}

Mesh *MOD_edit_poly_result(const ModifierData &md)
{
  const IDProperty *prop = prop_get(md, "result");
  if (prop == nullptr || prop->type != IDP_ID) {
    return nullptr;
  }
  ID *id = IDP_ID_get(prop);
  return (id && GS(id->name) == ID_ME) ? reinterpret_cast<Mesh *>(id) : nullptr;
}

/** FNV-1a over the edge and corner topology. */
static int topology_hash(const Mesh &mesh)
{
  uint32_t hash = 2166136261u;
  auto add = [&](const Span<int> values) {
    for (const int v : values) {
      hash = (hash ^ uint32_t(v)) * 16777619u;
    }
  };
  add(mesh.edges().cast<int>());
  add(mesh.corner_verts());
  add(mesh.face_offsets());
  return int(hash);
}

static bool input_matches(const ModifierData &md, const Mesh &mesh)
{
  const IDProperty *counts = prop_get(md, "base_counts");
  const IDProperty *hash = prop_get(md, "base_hash");
  if (counts == nullptr || counts->type != IDP_ARRAY || counts->len != 4 || hash == nullptr) {
    return false;
  }
  const int *c = IDP_array_int_get(counts);
  if (c[0] != mesh.verts_num || c[1] != mesh.edges_num || c[2] != mesh.faces_num ||
      c[3] != mesh.corners_num)
  {
    return false;
  }
  return IDP_int_get(hash) == topology_hash(mesh);
}

static Span<float3> float3_prop(const ModifierData &md, const StringRef name)
{
  const IDProperty *prop = prop_get(md, name);
  if (prop == nullptr || prop->type != IDP_ARRAY || prop->subtype != IDP_FLOAT) {
    return {};
  }
  return Span<float3>(reinterpret_cast<const float3 *>(IDP_array_float_get(prop)), prop->len / 3);
}

bool MOD_edit_poly_store(
    Main &bmain, ModifierData &md, const Mesh &input, const Mesh &edited, ReportList *reports)
{
  const Span<float3> input_positions = input.vert_positions();
  const Span<float3> edited_positions = edited.vert_positions();

  const bke::AttributeAccessor attributes = edited.attributes();
  const VArraySpan<int> orig = *attributes.lookup_or_default<int>(
      ORIG_ATTR, bke::AttrDomain::Point, -2);
  bool identity = true;
  for (const int i : orig.index_range()) {
    if (orig[i] != -2 && orig[i] != i) {
      identity = false;
      break;
    }
  }

  const bool same_topology = identity && edited.verts_num == input.verts_num &&
                             edited.edges_num == input.edges_num &&
                             edited.faces_num == input.faces_num &&
                             edited.corners_num == input.corners_num &&
                             topology_hash(edited) == topology_hash(input);

  prop_set(md, bke::idprop::create("mx_type", StringRefNull("EDIT_POLY")));
  prop_set(md,
           bke::idprop::create("base_counts",
                               Span<int>({input.verts_num,
                                          input.edges_num,
                                          input.faces_num,
                                          input.corners_num})));
  prop_set(md, bke::idprop::create("base_hash", topology_hash(input)));

  if (same_topology) {
    Array<float3> offsets(input.verts_num);
    for (const int i : offsets.index_range()) {
      offsets[i] = edited_positions[i] - input_positions[i];
    }
    prop_set(md, bke::idprop::create("offsets", offsets.as_span().cast<float>()));
    prop_set(md, bke::idprop::create("mode", int(EditPolyMode::Deform)));
    prop_remove(md, "base_positions");
    prop_remove(md, "result");
    return true;
  }

  /* Topology mode: keep the edited mesh as a Mesh data-block. */
  Mesh *result = MOD_edit_poly_result(md);
  if (result == nullptr) {
    result = BKE_mesh_add(&bmain, "Edit Poly");
    prop_set(md, bke::idprop::create("result", &result->id));
    /* The property holds the only user. */
    id_us_min(&result->id);
  }
  Mesh *edited_copy = BKE_mesh_copy_for_eval(edited);
  if (orig.is_empty() || !attributes.contains(ORIG_ATTR)) {
    /* No mapping: vertices map by index where the input has them. */
    bke::MutableAttributeAccessor dst = edited_copy->attributes_for_write();
    bke::SpanAttributeWriter<int> map = dst.lookup_or_add_for_write_only_span<int>(
        ORIG_ATTR, bke::AttrDomain::Point);
    for (const int i : map.span.index_range()) {
      map.span[i] = i < input.verts_num ? i : -1;
    }
    map.finish();
    BKE_report(reports, RPT_INFO, "Edit Poly: no vertex mapping, matched by index");
  }
  BKE_mesh_nomain_to_mesh(edited_copy, result, nullptr, false);
  prop_set(md, bke::idprop::create("base_positions", input_positions.cast<float>()));
  prop_set(md, bke::idprop::create("mode", int(EditPolyMode::Topology)));
  prop_remove(md, "offsets");
  return true;
}

static Mesh *modify_mesh(ModifierData *md, const ModifierEvalContext *ctx, Mesh *mesh)
{
  const EditPolyMode mode = MOD_edit_poly_mode(*md);
  if (mode == EditPolyMode::None) {
    return mesh;
  }
  const bool matches = input_matches(*md, *mesh);

  if (mode == EditPolyMode::Deform) {
    const Span<float3> offsets = float3_prop(*md, "offsets");
    if (offsets.size() != mesh->verts_num) {
      BKE_modifier_set_warning(ctx->object, md, "Topology below changed: the edit is off");
      return mesh;
    }
    if (!matches) {
      /* Max is index based too: same vertex count, keep applying by index. */
      BKE_modifier_set_warning(
          ctx->object, md, "Topology below changed: edits applied by vertex index");
    }
    Mesh *result = BKE_mesh_copy_for_eval(*mesh);
    MutableSpan<float3> positions = result->vert_positions_for_write();
    for (const int i : positions.index_range()) {
      positions[i] += offsets[i];
    }
    result->tag_positions_changed();
    return result;
  }

  const Mesh *stored = MOD_edit_poly_result(*md);
  if (stored == nullptr) {
    BKE_modifier_set_error(ctx->object, md, "Stored mesh is missing");
    return mesh;
  }
  Mesh *result = BKE_mesh_copy_for_eval(*stored);
  if (!matches) {
    BKE_modifier_set_warning(
        ctx->object, md, "Topology below changed: edits kept as they were");
    return result;
  }
  /* Edited vertices ride on the changes from below: add (input - base) of their source. */
  const Span<float3> base = float3_prop(*md, "base_positions");
  const Span<float3> input = mesh->vert_positions();
  const VArraySpan<int> orig = *result->attributes().lookup_or_default<int>(
      ORIG_ATTR, bke::AttrDomain::Point, -1);
  MutableSpan<float3> positions = result->vert_positions_for_write();
  for (const int i : positions.index_range()) {
    const int src = orig[i];
    if (src >= 0 && src < input.size() && src < base.size()) {
      positions[i] += input[src] - base[src];
    }
  }
  result->tag_positions_changed();
  return result;
}

static void update_depsgraph(ModifierData *md, const ModifierUpdateDepsgraphContext *ctx)
{
  if (Mesh *stored = MOD_edit_poly_result(*md)) {
    DEG_add_generic_id_relation(ctx->node, &stored->id, "Edit Poly Modifier");
  }
}

static void panel_draw(const bContext * /*C*/, Panel *panel)
{
  ui::Layout &layout = *panel->layout;
  PointerRNA ob_ptr;
  PointerRNA *ptr = modifier_panel_get_property_pointers(panel, &ob_ptr);
  const ModifierData &md = *ptr->data_as<ModifierData>();

  switch (MOD_edit_poly_mode(md)) {
    case EditPolyMode::None:
      layout.label(IFACE_("No edits yet"), ICON_INFO);
      break;
    case EditPolyMode::Deform:
      layout.label(IFACE_("Moved vertices, follows the stack below"), ICON_NONE);
      break;
    case EditPolyMode::Topology:
      layout.label(IFACE_("Edited topology, follows the stack below"), ICON_NONE);
      break;
  }
  modifier_error_message_draw(layout, ptr);
}

static void panel_register(ARegionType *region_type)
{
  modifier_panel_register(region_type, eModifierType_EditPoly, panel_draw);
}

ModifierTypeInfo modifierType_EditPoly = {
    /*idname*/ "EditPoly",
    /*name*/ N_("Edit Poly"),
    /*struct_name*/ "ModifierData",
    /*struct_size*/ sizeof(ModifierData),
    /*srna*/ &RNA_EditPolyModifier,
    /*type*/ ModifierTypeType::Constructive,
    /*flags*/
    (eModifierTypeFlag_AcceptsMesh | eModifierTypeFlag_SupportsEditmode |
     eModifierTypeFlag_EnableInEditmode),
    /*icon*/ ICON_EDITMODE_HLT,

    /*copy_data*/ BKE_modifier_copydata_generic,

    /*deform_verts*/ nullptr,
    /*deform_matrices*/ nullptr,
    /*deform_verts_EM*/ nullptr,
    /*deform_matrices_EM*/ nullptr,
    /*modify_mesh*/ modify_mesh,
    /*modify_geometry_set*/ nullptr,

    /*init_data*/ nullptr,
    /*required_data_mask*/ nullptr,
    /*free_data*/ nullptr,
    /*is_disabled*/ nullptr,
    /*update_depsgraph*/ update_depsgraph,
    /*depends_on_time*/ nullptr,
    /*depends_on_normals*/ nullptr,
    /*foreach_ID_link*/ nullptr,
    /*foreach_tex_link*/ nullptr,
    /*free_runtime_data*/ nullptr,
    /*panel_register*/ panel_register,
    /*blend_write*/ nullptr,
    /*blend_read*/ nullptr,
    /*foreach_cache*/ nullptr,
    /*foreach_working_space_color*/ nullptr,
};

}  // namespace blender
