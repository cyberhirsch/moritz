/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

#pragma once

/** \file
 * \ingroup bmesh
 */

#include "intern/bmesh_operator_api.hh"

#include "bmesh_class.hh"

namespace blender {

/**
 * \brief BM_mesh_decimate
 * \param bm: The mesh
 * \param factor: face count multiplier [0 - 1]
 * \param vweights: Optional array of vertex aligned weights [0 - 1],
 *        a vertex group is the usual source for this.
 * \param symmetry_axis: Axis of symmetry, -1 to disable mirror decimate.
 * \param symmetry_eps: Threshold when matching mirror verts.
 *
 * \note The caller is responsible for recalculating face and vertex normals.
 * - Vertex normals are maintained while decimating,
 *   although they won't necessarily match the final recalculated normals.
 * - Face normals are not maintained at all.
 */
void BM_mesh_decimate_collapse(BMesh *bm,
                               float factor,
                               float *vweights,
                               float vweight_factor,
                               bool do_triangulate,
                               int symmetry_axis,
                               float symmetry_eps);

/**
 * Moritz (3ds Max's ProOptimizer): #BM_mesh_decimate_collapse, plus
 * - edges tagged #BM_ELEM_TAG_ALT are kept in place like open borders: a plane through the edge on
 *   each side holds its vertices, so the edge can still lose vertices along its length (UV seams,
 *   material boundaries, hard edges);
 * - `compact_weight` > 0 favors compact triangles: thin results cost more.
 */
void BM_mesh_decimate_collapse_ex(BMesh *bm,
                                  float factor,
                                  float *vweights,
                                  float vweight_factor,
                                  bool do_triangulate,
                                  int symmetry_axis,
                                  float symmetry_eps,
                                  bool use_feature_edges,
                                  float compact_weight);

/**
 * \param tag_only: so we can call this from an operator.
 */
void BM_mesh_decimate_unsubdivide_ex(BMesh *bm, int iterations, bool tag_only);
void BM_mesh_decimate_unsubdivide(BMesh *bm, int iterations);

void BM_mesh_decimate_dissolve_ex(BMesh *bm,
                                  float angle_limit,
                                  bool do_dissolve_boundaries,
                                  BMO_Delimit delimit,
                                  BMVert **vinput_arr,
                                  int vinput_len,
                                  BMEdge **einput_arr,
                                  int einput_len,
                                  short oflag_out);
void BM_mesh_decimate_dissolve(BMesh *bm,
                               float angle_limit,
                               bool do_dissolve_boundaries,
                               const BMO_Delimit delimit);

}  // namespace blender
