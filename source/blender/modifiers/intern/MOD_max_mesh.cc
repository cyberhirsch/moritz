/* SPDX-FileCopyrightText: 2026 Moritz Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup modifiers
 *
 * Moritz: 3ds Max's mesh modifiers that Blender lacks.
 *
 * - Cap Holes: fills every open border, with a quad grid (Quad Cap) or one polygon.
 * - Normal: Unify (consistent face winding) and Flip.
 * - Mesh Clean: Weld, Remove Straight-Edge Vertices (a vertex with two edges in a straight
 *   line), Remove Loose, Remove Degenerate.
 * - Quadify Mesh: rebuilds the surface with quads of a size relative to the object.
 * - ProOptimizer: reduces the vertex count like Decimate, keeping borders, material and UV
 *   boundaries and hard edges where asked.
 * - VertexPaint: a vertex color layer that lives in the stack (colors stored by the Maximize
 *   add-on's painting session, see `rna_VertexPaintModifier_store`).
 *
 * Stored like Edit Poly: settings are ID properties in #ModifierData.system_properties of a plain
 * #ModifierData, with `mx_type` naming the kind. Stock Blender keeps them as disabled "None"
 * modifiers and writes the data back; Moritz revives them on load (see
 * #BKE_modifier_blend_read_data).
 */

#include <algorithm>
#include <cmath>

#include "MEM_guardedalloc.h"

#include "BLI_array.hh"
#include "BLI_kdopbvh.hh"
#include "BLI_bounds_types.hh"
#include "BLI_color.hh"
#include "BLI_listbase_iterator.hh"
#include "BLI_math_base_c.hh"
#include "BLI_math_vector_c.hh"
#include "BLI_math_vector.hh"
#include "BLI_math_vector_types.hh"
#include "BLI_string.hh"
#include "BLI_vector.hh"

#include "BLT_translation.hh"

#include "DNA_mesh_types.h"
#include "DNA_modifier_types.h"
#include "DNA_screen_types.h"

#include "BKE_attribute.hh"
#include "BKE_bvhutils.hh"
#include "BKE_customdata.hh"
#include "BKE_idprop.hh"
#include "BKE_lib_id.hh"
#include "BKE_mesh.hh"
#include "BKE_mesh_remesh_voxel.hh"
#include "BKE_modifier.hh"
#include "BKE_report.hh"

#include "UI_interface_layout.hh"
#include "UI_resources.hh"

#include "RNA_access.hh"
#include "RNA_prototypes.hh"

#include "bmesh.hh"
#include "bmesh_tools.hh"

#include "MOD_max_mesh.hh"
#include "MOD_modifiertypes.hh"
#include "MOD_ui_common.hh"

