/* SPDX-FileCopyrightText: 2026 Moritz Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup modifiers
 *
 * Moritz: Edit Poly modifier, see `moritz/docs/edit_poly_core_design.md`.
 */

#pragma once

namespace blender {

struct Main;
struct Mesh;
struct ModifierData;
struct ReportList;

/** How the edit is stored. */
enum class EditPolyMode : int {
  /** Nothing stored yet: the modifier passes its input through. */
  None = 0,
  /** Same topology as the input: one offset per input vertex. */
  Deform = 1,
  /** Topology edited: a stored result mesh that follows the input through `mx_orig`. */
  Topology = 2,
};

EditPolyMode MOD_edit_poly_mode(const ModifierData &md);

/**
 * Store an edit: `edited` is the edited version of `input` (the modifier's input mesh).
 * Vertices of `edited` may carry an int point attribute `mx_orig`, the input vertex each came
 * from (-1 for new ones). Without it, vertices map by index.
 */
bool MOD_edit_poly_store(
    Main &bmain, ModifierData &md, const Mesh &input, const Mesh &edited, ReportList *reports);

/** The stored result mesh (Topology mode), otherwise null. */
Mesh *MOD_edit_poly_result(const ModifierData &md);

}  // namespace blender
