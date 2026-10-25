/* SPDX-FileCopyrightText: 2026 Moritz Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup modifiers
 *
 * Moritz: Edit Spline, a spline edit that lives in the modifier stack and follows the modifiers
 * below (a shape's parameters, another Edit Spline), and Max's Interpolation rollout for its
 * output (Steps, Optimize, Adaptive).
 *
 * Stored like Edit Poly: ID properties in #ModifierData.system_properties of a plain
 * #ModifierData. Stock Blender keeps it as a disabled "None" modifier and writes the data back;
 * Moritz revives it on load (see #BKE_modifier_blend_read_data).
 *
 * Properties:
 * - `mx_type`: "EDIT_SPLINE".
 * - `mode`: #EditSplineMode.
 * - `base_counts`: point and curve count of the input at the last store.
 * - `base_hash`: hash of the input's curve offsets, cyclic flags and types at the last store.
 * - `offsets` (Deform): per input knot, the offsets of position, left and right handle.
 * - `base_knots` (Topology): positions, left and right handles of the input at the last store.
 * - `result` (Topology): the edited curves (a Curves data-block), with the int point attribute
 *   `mx_orig`. While the input no longer matches, the output carries the bool point attribute
 *   `mx_topology_changed`.
 * - `steps`, `optimize`, `adaptive`: the Interpolation rollout (steps -1: keep the input's).
 * - `session`: 1 while the modifier is edited in Edit Mode on the object itself (see
 *   #MOD_edit_spline_session_begin).
 */

#include <array>
#include <cmath>

#include "BLI_array.hh"
#include "BLI_listbase_iterator.hh"
#include "BLI_math_rotation.hh"
#include "BLI_math_vector.hh"
#include "BLI_math_vector_types.hh"
#include "BLI_span.hh"

#include "BLT_translation.hh"

#include "DNA_curves_types.h"
#include "DNA_modifier_types.h"
#include "DNA_object_types.h"
#include "DNA_screen_types.h"

#include "BKE_attribute.hh"
#include "BKE_curves.h"
#include "BKE_curves.hh"
#include "BKE_geometry_set.hh"
#include "BKE_idprop.hh"
#include "BKE_lib_id.hh"
#include "BKE_modifier.hh"
#include "BKE_report.hh"

#include "DEG_depsgraph_query.hh"

#include "UI_interface_layout.hh"
#include "UI_resources.hh"

#include "RNA_access.hh"
#include "RNA_prototypes.hh"

#include "MOD_edit_spline.hh"
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

static int int_prop(const ModifierData &md, const StringRef name, const int fallback)
{
  const IDProperty *prop = prop_get(md, name);
  return (prop && prop->type == IDP_INT) ? IDP_int_get(prop) : fallback;
}

EditSplineMode MOD_edit_spline_mode(const ModifierData &md)
{
  return EditSplineMode(int_prop(md, "mode", int(EditSplineMode::None)));
}

Curves *MOD_edit_spline_result(const ModifierData &md)
{
  const IDProperty *prop = prop_get(md, "result");
  if (prop == nullptr || prop->type != IDP_ID) {
    return nullptr;
  }
  ID *id = IDP_ID_get(prop);
  return (id && GS(id->name) == ID_CV) ? reinterpret_cast<Curves *>(id) : nullptr;
}

/** FNV-1a over the curve offsets, cyclic flags and curve types. */
static int topology_hash(const bke::CurvesGeometry &curves)
{
  uint32_t hash = 2166136261u;
  auto add = [&](const int v) { hash = (hash ^ uint32_t(v)) * 16777619u; };
  for (const int v : curves.offsets()) {
    add(v);
  }
  const VArray<bool> cyclic = curves.cyclic();
  const VArray<int8_t> types = curves.curve_types();
  for (const int i : curves.curves_range()) {
    add(int(cyclic[i]) | (int(types[i]) << 1));
  }
  return int(hash);
}

