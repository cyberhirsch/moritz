/* SPDX-FileCopyrightText: 2026 Moritz Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup modifiers
 *
 * Moritz: Edit Spline modifier, see `moritz/docs/splines_max_design.md`.
 */

#pragma once

namespace blender {

struct Curves;
struct Main;
struct ModifierData;
struct Object;
struct ReportList;

/** How the edit is stored. */
enum class EditSplineMode : int {
  /** Nothing stored yet: the modifier passes its input through (plus interpolation). */
  None = 0,
  /** Same knots as the input: one offset per knot for the position and both handles. */
  Deform = 1,
  /** Knots added, removed or reconnected: stored result curves that follow the input through
   * `mx_orig`. */
  Topology = 2,
};

EditSplineMode MOD_edit_spline_mode(const ModifierData &md);

/**
 * Store an edit: `edited` is the edited version of `input` (the modifier's input curves).
 * Knots of `edited` may carry an int point attribute `mx_orig`, the input knot each came from
 * (-1 for new ones). Without it, knots map by index.
 */
bool MOD_edit_spline_store(
    Main &bmain, ModifierData &md, const Curves &input, const Curves &edited, ReportList *reports);

/** The stored result curves (Topology mode), otherwise null. */
Curves *MOD_edit_spline_result(const ModifierData &md);

/**
 * Start an Edit Mode session: store the edit and mark the modifier, so that Edit Mode on the
 * object edits the modifier's result instead of the object's splines.
 */
bool MOD_edit_spline_session_begin(
    Main &bmain, ModifierData &md, const Curves &input, const Curves &edited, ReportList *reports);
/** The Edit Spline modifier of `ob` in an Edit Mode session, or null. */
ModifierData *MOD_edit_spline_session_find(const Object &ob);
/** Write the edit-nurbs (converted to `edited`, knots mapped by `mx_orig`) into the result. */
void MOD_edit_spline_session_load(Main &bmain, ModifierData &md, const Curves &edited);
/** End the session. */
void MOD_edit_spline_session_end(Main &bmain, ModifierData &md);

}  // namespace blender
