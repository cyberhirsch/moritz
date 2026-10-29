/* SPDX-FileCopyrightText: 2026 Moritz Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup modifiers
 *
 * Moritz: 3ds Max's mesh modifiers (Cap Holes, Normal, Mesh Clean, Quadify Mesh, ProOptimizer,
 * VertexPaint). Their settings are ID properties of a plain #ModifierData; RNA reads and writes
 * them through these functions.
 */

#pragma once

#include <string>

#include "BLI_string_ref.hh"

namespace blender {

struct Mesh;
struct ModifierData;
struct ReportList;

int MOD_max_mesh_int(const ModifierData &md, StringRef name, int fallback);
float MOD_max_mesh_float(const ModifierData &md, StringRef name, float fallback);
void MOD_max_mesh_int_set(ModifierData &md, StringRef name, int value);
void MOD_max_mesh_float_set(ModifierData &md, StringRef name, float value);
/** Store the kind (`mx_type`), so stock Blender's "None" modifier is revived as this one. */
void MOD_max_mesh_tag(ModifierData &md, StringRefNull mx_type);
std::string MOD_max_mesh_string(const ModifierData &md, StringRef name, StringRef fallback);
void MOD_max_mesh_string_set(ModifierData &md, StringRef name, StringRefNull value);

/** VertexPaint: keep the active color attribute of `mesh` (the modifier's input, painted). */
bool MOD_vertex_paint_store(ModifierData &md, const Mesh &mesh, ReportList *reports);
void MOD_vertex_paint_clear(ModifierData &md);
bool MOD_vertex_paint_has_colors(const ModifierData &md);

}  // namespace blender