/** Positions, then left handles, then right handles (the position where a curve has none). */
static Array<float3> knots(const bke::CurvesGeometry &curves)
{
  const int n = curves.points_num();
  Array<float3> out(n * 3);
  const Span<float3> positions = curves.positions();
  const std::optional<Span<float3>> left = curves.handle_positions_left();
  const std::optional<Span<float3>> right = curves.handle_positions_right();
  for (const int i : IndexRange(n)) {
    out[i] = positions[i];
    out[n + i] = left ? (*left)[i] : positions[i];
    out[2 * n + i] = right ? (*right)[i] : positions[i];
  }
  return out;
}

static Span<float3> float3_prop(const ModifierData &md, const StringRef name)
{
  const IDProperty *prop = prop_get(md, name);
  if (prop == nullptr || prop->type != IDP_ARRAY || prop->subtype != IDP_FLOAT) {
    return {};
  }
  return Span<float3>(reinterpret_cast<const float3 *>(IDP_array_float_get(prop)), prop->len / 3);
}

static bool input_matches(const ModifierData &md, const bke::CurvesGeometry &curves)
{
  const IDProperty *counts = prop_get(md, "base_counts");
  const IDProperty *hash = prop_get(md, "base_hash");
  if (counts == nullptr || counts->type != IDP_ARRAY || counts->len != 2 || hash == nullptr) {
    return false;
  }
  const int *c = IDP_array_int_get(counts);
  if (c[0] != curves.points_num() || c[1] != curves.curves_num()) {
    return false;
  }
  return IDP_int_get(hash) == topology_hash(curves);
}

/** Store `edited` as the edit of an input described by its knots, counts and topology hash. */
static bool store_from_base(Main &bmain,
                            ModifierData &md,
                            const Span<float3> base_knots,
                            const std::array<int, 2> &counts_in,
                            const int hash,
                            const bke::CurvesGeometry &edited,
                            ReportList *reports)
{
  const int counts[2] = {counts_in[0], counts_in[1]};

  const VArraySpan<int> orig = *edited.attributes().lookup_or_default<int>(
      ORIG_ATTR, bke::AttrDomain::Point, -2);
  bool identity = true;
  for (const int i : orig.index_range()) {
    if (orig[i] != -2 && orig[i] != i) {
      identity = false;
      break;
    }
  }
  /* Splines are small: keep the edited splines even for a pure move, so a knot count change
   * below keeps the edit visible as it was (as Max does) instead of switching it off. Deform mode
   * (offsets only) is used when the input has no knots to keep. */
  const bool same_topology = identity && edited.points_num() == counts[0] &&
                             edited.curves_num() == counts[1] && topology_hash(edited) == hash &&
                             counts[0] == 0;
  /* Copy first: `base_knots` may point into a property replaced below. */
  const Array<float3> base(base_knots);

  prop_set(md, bke::idprop::create("mx_type", StringRefNull("EDIT_SPLINE")));
  prop_set(md, bke::idprop::create("base_counts", Span<int>(counts, 2)));
  prop_set(md, bke::idprop::create("base_hash", hash));

  if (same_topology) {
    const Array<float3> moved = knots(edited);
    Array<float3> offsets(base.size());
    for (const int i : offsets.index_range()) {
      offsets[i] = moved[i] - base[i];
    }
    prop_set(md, bke::idprop::create("offsets", offsets.as_span().cast<float>()));
    prop_set(md, bke::idprop::create("mode", int(EditSplineMode::Deform)));
    prop_remove(md, "base_knots");
    prop_remove(md, "result");
    return true;
  }

  Curves *result = MOD_edit_spline_result(md);
  if (result == nullptr) {
    result = BKE_curves_add(&bmain, "Edit Spline");
    prop_set(md, bke::idprop::create("result", &result->id));
    /* The property holds the only user. */
    id_us_min(&result->id);
  }
  bke::CurvesGeometry copy(edited);
  /* The types may have been written as an attribute (from Python): recount them. */
  copy.update_curve_types();
  if (!copy.attributes().contains(ORIG_ATTR)) {
    /* No mapping: knots map by index where the input has them. */
    bke::SpanAttributeWriter<int> map =
        copy.attributes_for_write().lookup_or_add_for_write_only_span<int>(ORIG_ATTR,
                                                                         bke::AttrDomain::Point);
    for (const int i : map.span.index_range()) {
      map.span[i] = i < counts[0] ? i : -1;
    }
    map.finish();
    BKE_report(reports, RPT_INFO, "Edit Spline: no knot mapping, matched by index");
  }
  result->geometry.wrap() = std::move(copy);
  prop_set(md, bke::idprop::create("base_knots", base.as_span().cast<float>()));
  prop_set(md, bke::idprop::create("mode", int(EditSplineMode::Topology)));
  prop_remove(md, "offsets");
  return true;
}

