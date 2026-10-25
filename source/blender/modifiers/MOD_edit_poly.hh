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
struct Object;
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

/**
 * Start an Edit Mode session: store the edit (as a result mesh) and mark the modifier, so that
 * Edit Mode on the object edits the modifier's result instead of the object's mesh.
 */
bool MOD_edit_poly_session_begin(
    Main &bmain, ModifierData &md, const Mesh &input, const Mesh &edited, ReportList *reports);
/** The Edit Poly modifier of `ob` in an Edit Mode session, or null. */
ModifierData *MOD_edit_poly_session_find(const Object &ob);
/** Write the edit-mesh (converted to `edited`) into the session's result. */
void MOD_edit_poly_session_load(Main &bmain, ModifierData &md, const Mesh &edited);
/** End the session: clear the mark and store the edit compactly. */
void MOD_edit_poly_session_end(Main &bmain, ModifierData &md);

}  // namespace blender
