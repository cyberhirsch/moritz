/* SPDX-FileCopyrightText: 2016 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup DNA
 */

#pragma once

#include "DRW_render.hh"
#include "RE_engine.h"

namespace blender {

extern RenderEngineType DRW_engine_viewport_mnpr_type;

namespace mnpr {

struct Engine : public DrawEngine::Pointer {
  DrawEngine *create_instance() final;

  static void free_static();
};

}  // namespace mnpr
}  // namespace blender