bool MOD_edit_spline_store(
    Main &bmain, ModifierData &md, const Curves &input_id, const Curves &edited_id, ReportList *reports)
{
  const bke::CurvesGeometry &input = input_id.geometry.wrap();
  return store_from_base(bmain,
                         md,
                         knots(input),
                         {input.points_num(), input.curves_num()},
                         topology_hash(input),
                         edited_id.geometry.wrap(),
                         reports);
}

/* -------------------------------------------------------------------- */
/** 
ame Edit Mode session
 *
 * While `session` is set, Edit Mode on the object edits the modifier's result instead of the
 * object's splines: entering builds the edit-nurbs from `result`, evaluation in Edit Mode skips
 * this modifier and everything below it, and loading the edit-nurbs writes into `result`.
 * Leaving Edit Mode ends the session.
 * \{ */

bool MOD_edit_spline_session_begin(
    Main &bmain, ModifierData &md, const Curves &input, const Curves &edited, ReportList *reports)
{
  if (!MOD_edit_spline_store(bmain, md, input, edited, reports)) {
    return false;
  }
  if (MOD_edit_spline_mode(md) != EditSplineMode::Topology) {
    BKE_report(reports, RPT_ERROR, "Edit Spline: nothing to edit");
    return false;
  }
  prop_set(md, bke::idprop::create("session", 1));
  return true;
}

static bool session_active(const ModifierData &md)
{
  return md.type == eModifierType_EditSpline && int_prop(md, "session", 0) != 0;
}

ModifierData *MOD_edit_spline_session_find(const Object &ob)
{
  for (ModifierData &md : const_cast<Object &>(ob).modifiers) {
    if (session_active(md)) {
      return &md;
    }
  }
  return nullptr;
}

void MOD_edit_spline_session_load(Main &bmain, ModifierData &md, const Curves &edited)
{
  const IDProperty *counts = prop_get(md, "base_counts");
  const IDProperty *hash = prop_get(md, "base_hash");
  const Span<float3> base = float3_prop(md, "base_knots");
  if (counts == nullptr || counts->type != IDP_ARRAY || counts->len != 2 || hash == nullptr) {
    return;
  }
  const int *c = IDP_array_int_get(counts);
  store_from_base(bmain, md, base, {c[0], c[1]}, IDP_int_get(hash), edited.geometry.wrap(), nullptr);
}

void MOD_edit_spline_session_end(Main & /*bmain*/, ModifierData &md)
{
  prop_remove(md, "session");
}

/** \} */

/** Add per-knot offsets (position, left, right handle) to `curves`; `src` maps knots to `offsets`
 * slots (index into the input), or is empty for the identity. */
static void add_offsets(bke::CurvesGeometry &curves,
                        const Span<float3> offsets,
                        const int input_num,
                        const Span<int> src)
{
  MutableSpan<float3> positions = curves.positions_for_write();
  const bool has_handles = curves.handle_positions_left().has_value();
  MutableSpan<float3> left = has_handles ? curves.handle_positions_left_for_write() :
                                           MutableSpan<float3>();
  MutableSpan<float3> right = has_handles ? curves.handle_positions_right_for_write() :
                                            MutableSpan<float3>();
  for (const int i : positions.index_range()) {
    const int s = src.is_empty() ? i : src[i];
    if (s < 0 || s >= input_num) {
      continue;
    }
    positions[i] += offsets[s];
    if (has_handles) {
      left[i] += offsets[input_num + s];
      right[i] += offsets[2 * input_num + s];
    }
  }
  curves.tag_positions_changed();
}

