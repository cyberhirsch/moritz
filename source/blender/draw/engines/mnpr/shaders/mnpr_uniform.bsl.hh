/* SPDX-FileCopyrightText: 2022 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

#pragma once

#include "mnpr_uniform_shared.hh"

namespace mnpr {

struct Uniform {
  [[uniform(UNIFORM_BUF_SLOT)]] const UniformData &uniform_buf;
  [[uniform(PIPELINE_BUF_SLOT)]] const PipelineInfoData &pipeline_buf;
  [[uniform(RAYTRACE_BUF_SLOT)]] const RayTraceData &raytrace_buf;
};

}  // namespace mnpr