namespace blender {

/* -------------------------------------------------------------------- */
/** \name Settings in ID properties
 * \{ */

static const IDProperty *setting(const ModifierData &md, const StringRef name)
{
  return md.system_properties ? IDP_GetPropertyFromGroup_null(md.system_properties, name) :
                                nullptr;
}

int MOD_max_mesh_int(const ModifierData &md, const StringRef name, const int fallback)
{
  const IDProperty *prop = setting(md, name);
  return (prop && prop->type == IDP_INT) ? IDP_int_get(prop) : fallback;
}

float MOD_max_mesh_float(const ModifierData &md, const StringRef name, const float fallback)
{
  const IDProperty *prop = setting(md, name);
  if (prop && prop->type == IDP_FLOAT) {
    return IDP_float_get(prop);
  }
  if (prop && prop->type == IDP_DOUBLE) {
    return float(IDP_double_get(prop));
  }
  return fallback;
}

static void ensure_group(ModifierData &md)
{
  if (md.system_properties == nullptr) {
    md.system_properties = bke::idprop::create_group("").release();
  }
}

void MOD_max_mesh_tag(ModifierData &md, const StringRefNull mx_type)
{
  ensure_group(md);
  IDP_ReplaceInGroup(md.system_properties, bke::idprop::create("mx_type", mx_type).release());
}

void MOD_max_mesh_int_set(ModifierData &md, const StringRef name, const int value)
{
  ensure_group(md);
  IDP_ReplaceInGroup(md.system_properties, bke::idprop::create(name, value).release());
}

void MOD_max_mesh_float_set(ModifierData &md, const StringRef name, const float value)
{
  ensure_group(md);
  IDP_ReplaceInGroup(md.system_properties, bke::idprop::create(name, value).release());
}

std::string MOD_max_mesh_string(const ModifierData &md,
                                const StringRef name,
                                const StringRef fallback)
{
  const IDProperty *prop = setting(md, name);
  return (prop && prop->type == IDP_STRING) ? std::string(IDP_string_get(prop)) :
                                              std::string(fallback);
}

void MOD_max_mesh_string_set(ModifierData &md, const StringRef name, const StringRefNull value)
{
  ensure_group(md);
  IDP_ReplaceInGroup(md.system_properties, bke::idprop::create(name, value).release());
}

static bool flag(const ModifierData &md, const StringRef name, const bool fallback)
{
  return MOD_max_mesh_int(md, name, fallback) != 0;
}

static BMesh *to_bmesh(const Mesh *mesh)
{
  BMeshCreateParams create_params{};
  create_params.use_toolflags = true;
  BMeshFromMeshParams convert_params{};
  convert_params.calc_face_normal = true;
  convert_params.calc_vert_normal = true;
  return BKE_mesh_to_bmesh_ex(mesh, &create_params, &convert_params);
}

static Mesh *from_bmesh(BMesh *bm, const Mesh *mesh)
{
  Mesh *result = BKE_mesh_from_bmesh_for_eval_nomain(bm, nullptr, mesh);
  BM_mesh_free(bm);
  return result;
}

static void clear_tags(BMesh *bm)
{
  BM_mesh_elem_hflag_disable_all(bm, BM_VERT | BM_EDGE | BM_FACE, BM_ELEM_TAG, false);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Cap Holes
 * \{ */

/** The open borders, each as its ring of vertices in order. */
static Vector<Vector<BMVert *>> border_loops(BMesh *bm)
{
  ListBaseT<BMEdgeLoopStore> eloops = {nullptr};
  BM_mesh_edgeloops_find(bm, &eloops, [](BMEdge *e) { return BM_edge_is_boundary(e); });
  Vector<Vector<BMVert *>> loops;
  for (BMEdgeLoopStore &el_store : eloops) {
    if (!BM_edgeloop_is_closed(&el_store)) {
      continue;
    }
    Vector<BMVert *> verts;
    for (LinkData &link : *BM_edgeloop_verts_get(&el_store)) {
      verts.append(static_cast<BMVert *>(link.data));
    }
    if (verts.size() >= 3) {
      loops.append(std::move(verts));
    }
  }
  BM_mesh_edgeloops_free(&eloops);
  return loops;
}

static bool tag_ring_edges(const Span<BMVert *> verts, const int first, const int count)
{
  const int n = verts.size();
  for (int i = 0; i < count; i++) {
    BMEdge *e = BM_edge_exists(verts[(first + i) % n], verts[(first + i + 1) % n]);
    if (e == nullptr) {
      return false;
    }
    BM_elem_flag_enable(e, BM_ELEM_TAG);
  }
  return true;
}

static void fill_ngon(BMesh *bm, const Span<BMVert *> verts, const bool smooth)
{
  clear_tags(bm);
  if (!tag_ring_edges(verts, 0, verts.size())) {
    return;
  }
  BMOperator op;
  BMO_op_initf(bm, &op, BMO_FLAG_DEFAULTS, "holes_fill edges=%he sides=%i", BM_ELEM_TAG, 0);
  BMO_op_exec(bm, &op);
  BMOIter iter;
  BMFace *f;
  BMO_ITER (f, &iter, op.slots_out, "faces.out", BM_FACE) {
    BM_elem_flag_set(f, BM_ELEM_SMOOTH, smooth);
  }
  BMO_op_finish(bm, &op);
}

/** How far a ring vertex turns (0 on a straight border, larger at a corner). */
static float turn_angle(const Span<BMVert *> verts, const int i)
{
  const int n = verts.size();
  return fabsf(float(M_PI) -
               angle_v3v3v3(verts[(i + n - 1) % n]->co, verts[i]->co, verts[(i + 1) % n]->co));
}

/**
 * A quad grid over the ring, as Blender's Grid Fill does for a single loop: the ring is cut into
 * two opposite rails and two sides at its sharpest corner. An odd ring gets a temporary middle
 * vertex on its longest edge, merged away afterwards, so the grid face next to it becomes the one
 * triangle (as Moritz's Edit Poly Cap does).
 */
static bool fill_quads(BMesh *bm, Vector<BMVert *> verts, const bool smooth)
{
  BMVert *extra = nullptr;
  BMVert *extra_neighbor = nullptr;
  if (verts.size() % 2) {
    int longest = 0;
    float length = -1.0f;
    for (const int i : verts.index_range()) {
      const float l = len_v3v3(verts[i]->co, verts[(i + 1) % verts.size()]->co);
      if (l > length) {
        length = l;
        longest = i;
      }
    }
    BMEdge *e = BM_edge_exists(verts[longest], verts[(longest + 1) % verts.size()]);
    if (e == nullptr) {
      return false;
    }
    extra_neighbor = verts[longest];
    extra = BM_edge_split(bm, e, verts[longest], nullptr, 0.5f);
    verts.insert(longest + 1, extra);
  }
  const int n = verts.size();
  if (n < 4) {
    return false;
  }
  /* Start at the sharpest corner. */
  int corner = 0;
  for (const int i : verts.index_range()) {
    if (turn_angle(verts, i) > turn_angle(verts, corner)) {
      corner = i;
    }
  }
  std::rotate(verts.begin(), verts.begin() + corner, verts.end());
  const int side = std::max(n / 4, 1);
  const int rail = n / 2 - side;
  bool done = false;
  if (rail >= 1) {
    clear_tags(bm);
    if (tag_ring_edges(verts, side, rail) && tag_ring_edges(verts, n / 2 + side, rail)) {
      const int faces_before = bm->totface;
      BMO_op_callf(bm,
                   BMO_FLAG_DEFAULTS,
                   "grid_fill edges=%he mat_nr=%i use_smooth=%b use_interp_simple=%b",
                   BM_ELEM_TAG,
                   0,
                   smooth,
                   false);
      done = bm->totface > faces_before;
    }
  }
  if (!done) {
    if (extra) {
      /* Back to the border as it was. */
      BMEdge *e = BM_edge_exists(extra, extra_neighbor);
      if (e) {
        BM_vert_collapse_edge(bm, e, extra, true, true, true);
      }
    }
    return false;
  }
  if (extra) {
    clear_tags(bm);
    BM_elem_flag_enable(extra, BM_ELEM_TAG);
    BM_elem_flag_enable(extra_neighbor, BM_ELEM_TAG);
    BMO_op_callf(
        bm, BMO_FLAG_DEFAULTS, "pointmerge verts=%hv merge_co=%v", BM_ELEM_TAG, extra_neighbor->co);
  }
  return true;
}

static Mesh *cap_holes_modify(ModifierData *md, const ModifierEvalContext * /*ctx*/, Mesh *mesh)
{
  const bool quad_cap = flag(*md, "quad_cap", true);
  const bool smooth = flag(*md, "smooth", false);
  BMesh *bm = to_bmesh(mesh);
  const Vector<Vector<BMVert *>> loops = border_loops(bm);
  if (loops.is_empty()) {
    BM_mesh_free(bm);
    return mesh;
  }
  for (const Vector<BMVert *> &verts : loops) {
    if (!quad_cap || !fill_quads(bm, verts, smooth)) {
      fill_ngon(bm, verts, smooth);
    }
  }
  return from_bmesh(bm, mesh);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Normal
 * \{ */

static Mesh *normal_modify(ModifierData *md, const ModifierEvalContext * /*ctx*/, Mesh *mesh)
{
  const bool unify = flag(*md, "unify", true);
  const bool flip = flag(*md, "flip", false);
  if (!unify && !flip) {
    return mesh;
  }
  BMesh *bm = to_bmesh(mesh);
  if (unify) {
    BMO_op_callf(bm, BMO_FLAG_DEFAULTS, "recalc_face_normals faces=%af");
  }
  if (flip) {
    BMO_op_callf(bm, BMO_FLAG_DEFAULTS, "reverse_faces faces=%af flip_multires=%b", false);
  }
  return from_bmesh(bm, mesh);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Mesh Clean
 * \{ */

static Mesh *mesh_clean_modify(ModifierData *md, const ModifierEvalContext * /*ctx*/, Mesh *mesh)
{
  const bool weld = flag(*md, "weld", true);
  const float weld_distance = MOD_max_mesh_float(*md, "weld_distance", 0.0001f);
  const bool straight = flag(*md, "remove_straight", true);
  const float straight_angle = MOD_max_mesh_float(*md, "straight_angle", DEG2RADF(1.0f));
  const bool loose = flag(*md, "remove_loose", true);
  const bool degenerate = flag(*md, "remove_degenerate", true);

  BMesh *bm = to_bmesh(mesh);
  if (weld) {
    BMO_op_callf(bm, BMO_FLAG_DEFAULTS, "remove_doubles verts=%av dist=%f", weld_distance);
  }
  if (degenerate) {
    BMO_op_callf(bm, BMO_FLAG_DEFAULTS, "dissolve_degenerate dist=%f edges=%ae", weld_distance);
  }
  if (loose) {
    clear_tags(bm);
    BMIter iter;
    BMEdge *e;
    BM_ITER_MESH (e, &iter, bm, BM_EDGES_OF_MESH) {
      if (e->l == nullptr) {
        BM_elem_flag_enable(e, BM_ELEM_TAG);
      }
    }
    BMO_op_callf(bm, BMO_FLAG_DEFAULTS, "delete geom=%he context=%i", BM_ELEM_TAG, DEL_EDGES);
    clear_tags(bm);
    BMVert *v;
    BM_ITER_MESH (v, &iter, bm, BM_VERTS_OF_MESH) {
      if (v->e == nullptr) {
        BM_elem_flag_enable(v, BM_ELEM_TAG);
      }
    }
    BMO_op_callf(bm, BMO_FLAG_DEFAULTS, "delete geom=%hv context=%i", BM_ELEM_TAG, DEL_VERTS);
  }
  if (straight) {
    /* What Max's Turn to Poly leaves out: a vertex with exactly two edges in a straight line. */
    clear_tags(bm);
    BMIter iter;
    BMVert *v;
    BM_ITER_MESH (v, &iter, bm, BM_VERTS_OF_MESH) {
      if (BM_vert_edge_count_is_equal(v, 2)) {
        BMEdge *e1 = v->e;
        BMEdge *e2 = BM_DISK_EDGE_NEXT(e1, v);
        const BMVert *a = BM_edge_other_vert(e1, v);
        const BMVert *b = BM_edge_other_vert(e2, v);
        if (fabsf(float(M_PI) - angle_v3v3v3(a->co, v->co, b->co)) <= straight_angle) {
          BM_elem_flag_enable(v, BM_ELEM_TAG);
        }
      }
    }
    BMO_op_callf(bm,
                 BMO_FLAG_DEFAULTS,
                 "dissolve_verts verts=%hv use_face_split=%b use_boundary_tear=%b",
                 BM_ELEM_TAG,
                 false,
                 false);
  }
  return from_bmesh(bm, mesh);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Quadify Mesh
 * \{ */

/* QuadriFlow calls its progress callback unconditionally. */
static void quadify_progress(void * /*data*/, float /*progress*/, int * /*cancel*/) {}

static Mesh *quadify_modify(ModifierData *md, const ModifierEvalContext *ctx, Mesh *mesh)
{
  /* Max's Quad Size %: the quads' size as a part of the object's bounding box diagonal. */
  const float quad_size = MOD_max_mesh_float(*md, "quad_size", 4.0f) / 100.0f;
  if (mesh->faces_num == 0 || quad_size <= 0.0f) {
    return mesh;
  }
  const std::optional<Bounds<float3>> bounds = mesh->bounds_min_max();
  if (!bounds) {
    return mesh;
  }
  const float edge = math::distance(bounds->min, bounds->max) * quad_size;
  if (edge <= 0.0f) {
    return mesh;
  }
  const Span<float3> positions = mesh->vert_positions();
  const OffsetIndices faces = mesh->faces();
  const Span<int> corner_verts = mesh->corner_verts();
  float area = 0.0f;
  for (const int i : faces.index_range()) {
    area += bke::mesh::face_area_calc(positions, corner_verts.slice(faces[i]));
  }
  const int target = std::clamp(int(area / (edge * edge)), 4, 200000);
  Mesh *result = BKE_mesh_remesh_quadriflow(mesh,
                                            target,
                                            MOD_max_mesh_int(*md, "seed", 0),
                                            flag(*md, "preserve_sharp", false),
                                            flag(*md, "preserve_boundary", true),
                                            false,
                                            quadify_progress,
                                            nullptr);
  if (result == nullptr) {
    BKE_modifier_set_error(ctx->object, md, "Could not quadify this mesh (it must be manifold)");
    return mesh;
  }
  bke::mesh_remesh_reproject_attributes(*mesh, *result);
  return result;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Retopology
 *
 * Max's Retopology modifier: clean the input (non-manifold input through a voxel pass, which is
 * where QuadriFlow alone usually fails), optionally solve one half and mirror it, then QuadriFlow
 * to a face count, and finally Conform (project onto the input) and Relax.
 * \{ */

/** Weld, remove loose and degenerate parts; returns whether the result is manifold. */
static Mesh *retopology_clean(const Mesh *mesh, const float dist, bool &r_manifold)
{
  BMesh *bm = to_bmesh(mesh);
  BMO_op_callf(bm, BMO_FLAG_DEFAULTS, "remove_doubles verts=%av dist=%f", dist);
  BMO_op_callf(bm, BMO_FLAG_DEFAULTS, "dissolve_degenerate dist=%f edges=%ae", dist);
  clear_tags(bm);
  BMIter iter;
  BMEdge *e;
  BM_ITER_MESH (e, &iter, bm, BM_EDGES_OF_MESH) {
    if (e->l == nullptr) {
      BM_elem_flag_enable(e, BM_ELEM_TAG);
    }
  }
  BMO_op_callf(bm, BMO_FLAG_DEFAULTS, "delete geom=%he context=%i", BM_ELEM_TAG, DEL_EDGES);
  clear_tags(bm);
  BMVert *v;
  BM_ITER_MESH (v, &iter, bm, BM_VERTS_OF_MESH) {
    if (v->e == nullptr) {
      BM_elem_flag_enable(v, BM_ELEM_TAG);
    }
  }
  BMO_op_callf(bm, BMO_FLAG_DEFAULTS, "delete geom=%hv context=%i", BM_ELEM_TAG, DEL_VERTS);
  r_manifold = true;
  BM_ITER_MESH (e, &iter, bm, BM_EDGES_OF_MESH) {
    if (!BM_edge_is_manifold(e) && !BM_edge_is_boundary(e)) {
      r_manifold = false;
      break;
    }
  }
  BM_ITER_MESH (v, &iter, bm, BM_VERTS_OF_MESH) {
    if (!r_manifold) {
      break;
    }
    if (!BM_vert_is_manifold(v) && !BM_vert_is_boundary(v)) {
      r_manifold = false;
    }
  }
  return from_bmesh(bm, mesh);
}

/** Cut away the positive side of `axis` (the side Symmetrize mirrors over). */
static Mesh *retopology_half(const Mesh *mesh, const int axis)
{
  BMesh *bm = to_bmesh(mesh);
  float plane_co[3] = {0.0f, 0.0f, 0.0f};
  float plane_no[3] = {0.0f, 0.0f, 0.0f};
  plane_no[axis] = 1.0f;
  BMO_op_callf(bm,
               BMO_FLAG_DEFAULTS,
               "bisect_plane geom=%avef dist=%f plane_co=%v plane_no=%v use_snap_center=%b "
               "clear_outer=%b clear_inner=%b",
               0.00001f,
               plane_co,
               plane_no,
               true,
               true,
               false);
  return from_bmesh(bm, mesh);
}

static Mesh *retopology_mirror(Mesh *mesh, const int axis, const float dist)
{
  BMesh *bm = to_bmesh(mesh);
  BMO_op_callf(bm,
               BMO_FLAG_DEFAULTS,
               "symmetrize input=%avef direction=%i dist=%f use_shapekey=%b",
               axis,
               dist,
               false);
  Mesh *result = from_bmesh(bm, mesh);
  BKE_id_free(nullptr, mesh);
  return result;
}

/** Conform and Relax: smooth the inner vertices, then pull every vertex onto `surface`. */
static void retopology_conform(Mesh &mesh, const Mesh &surface, const int relax_iterations)
{
  bke::BVHTreeFromMesh tree = surface.bvh_corner_tris();
  if (tree.tree == nullptr) {
    return;
  }
  MutableSpan<float3> positions = mesh.vert_positions_for_write();
  const Span<int2> edges = mesh.edges();
  Array<int> edge_faces(edges.size(), 0);
  const OffsetIndices faces = mesh.faces();
  const Span<int> corner_edges = mesh.corner_edges();
  for (const int i : faces.index_range()) {
    for (const int e : corner_edges.slice(faces[i])) {
      edge_faces[e]++;
    }
  }
  Array<bool> fixed(positions.size(), false);
  for (const int e : edges.index_range()) {
    if (edge_faces[e] < 2) {
      fixed[edges[e][0]] = fixed[edges[e][1]] = true;
    }
  }
  auto project = [&]() {
    for (float3 &co : positions) {
      BVHTreeNearest nearest;
      nearest.index = -1;
      nearest.dist_sq = FLT_MAX;
      BLI_bvhtree_find_nearest(tree.tree, co, &nearest, tree.nearest_callback, &tree);
      if (nearest.index != -1) {
        co = float3(nearest.co);
      }
    }
  };
  project();
  Array<float3> sum(positions.size());
  Array<int> count(positions.size());
  for ([[maybe_unused]] const int iteration : IndexRange(relax_iterations)) {
    sum.fill(float3(0.0f));
    count.fill(0);
    for (const int2 &edge : edges) {
      sum[edge[0]] += positions[edge[1]];
      sum[edge[1]] += positions[edge[0]];
      count[edge[0]]++;
      count[edge[1]]++;
    }
    for (const int v : positions.index_range()) {
      if (!fixed[v] && count[v] > 0) {
        positions[v] = math::interpolate(positions[v], sum[v] / float(count[v]), 0.5f);
      }
    }
    project();
  }
  mesh.tag_positions_changed();
}

static Mesh *retopology_modify(ModifierData *md, const ModifierEvalContext *ctx, Mesh *mesh)
{
  const int face_count = MOD_max_mesh_int(*md, "face_count", 2000);
  const int symmetry = std::clamp(MOD_max_mesh_int(*md, "symmetry_axis", -1), -1, 2);
  const int relax = std::clamp(MOD_max_mesh_int(*md, "relax_iterations", 2), 0, 50);
  if (mesh->faces_num == 0 || face_count < 4) {
    return mesh;
  }
  const std::optional<Bounds<float3>> bounds = mesh->bounds_min_max();
  if (!bounds) {
    return mesh;
  }
  const float diagonal = math::distance(bounds->min, bounds->max);

  /* Pre-processing. */
  bool manifold = true;
  Mesh *clean = retopology_clean(mesh, diagonal * 0.00001f, manifold);
  if (!manifold) {
    Mesh *voxel = BKE_mesh_remesh_voxel(clean, diagonal / 200.0f, 0.0f, 0.0f, nullptr);
    if (voxel != nullptr) {
      BKE_id_free(nullptr, clean);
      clean = voxel;
    }
  }
  /* Symmetry: solve one half (bisected at the object's origin), mirror it afterwards. */
  Mesh *input = clean;
  if (symmetry != -1) {
    input = retopology_half(clean, symmetry);
  }
  Mesh *result = BKE_mesh_remesh_quadriflow(input,
                                            symmetry != -1 ? face_count / 2 : face_count,
                                            MOD_max_mesh_int(*md, "seed", 0),
                                            flag(*md, "preserve_sharp", true),
                                            flag(*md, "preserve_boundary", true),
                                            false,
                                            quadify_progress,
                                            nullptr);
  if (result == nullptr) {
    if (input != clean) {
      BKE_id_free(nullptr, input);
    }
    BKE_id_free(nullptr, clean);
    BKE_modifier_set_error(ctx->object, md, "Retopology failed on this mesh");
    return mesh;
  }
  /* Post-processing, on the half before mirroring, so the result stays exactly symmetric. */
  if (flag(*md, "conform", true)) {
    retopology_conform(*result, *input, relax);
  }
  if (input != clean) {
    BKE_id_free(nullptr, input);
  }
  if (symmetry != -1) {
    result = retopology_mirror(result, symmetry, diagonal * 0.001f);
  }
  BKE_id_free(nullptr, clean);
  bke::mesh_remesh_reproject_attributes(*mesh, *result);
  return result;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name ProOptimizer
 * \{ */

/** The edge separates different UVs (a seam in the first UV map). */
static bool uv_seam_edge(const BMEdge *e, const int cd_uv)
{
  if (cd_uv == -1 || e->l == nullptr || e->l->radial_next == e->l) {
    return false;
  }
  const BMLoop *l_a = e->l;
  const BMLoop *l_b = e->l->radial_next;
  /* The loops of the same vertex on both sides: a loop starts at its vertex. */
  const BMLoop *l_b_same = (l_b->v == l_a->v) ? l_b : l_b->next;
  const BMLoop *l_b_other = (l_b->v == l_a->v) ? l_b->next : l_b;
  return !equals_v2v2(BM_ELEM_CD_GET_FLOAT_P(l_a, cd_uv),
                      BM_ELEM_CD_GET_FLOAT_P(l_b_same, cd_uv)) ||
         !equals_v2v2(BM_ELEM_CD_GET_FLOAT_P(l_a->next, cd_uv),
                      BM_ELEM_CD_GET_FLOAT_P(l_b_other, cd_uv));
}

static Mesh *pro_optimizer_modify(ModifierData *md,
                                  const ModifierEvalContext * /*ctx*/,
                                  Mesh *mesh)
{
  const float percent = MOD_max_mesh_float(*md, "vertex_percent", 50.0f);
  if (percent >= 100.0f || mesh->faces_num == 0) {
    return mesh;
  }
  const bool borders = flag(*md, "protect_borders", true);
  const bool materials = flag(*md, "keep_material_boundaries", true);
  const bool uvs = flag(*md, "keep_uv_boundaries", true);
  const bool normals = flag(*md, "keep_normals", false);
  const bool compact = flag(*md, "favor_compact", true);
  const int symmetry = MOD_max_mesh_int(*md, "symmetry_axis", -1);

  BMesh *bm = to_bmesh(mesh);
  const int cd_uv = CustomData_get_offset(&bm->ldata, CD_PROP_FLOAT2);

  /* Protect Borders: the border vertices stay (a weight of 0 never collapses). */
  Array<float> weights(bm->totvert, 1.0f);
  bool any_kept = false;
  BMIter iter;
  BMVert *v;
  int i;
  BM_ITER_MESH_INDEX (v, &iter, bm, BM_VERTS_OF_MESH, i) {
    BM_elem_index_set(v, i);
    if (borders && BM_vert_is_boundary(v)) {
      weights[i] = 0.0f;
      any_kept = true;
    }
  }
  bm->elem_index_dirty &= ~BM_VERT;

  /* Material and UV boundaries and hard edges stay in place but can still lose vertices along
   * their length, as in Max (the decimation holds them like open borders). */
  bool any_feature = false;
  BMEdge *e;
  BM_ITER_MESH (e, &iter, bm, BM_EDGES_OF_MESH) {
    bool feature = false;
    if (e->l && e->l->radial_next != e->l) {
      feature = (materials && e->l->f->mat_nr != e->l->radial_next->f->mat_nr) ||
                (uvs && uv_seam_edge(e, cd_uv)) ||
                (normals && !BM_elem_flag_test(e, BM_ELEM_SMOOTH));
    }
    BM_elem_flag_set(e, BM_ELEM_TAG_ALT, feature);
    any_feature |= feature;
  }

  BM_mesh_decimate_collapse_ex(bm,
                               std::clamp(percent / 100.0f, 0.0f, 1.0f),
                               any_kept ? weights.data() : nullptr,
                               1.0f,
                               true,
                               std::clamp(symmetry, -1, 2),
                               0.00002f,
                               any_feature,
                               compact ? 1.0f : 0.0f);
  BM_mesh_elem_hflag_disable_all(bm, BM_EDGE, BM_ELEM_TAG_ALT, false);
  return from_bmesh(bm, mesh);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name VertexPaint
 * \{ */

bool MOD_vertex_paint_has_colors(const ModifierData &md)
{
  const IDProperty *colors = setting(md, "colors");
  return colors && colors->type == IDP_ARRAY && colors->len > 0;
}

void MOD_vertex_paint_clear(ModifierData &md)
{
  if (IDProperty *colors = md.system_properties ?
                               IDP_GetPropertyFromGroup_null(md.system_properties, "colors") :
                               nullptr)
  {
    IDP_FreeFromGroup(md.system_properties, colors);
  }
}

bool MOD_vertex_paint_store(ModifierData &md, const Mesh &mesh, ReportList *reports)
{
  const char *name = mesh.active_color_attribute;
  const bke::AttributeAccessor attributes = mesh.attributes();
  const std::optional<bke::AttributeMetaData> meta = name ? attributes.lookup_meta_data(name) :
                                                            std::nullopt;
  if (!meta || !ELEM(meta->domain, bke::AttrDomain::Point, bke::AttrDomain::Corner)) {
    BKE_report(reports, RPT_ERROR, "VertexPaint: the mesh has no color attribute to keep");
    return false;
  }
  const VArraySpan<ColorGeometry4f> colors = *attributes.lookup<ColorGeometry4f>(name,
                                                                                meta->domain);
  Array<float> values(colors.size() * 4);
  for (const int i : colors.index_range()) {
    values[i * 4] = colors[i].r;
    values[i * 4 + 1] = colors[i].g;
    values[i * 4 + 2] = colors[i].b;
    values[i * 4 + 3] = colors[i].a;
  }
  ensure_group(md);
  IDP_ReplaceInGroup(md.system_properties,
                     bke::idprop::create("colors", values.as_span()).release());
  MOD_max_mesh_int_set(md, "domain", meta->domain == bke::AttrDomain::Corner ? 1 : 0);
  MOD_max_mesh_tag(md, "VERTEX_PAINT");
  return true;
}

static Mesh *vertex_paint_modify(ModifierData *md, const ModifierEvalContext *ctx, Mesh *mesh)
{
  const IDProperty *colors = setting(*md, "colors");
  if (colors == nullptr || colors->type != IDP_ARRAY || colors->subtype != IDP_FLOAT) {
    return mesh;
  }
  const bke::AttrDomain domain = MOD_max_mesh_int(*md, "domain", 0) == 1 ?
                                     bke::AttrDomain::Corner :
                                     bke::AttrDomain::Point;
  const int count = domain == bke::AttrDomain::Corner ? mesh->corners_num : mesh->verts_num;
  if (colors->len != count * 4) {
    BKE_modifier_set_error(ctx->object, md, "The mesh below changed: paint again");
    return mesh;
  }
  const float *values = static_cast<const float *>(IDP_array_voidp_get(colors));
  const IDProperty *name_prop = setting(*md, "layer");
  const std::string name = (name_prop && name_prop->type == IDP_STRING) ?
                               std::string(IDP_string_get(name_prop)) :
                               std::string("VertexPaint");
  Mesh *result = BKE_mesh_copy_for_eval(*mesh);
  bke::MutableAttributeAccessor attributes = result->attributes_for_write();
  attributes.remove(name);
  bke::SpanAttributeWriter<ColorGeometry4f> writer =
      attributes.lookup_or_add_for_write_only_span<ColorGeometry4f>(name, domain);
  if (!writer) {
    return result;
  }
  for (const int i : IndexRange(count)) {
    writer.span[i] = ColorGeometry4f(
        values[i * 4], values[i * 4 + 1], values[i * 4 + 2], values[i * 4 + 3]);
  }
  writer.finish();
  MEM_SAFE_DELETE(result->active_color_attribute);
  result->active_color_attribute = BLI_strdup(name.c_str());
  MEM_SAFE_DELETE(result->default_color_attribute);
  result->default_color_attribute = BLI_strdup(name.c_str());
  return result;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Type infos
 * \{ */

static void draw_settings(const bContext * /*C*/, Panel *panel)
{
  ui::Layout &layout = *panel->layout;
  PointerRNA ob_ptr;
  PointerRNA *ptr = modifier_panel_get_property_pointers(panel, &ob_ptr);
  layout.use_property_split_set(true);
  /* The settings of the modifier's own RNA struct (not the ones every modifier has), in order. */
  RNA_STRUCT_BEGIN (ptr, prop) {
    const char *identifier = RNA_property_identifier(prop);
    if ((RNA_property_flag(prop) & PROP_HIDDEN) || !RNA_property_editable(ptr, prop) ||
        RNA_struct_type_find_property(RNA_Modifier, identifier))
    {
      continue;
    }
    layout.prop(ptr, identifier, UI_ITEM_NONE, std::nullopt, ICON_NONE);
  }
  RNA_STRUCT_END;
  modifier_error_message_draw(layout, ptr);
}

static void panel_register_cap_holes(ARegionType *region_type)
{
  modifier_panel_register(region_type, eModifierType_CapHoles, draw_settings);
}
static void panel_register_normal(ARegionType *region_type)
{
  modifier_panel_register(region_type, eModifierType_MaxNormal, draw_settings);
}
static void panel_register_mesh_clean(ARegionType *region_type)
{
  modifier_panel_register(region_type, eModifierType_MeshClean, draw_settings);
}
static void panel_register_quadify(ARegionType *region_type)
{
  modifier_panel_register(region_type, eModifierType_QuadifyMesh, draw_settings);
}
static void panel_register_pro_optimizer(ARegionType *region_type)
{
  modifier_panel_register(region_type, eModifierType_ProOptimizer, draw_settings);
}
static void panel_register_vertex_paint(ARegionType *region_type)
{
  modifier_panel_register(region_type, eModifierType_VertexPaint, draw_settings);
}
static void panel_register_retopology(ARegionType *region_type)
{
  modifier_panel_register(region_type, eModifierType_Retopology, draw_settings);
}

#define MX_INIT(fn, mx_type) \
  static void fn(ModifierData *md) \
  { \
    MOD_max_mesh_tag(*md, mx_type); \
  }

MX_INIT(init_cap_holes, "CAP_HOLES")
MX_INIT(init_normal, "MAX_NORMAL")
MX_INIT(init_mesh_clean, "MESH_CLEAN")
MX_INIT(init_quadify, "QUADIFY_MESH")
MX_INIT(init_pro_optimizer, "PRO_OPTIMIZER")
MX_INIT(init_vertex_paint, "VERTEX_PAINT")
MX_INIT(init_retopology, "RETOPOLOGY")

#undef MX_INIT

#define MX_TYPE_INFO(var, idname, label, srna, kind, icon, modify, init, panel) \
  ModifierTypeInfo var = { \
      /*idname*/ idname, \
      /*name*/ label, \
      /*struct_name*/ "ModifierData", \
      /*struct_size*/ sizeof(ModifierData), \
      /*srna*/ srna, \
      /*type*/ kind, \
      /*flags*/ (eModifierTypeFlag_AcceptsMesh | eModifierTypeFlag_SupportsEditmode | \
                 eModifierTypeFlag_EnableInEditmode), \
      /*icon*/ icon, \
      /*copy_data*/ BKE_modifier_copydata_generic, \
      /*deform_verts*/ nullptr, \
      /*deform_matrices*/ nullptr, \
      /*deform_verts_EM*/ nullptr, \
      /*deform_matrices_EM*/ nullptr, \
      /*modify_mesh*/ modify, \
      /*modify_geometry_set*/ nullptr, \
      /*init_data*/ init, \
      /*required_data_mask*/ nullptr, \
      /*free_data*/ nullptr, \
      /*is_disabled*/ nullptr, \
      /*update_depsgraph*/ nullptr, \
      /*depends_on_time*/ nullptr, \
      /*depends_on_normals*/ nullptr, \
      /*foreach_ID_link*/ nullptr, \
      /*foreach_tex_link*/ nullptr, \
      /*free_runtime_data*/ nullptr, \
      /*panel_register*/ panel, \
      /*blend_write*/ nullptr, \
      /*blend_read*/ nullptr, \
      /*foreach_cache*/ nullptr, \
      /*foreach_working_space_color*/ nullptr, \
  };

MX_TYPE_INFO(modifierType_CapHoles,
             "CapHoles",
             N_("Cap Holes"),
             &RNA_CapHolesModifier,
             ModifierTypeType::Constructive,
             ICON_MOD_SOLIDIFY,
             cap_holes_modify,
             init_cap_holes,
             panel_register_cap_holes)
MX_TYPE_INFO(modifierType_MaxNormal,
             "MaxNormal",
             N_("Normal"),
             &RNA_MaxNormalModifier,
             ModifierTypeType::Nonconstructive,
             ICON_NORMALS_FACE,
             normal_modify,
             init_normal,
             panel_register_normal)
MX_TYPE_INFO(modifierType_MeshClean,
             "MeshClean",
             N_("Mesh Clean"),
             &RNA_MeshCleanModifier,
             ModifierTypeType::Constructive,
             ICON_BRUSH_DATA,
             mesh_clean_modify,
             init_mesh_clean,
             panel_register_mesh_clean)
MX_TYPE_INFO(modifierType_QuadifyMesh,
             "QuadifyMesh",
             N_("Quadify Mesh"),
             &RNA_QuadifyMeshModifier,
             ModifierTypeType::Constructive,
             ICON_MOD_REMESH,
             quadify_modify,
             init_quadify,
             panel_register_quadify)
MX_TYPE_INFO(modifierType_ProOptimizer,
             "ProOptimizer",
             N_("ProOptimizer"),
             &RNA_ProOptimizerModifier,
             ModifierTypeType::Nonconstructive,
             ICON_MOD_DECIM,
             pro_optimizer_modify,
             init_pro_optimizer,
             panel_register_pro_optimizer)
MX_TYPE_INFO(modifierType_VertexPaint,
             "VertexPaint",
             N_("VertexPaint"),
             &RNA_VertexPaintModifier,
             ModifierTypeType::NonGeometrical,
             ICON_VPAINT_HLT,
             vertex_paint_modify,
             init_vertex_paint,
             panel_register_vertex_paint)
MX_TYPE_INFO(modifierType_Retopology,
             "Retopology",
             N_("Retopology"),
             &RNA_RetopologyModifier,
             ModifierTypeType::Constructive,
             ICON_MOD_REMESH,
             retopology_modify,
             init_retopology,
             panel_register_retopology)

#undef MX_TYPE_INFO

/** \} */

}  // namespace blender