/** The angle the cubic Bezier `p0..p3` turns through, from its control polygon. */
static float bezier_turn(const float3 &p0, const float3 &p1, const float3 &p2, const float3 &p3)
{
  float total = 0.0f;
  const float3 legs[3] = {p1 - p0, p2 - p1, p3 - p2};
  float3 prev{0.0f};
  for (const float3 &leg : legs) {
    if (math::length_squared(leg) < 1e-12f) {
      continue;
    }
    if (math::length_squared(prev) > 0.0f) {
      total += math::angle_between(math::normalize(prev), math::normalize(leg)).radian();
    }
    prev = leg;
  }
  return total;
}

/** Max's Interpolation: Steps, Optimize (straight segments get no steps) and Adaptive (as many
 * steps as each spline's curviest segment needs, straight segments none). */
static void apply_interpolation(const ModifierData &md, bke::CurvesGeometry &curves)
{
  const int steps = int_prop(md, "steps", -1);
  const bool optimize = int_prop(md, "optimize", 0) != 0;
  const bool adaptive = int_prop(md, "adaptive", 0) != 0;
  if (steps < 0 && !optimize && !adaptive) {
    return;
  }
  const bool has_handles = curves.handle_positions_left().has_value();
  const OffsetIndices points_by_curve = curves.points_by_curve();
  const VArray<int8_t> types = curves.curve_types();
  const VArray<bool> cyclic = curves.cyclic();
  MutableSpan<int> resolution = curves.resolution_for_write();
  if (steps >= 0 && !adaptive) {
    resolution.fill(steps + 1);
  }
  if (!has_handles || !(optimize || adaptive)) {
    curves.tag_topology_changed();
    return;
  }
  const Span<float3> positions = curves.positions();
  const Span<float3> left = *curves.handle_positions_left();
  const Span<float3> right = *curves.handle_positions_right();
  MutableSpan<int8_t> types_left = curves.handle_types_left_for_write();
  MutableSpan<int8_t> types_right = curves.handle_types_right_for_write();
  for (const int c : curves.curves_range()) {
    if (types[c] != CURVE_TYPE_BEZIER) {
      continue;
    }
    const IndexRange points = points_by_curve[c];
    const int segments = cyclic[c] ? points.size() : points.size() - 1;
    int needed = 1;
    for (const int s : IndexRange(segments)) {
      const int a = points[s];
      const int b = points[(s + 1) % points.size()];
      const float turn = bezier_turn(positions[a], right[a], left[b], positions[b]);
      if (turn < 1e-4f) {
        /* Straight: two points are enough. Vector handles evaluate a segment to its ends. */
        types_right[a] = BEZIER_HANDLE_VECTOR;
        types_left[b] = BEZIER_HANDLE_VECTOR;
        continue;
      }
      /* About 6 degrees per step, as Max's Adaptive. */
      needed = std::max(needed, int(std::ceil(turn / 0.1f)));
    }
    if (adaptive) {
      resolution[c] = std::min(needed, 100);
    }
  }
  curves.tag_topology_changed();
}

static void modify_geometry_set(ModifierData *md,
                                const ModifierEvalContext *ctx,
                                bke::GeometrySet *geometry_set)
{
  Object *ob = ctx->object;
  if (!geometry_set->has_curves()) {
    return;
  }
  Curves *curves_id = geometry_set->get_curves_for_write();
  bke::CurvesGeometry &curves = curves_id->geometry.wrap();
  const EditSplineMode mode = MOD_edit_spline_mode(*md);

  if (mode == EditSplineMode::Deform) {
    const Span<float3> offsets = float3_prop(*md, "offsets");
    if (offsets.size() != curves.points_num() * 3) {
      BKE_modifier_set_warning(ob, md, "Knots below changed: the edit is off");
    }
    else {
      if (!input_matches(*md, curves)) {
        BKE_modifier_set_warning(ob, md, "Splines below changed: edits applied by knot index");
      }
      add_offsets(curves, offsets, curves.points_num(), {});
    }
  }
  else if (mode == EditSplineMode::Topology) {
    const Curves *stored = MOD_edit_spline_result(*md);
    if (stored != nullptr) {
      stored = DEG_get_original(stored);
    }
    if (stored == nullptr) {
      BKE_modifier_set_error(ob, md, "Stored splines are missing");
      return;
    }
    const bool matches = input_matches(*md, curves);
    bke::CurvesGeometry result(stored->geometry.wrap());
    if (!matches) {
      BKE_modifier_set_warning(ob, md, "Splines below changed: edits kept as they were");
      /* For the add-on: editing again maps the knots to the new input by position. */
      bke::SpanAttributeWriter<bool> changed =
          result.attributes_for_write().lookup_or_add_for_write_only_span<bool>(
              "mx_topology_changed", bke::AttrDomain::Point);
      changed.span.fill(true);
      changed.finish();
    }
    else {
      /* Edited knots ride on the changes from below: add (input - base) of their source. */
      const Span<float3> base = float3_prop(*md, "base_knots");
      const Array<float3> input = knots(curves);
      if (base.size() == input.size()) {
        Array<float3> delta(input.size());
        for (const int i : delta.index_range()) {
          delta[i] = input[i] - base[i];
        }
        const VArraySpan<int> orig = *result.attributes().lookup_or_default<int>(
            ORIG_ATTR, bke::AttrDomain::Point, -1);
        add_offsets(result, delta, curves.points_num(), orig);
      }
    }
    curves = std::move(result);
  }
  apply_interpolation(*md, curves);
}

