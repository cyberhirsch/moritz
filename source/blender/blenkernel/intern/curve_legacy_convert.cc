/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup bke
 */

#include "MEM_guardedalloc.h"

#include "BLI_listbase.hh"
#include "BLI_math_vector_c.hh"
#include "BLI_math_vector.hh"
#include "BLI_task.hh"
#include "BLI_vector.hh"

#include "DNA_curve_types.h"
#include "DNA_curves_types.h"

#include "BKE_curve.hh"
#include "BKE_curve_legacy_convert.hh"
#include "BKE_curves.hh"
#include "BKE_curves_utils.hh"
#include "BKE_geometry_set.hh"

namespace blender::bke {

static CurveType curve_type_from_legacy(const short type)
{
  switch (type) {
    case CU_POLY:
      return CURVE_TYPE_POLY;
    case CU_BEZIER:
      return CURVE_TYPE_BEZIER;
    case CU_NURBS:
      return CURVE_TYPE_NURBS;
  }
  BLI_assert_unreachable();
  return CURVE_TYPE_POLY;
}

static HandleType handle_type_from_legacy(const uint8_t handle_type_legacy)
{
  switch (handle_type_legacy) {
    case HD_FREE:
      return BEZIER_HANDLE_FREE;
    case HD_AUTO:
      return BEZIER_HANDLE_AUTO;
    case HD_VECT:
      return BEZIER_HANDLE_VECTOR;
    case HD_ALIGN:
      return BEZIER_HANDLE_ALIGN;
    case HD_AUTO_ANIM:
      return BEZIER_HANDLE_AUTO;
    case HD_ALIGN_DOUBLESIDE:
      return BEZIER_HANDLE_ALIGN;
  }
  BLI_assert_unreachable();
  return BEZIER_HANDLE_AUTO;
}

static NormalMode normal_mode_from_legacy(const short twist_mode)
{
  switch (twist_mode) {
    case CU_TWIST_Z_UP:
    case CU_TWIST_TANGENT:
      return NORMAL_MODE_Z_UP;
    case CU_TWIST_MINIMUM:
      return NORMAL_MODE_MINIMUM_TWIST;
  }
  BLI_assert_unreachable();
  return NORMAL_MODE_MINIMUM_TWIST;
}

KnotsMode knots_mode_from_legacy(const short flag)
{
  if (flag & CU_NURB_CUSTOM) {
    return NURBS_KNOT_MODE_CUSTOM;
  }
  switch (flag & (CU_NURB_ENDPOINT | CU_NURB_BEZIER)) {
    case CU_NURB_ENDPOINT:
      return NURBS_KNOT_MODE_ENDPOINT;
    case CU_NURB_BEZIER:
      return NURBS_KNOT_MODE_BEZIER;
    case CU_NURB_ENDPOINT | CU_NURB_BEZIER:
      return NURBS_KNOT_MODE_ENDPOINT_BEZIER;
    case 0:
      return NURBS_KNOT_MODE_NORMAL;
  }
  BLI_assert_unreachable();
  return NURBS_KNOT_MODE_NORMAL;
}

Curves *curve_legacy_to_curves(const Curve &curve_legacy, const ListBaseT<Nurb> &nurbs_list)
{
  Vector<const Nurb *> src_curves;
  for (const Nurb &item : nurbs_list) {
    src_curves.append(&item);
  }
  if (src_curves.is_empty()) {
    return nullptr;
  }

  Curves *curves_id = curves_new_nomain(0, src_curves.size());
  CurvesGeometry &curves = curves_id->geometry.wrap();
  MutableAttributeAccessor curves_attributes = curves.attributes_for_write();

  MutableSpan<int8_t> types = curves.curve_types_for_write();
  MutableSpan<bool> cyclic = curves.cyclic_for_write();

  int offset = 0;
  MutableSpan<int> offsets = curves.offsets_for_write();
  for (const int i : src_curves.index_range()) {
    offsets[i] = offset;

    const Nurb &src_curve = *src_curves[i];
    types[i] = curve_type_from_legacy(src_curve.type);
    cyclic[i] = src_curve.flagu & CU_NURB_CYCLIC;

    offset += src_curve.pntsu;
  }
  offsets.last() = offset;
  curves.resize(curves.offsets().last(), curves.curves_num());

  curves.update_curve_types();

  const OffsetIndices points_by_curve = curves.points_by_curve();
  MutableSpan<float3> positions = curves.positions_for_write();
  SpanAttributeWriter<float> radius_attribute =
      curves_attributes.lookup_or_add_for_write_only_span<float>("radius", AttrDomain::Point);
  MutableSpan<float> radii = radius_attribute.span;
  MutableSpan<float> tilts = curves.tilt_for_write();

  auto create_poly = [&](const IndexMask &selection) {
    selection.foreach_index(
        [&](const int curve_i) {
          const Nurb &src_curve = *src_curves[curve_i];
          const Span<BPoint> src_points(src_curve.bp, src_curve.pntsu);
          const IndexRange points = points_by_curve[curve_i];

          for (const int i : src_points.index_range()) {
            const BPoint &bp = src_points[i];
            positions[points[i]] = bp.vec;
            radii[points[i]] = bp.radius;
            tilts[points[i]] = bp.tilt;
          }
        },
        exec_mode::grain_size(256));
  };

  /* NOTE: For curve handles, legacy curves can end up in invalid situations where the handle
   * positions don't agree with the types because of evaluation, or because one-sided aligned
   * handles weren't considered. While recalculating automatic handles to fix those situations
   * is an option, currently this opts not to for the sake of flexibility. */
  auto create_bezier = [&](const IndexMask &selection) {
    MutableSpan<int> resolutions = curves.resolution_for_write();
    MutableSpan<float3> handle_positions_l = curves.handle_positions_left_for_write();
    MutableSpan<float3> handle_positions_r = curves.handle_positions_right_for_write();
    MutableSpan<int8_t> handle_types_l = curves.handle_types_left_for_write();
    MutableSpan<int8_t> handle_types_r = curves.handle_types_right_for_write();

    selection.foreach_index(
        [&](const int curve_i) {
          const Nurb &src_curve = *src_curves[curve_i];
          const Span<BezTriple> src_points(src_curve.bezt, src_curve.pntsu);
          const IndexRange points = points_by_curve[curve_i];

          resolutions[curve_i] = src_curve.resolu;

          for (const int i : src_points.index_range()) {
            const BezTriple &point = src_points[i];
            positions[points[i]] = point.vec[1];
            handle_positions_l[points[i]] = point.vec[0];
            handle_types_l[points[i]] = handle_type_from_legacy(point.h1);
            handle_positions_r[points[i]] = point.vec[2];
            handle_types_r[points[i]] = handle_type_from_legacy(point.h2);
            radii[points[i]] = point.radius;
            tilts[points[i]] = point.tilt;
          }

          if (curve_legacy.flag & CU_OPTIMIZE) {
            /* Moritz: a segment whose handles lie on its chord is a straight line; vector
             * handles make it evaluate to its two end points only, as Max's Optimize does. */
            const int segments_num = (src_curve.flagu & CU_NURB_CYCLIC) ? src_points.size() :
                                                                          src_points.size() - 1;
            for (const int i : IndexRange(segments_num)) {
              const int next = (i + 1) % src_points.size();
              const float3 start = positions[points[i]];
              const float3 chord = positions[points[next]] - start;
              const float chord_sq = math::length_squared(chord);
              if (chord_sq == 0.0f) {
                continue;
              }
              const auto on_chord = [&](const float3 &handle) {
                const float3 offset = handle - start;
                const float along = math::dot(offset, chord);
                return along >= 0.0f && along <= chord_sq &&
                       math::length_squared(math::cross(offset, chord)) <=
                           1e-10f * chord_sq * chord_sq;
              };
              if (on_chord(handle_positions_r[points[i]]) &&
                  on_chord(handle_positions_l[points[next]]))
              {
                handle_types_r[points[i]] = BEZIER_HANDLE_VECTOR;
                handle_types_l[points[next]] = BEZIER_HANDLE_VECTOR;
              }
            }
          }
        },
        exec_mode::grain_size(256));
  };

  auto create_nurbs = [&](const IndexMask &selection) {
    MutableSpan<int> resolutions = curves.resolution_for_write();
    MutableSpan<float> nurbs_weights = curves.nurbs_weights_for_write();
    MutableSpan<int8_t> nurbs_orders = curves.nurbs_orders_for_write();
    MutableSpan<int8_t> nurbs_knots_modes = curves.nurbs_knots_modes_for_write();

    selection.foreach_index(
        [&](const int curve_i) {
          const Nurb &src_curve = *src_curves[curve_i];
          const Span src_points(src_curve.bp, src_curve.pntsu);
          const IndexRange points = points_by_curve[curve_i];

          resolutions[curve_i] = src_curve.resolu;
          nurbs_orders[curve_i] = src_curve.orderu;
          nurbs_knots_modes[curve_i] = knots_mode_from_legacy(src_curve.flagu);

          for (const int i : src_points.index_range()) {
            const BPoint &bp = src_points[i];
            positions[points[i]] = bp.vec;
            radii[points[i]] = bp.radius;
            tilts[points[i]] = bp.tilt;
            nurbs_weights[points[i]] = bp.vec[3];
          }
        },
        exec_mode::grain_size(256));

    curves.nurbs_custom_knots_update_size();
    if (!curves.nurbs_has_custom_knots()) {
      return;
    }

    const OffsetIndices<int> knots_by_curve = curves.nurbs_custom_knots_by_curve();
    MutableSpan<float> custom_knots = curves.nurbs_custom_knots_for_write();
    selection.foreach_index([&](const int curve_i) {
      if (nurbs_knots_modes[curve_i] == NURBS_KNOT_MODE_CUSTOM) {
        const Nurb &src_curve = *src_curves[curve_i];
        const IndexRange knots = knots_by_curve[curve_i];
        custom_knots.slice(knots).copy_from(Span<float>(src_curve.knotsu, knots.size()));
      }
    });
  };

  bke::curves::foreach_curve_by_type(
      curves.curve_types(),
      curves.curve_type_counts(),
      curves.curves_range(),
      [&](const IndexMask & /*selection*/) { BLI_assert_unreachable(); },
      create_poly,
      create_bezier,
      create_nurbs);

  curves_attributes.add<int8_t>(
      "normal_mode",
      bke::AttrDomain::Curve,
      bke::AttributeInitValue(int8_t(normal_mode_from_legacy(curve_legacy.twist_mode))));

  radius_attribute.finish();

  curves_id->mat = MEM_dupalloc(curve_legacy.mat);
  curves_id->totcol = curve_legacy.totcol;

  return curves_id;
}

Curves *curve_legacy_to_curves(const Curve &curve_legacy)
{
  return curve_legacy_to_curves(curve_legacy, *BKE_curve_nurbs_get_for_read(&curve_legacy));
}

static eBezTriple_Handle handle_type_to_legacy(const int8_t handle_type)
{
  switch (handle_type) {
    case BEZIER_HANDLE_FREE:
      return HD_FREE;
    case BEZIER_HANDLE_AUTO:
      return HD_AUTO;
    case BEZIER_HANDLE_VECTOR:
      return HD_VECT;
    case BEZIER_HANDLE_ALIGN:
      return HD_ALIGN;
  }
  return HD_FREE;
}

static int knots_flag_to_legacy(const int8_t mode)
{
  switch (mode) {
    case NURBS_KNOT_MODE_ENDPOINT:
    case NURBS_KNOT_MODE_CUSTOM:
      return CU_NURB_ENDPOINT;
    case NURBS_KNOT_MODE_BEZIER:
      return CU_NURB_BEZIER;
    case NURBS_KNOT_MODE_ENDPOINT_BEZIER:
      return CU_NURB_ENDPOINT | CU_NURB_BEZIER;
  }
  return 0;
}

void curves_to_curve_legacy_nurbs(const CurvesGeometry &curves, ListBaseT<Nurb> &r_nurbs)
{
  const OffsetIndices points_by_curve = curves.points_by_curve();
  const VArray<int8_t> types = curves.curve_types();
  const VArray<bool> cyclic = curves.cyclic();
  const VArray<int> resolution = curves.resolution();
  const Span<float3> positions = curves.positions();
  const AttributeAccessor attributes = curves.attributes();
  const VArraySpan<float> radius = *attributes.lookup_or_default<float>(
      "radius", AttrDomain::Point, 1.0f);
  const VArraySpan<float> tilt = *attributes.lookup_or_default<float>(
      "tilt", AttrDomain::Point, 0.0f);
  const VArraySpan<int> material = *attributes.lookup_or_default<int>(
      "material_index", AttrDomain::Curve, 0);
  const std::optional<Span<float3>> left = curves.handle_positions_left();
  const std::optional<Span<float3>> right = curves.handle_positions_right();
  const VArray<int8_t> types_left = curves.handle_types_left();
  const VArray<int8_t> types_right = curves.handle_types_right();
  const VArray<int8_t> orders = curves.nurbs_orders();
  const VArray<int8_t> knots_modes = curves.nurbs_knots_modes();
  const std::optional<Span<float>> weights = curves.nurbs_weights();

  for (const int c : curves.curves_range()) {
    const IndexRange points = points_by_curve[c];
    if (points.is_empty()) {
      continue;
    }
    Nurb *nu = MEM_new<Nurb>(__func__);
    nu->pntsv = 1;
    nu->resolu = nu->resolv = short(std::max(resolution[c], 1));
    nu->orderu = nu->orderv = 4;
    nu->flag = CU_SMOOTH;
    nu->flagu = eNurbKnotFlag(cyclic[c] ? CU_NURB_CYCLIC : 0);
    nu->mat_nr = short(material[c]);
    const bool bezier = types[c] == CURVE_TYPE_BEZIER && left.has_value();
    if (bezier) {
      nu->type = CU_BEZIER;
      BKE_nurb_bezierPoints_add(nu, points.size());
      for (const int i : points.index_range()) {
        const int p = points[i];
        BezTriple &bezt = nu->bezt[i];
        copy_v3_v3(bezt.vec[0], (*left)[p]);
        copy_v3_v3(bezt.vec[1], positions[p]);
        copy_v3_v3(bezt.vec[2], (*right)[p]);
        bezt.h1 = handle_type_to_legacy(types_left[p]);
        bezt.h2 = handle_type_to_legacy(types_right[p]);
        bezt.radius = radius[p];
        bezt.tilt = tilt[p];
        bezt.weight = 1.0f;
      }
    }
    else {
      const bool nurbs = types[c] == CURVE_TYPE_NURBS;
      nu->type = nurbs ? CU_NURBS : CU_POLY;
      if (nurbs) {
        nu->orderu = nu->orderv = short(orders[c]);
        nu->flagu = eNurbKnotFlag(nu->flagu | knots_flag_to_legacy(knots_modes[c]));
      }
      BKE_nurb_points_add(nu, points.size());
      for (const int i : points.index_range()) {
        const int p = points[i];
        BPoint &bp = nu->bp[i];
        copy_v3_v3(bp.vec, positions[p]);
        bp.vec[3] = (nurbs && weights) ? (*weights)[p] : 1.0f;
        bp.radius = radius[p];
        bp.tilt = tilt[p];
        bp.weight = 1.0f;
      }
      if (nurbs) {
        BKE_nurb_knot_calc_u(nu);
      }
    }
    BLI_addtail(&r_nurbs, nu);
  }
}

}  // namespace blender::bke