static Mesh *modify_mesh(ModifierData * /*md*/, const ModifierEvalContext * /*ctx*/, Mesh *mesh)
{
  /* Only curves are edited; a mesh (a curve converted earlier in the stack) passes through. */
  return mesh;
}

static void panel_draw(const bContext * /*C*/, Panel *panel)
{
  ui::Layout &layout = *panel->layout;
  PointerRNA ob_ptr;
  PointerRNA *ptr = modifier_panel_get_property_pointers(panel, &ob_ptr);
  const ModifierData &md = *ptr->data_as<ModifierData>();

  switch (MOD_edit_spline_mode(md)) {
    case EditSplineMode::None:
      layout.label(IFACE_("No edits yet"), ICON_INFO);
      break;
    case EditSplineMode::Deform:
      layout.label(IFACE_("Moved knots, follows the stack below"), ICON_NONE);
      break;
    case EditSplineMode::Topology:
      layout.label(IFACE_("Edited splines, follows the stack below"), ICON_NONE);
      break;
  }
  ui::Layout &col = layout.column(true, IFACE_("Interpolation"));
  col.prop(ptr, "steps", UI_ITEM_NONE, std::nullopt, ICON_NONE);
  col.prop(ptr, "use_optimize", UI_ITEM_NONE, std::nullopt, ICON_NONE);
  col.prop(ptr, "use_adaptive", UI_ITEM_NONE, std::nullopt, ICON_NONE);
  if (session_active(md)) {
    layout.label(IFACE_("Editing in Edit Mode"), ICON_EDITMODE_HLT);
  }
  modifier_error_message_draw(layout, ptr);
}

static void panel_register(ARegionType *region_type)
{
  modifier_panel_register(region_type, eModifierType_EditSpline, panel_draw);
}

ModifierTypeInfo modifierType_EditSpline = {
    /*idname*/ "EditSpline",
    /*name*/ N_("Edit Spline"),
    /*struct_name*/ "ModifierData",
    /*struct_size*/ sizeof(ModifierData),
    /*srna*/ &RNA_EditSplineModifier,
    /*type*/ ModifierTypeType::Constructive,
    /*flags*/ (eModifierTypeFlag_AcceptsCVs | eModifierTypeFlag_SupportsEditmode),
    /*icon*/ ICON_CURVE_BEZCURVE,

    /*copy_data*/ BKE_modifier_copydata_generic,

    /*deform_verts*/ nullptr,
    /*deform_matrices*/ nullptr,
    /*deform_verts_EM*/ nullptr,
    /*deform_matrices_EM*/ nullptr,
    /*modify_mesh*/ modify_mesh,
    /*modify_geometry_set*/ modify_geometry_set,

    /*init_data*/ nullptr,
    /*required_data_mask*/ nullptr,
    /*free_data*/ nullptr,
    /*is_disabled*/ nullptr,
    /*update_depsgraph*/ nullptr,
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
