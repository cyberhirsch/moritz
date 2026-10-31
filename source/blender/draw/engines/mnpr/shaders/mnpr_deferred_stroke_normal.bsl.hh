/* SPDX-FileCopyrightText: 2026 Moritz Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/**
 * mNPR: painted strokes. Splits surfaces into stroke-shaped cells and gives every pixel of a
 * cell the same shading normal, so each stroke lights as one flat facet (the "painted
 * object-space normal map" look, computed instead of painted).
 *
 * Cells are anisotropic 3D Voronoi cells in world space: every cell has its own random direction
 * and is stretched along it. The cell's normal is read around the screen position of the cell's
 * centre, from pixels of the same cell; every pixel of a cell reads the same samples, so all of
 * them get exactly the same normal.
 */

#pragma once

#include "draw_view.bsl.hh"
#include "mnpr_gbuffer_types.bsl.hh"
#include "mnpr_hiz.bsl.hh"
#include "mnpr_sampling_lib.bsl.hh"

namespace mnpr::stroke {

struct Cell {
  int3 id;
  /* Cell centre in grid space. */
  float3 center;
};

float3 cell_direction(int3 c)
{
  float3 d = random::pcg_3d(float3(c) + 17.31f) * 2.0f - 1.0f;
  return normalize(d + float3(0.0f, 0.0f, 1e-4f));
}

/* Nearest stretched feature point to `q` (grid space). */
Cell find_cell(float3 q, float stretch)
{
  int3 base = int3(floor(q));
  float best = 1e30f;
  Cell cell;
  cell.id = base;
  cell.center = float3(base);
  for (int z = -1; z <= 1; z++) {
    for (int y = -1; y <= 1; y++) {
      for (int x = -1; x <= 1; x++) {
        int3 c = base + int3(x, y, z);
        float3 f = float3(c) + random::pcg_3d(float3(c));
        float3 v = q - f;
        float3 d = cell_direction(c);
        float along = dot(v, d);
        float3 perp = v - along * d;
        float dist = along * along / (stretch * stretch) + dot(perp, perp);
        if (dist < best) {
          best = dist;
          cell.id = c;
          cell.center = f;
        }
      }
    }
  }
  return cell;
}

}  // namespace mnpr::stroke

namespace mnpr {

struct StrokeNormal {
  [[push_constant]] const float stroke_size;
  [[push_constant]] const float stroke_stretch;
  [[push_constant]] const float stroke_strength;

  [[sampler(0)]] usampler2DArray gbuf_header_tx;
  [[sampler(1)]] sampler2DArray gbuf_normal_copy_tx;
  [[image(0, read_write, UNORM_16_16)]] image2DArray gbuf_normal_img;
};

[[compute, local_size(8, 8)]]
void stroke_normal_comp([[resource_table]] StrokeNormal &srt,
                        [[resource_table]] const draw::View &views,
                        [[resource_table]] const HiZ &hiz,
                        [[global_invocation_id]] const uint3 global_id)
{
  const int2 extent = textureSize(srt.gbuf_normal_copy_tx, 0).xy;
  int2 texel = int2(global_id.xy);
  if (any(greaterThanEqual(texel, extent))) {
    return;
  }
  if (texelFetch(srt.gbuf_header_tx, int3(texel, 0), 0).r == 0u) {
    /* Background or no closure. */
    return;
  }

  const ViewMatrices view = views.get(0);
  const float inv_size = 1.0f / max(srt.stroke_size, 1e-4f);
  const float stretch = max(srt.stroke_stretch, 1.0f);

  const float depth = texelFetch(hiz.hiz_tx, texel, 0).r;
  const float3 P = view.point_screen_to_world(float3((float2(texel) + 0.5f) / float2(extent), depth));
  const stroke::Cell cell = stroke::find_cell(P * inv_size, stretch);

  /* Sample around the screen position of the cell centre. Same pattern for every pixel of the
   * cell, so all of them average the same normals. */
  const float3 center_ws = cell.center * srt.stroke_size;
  const float2 center_uv = view.point_world_to_screen(center_ws).xy;
  /* Screen radius of a stroke: project a point one stroke width away. */
  const float3 side_ws = center_ws + view.viewinv[0].xyz() * srt.stroke_size * 0.5f;
  const float radius_uv = distance(view.point_world_to_screen(side_ws).xy, center_uv);

  float3 N_sum = float3(0.0f);
  constexpr int ring_count = 3;
  constexpr int ring_samples = 8;
  for (int r = 0; r <= ring_count; r++) {
    int count = (r == 0) ? 1 : ring_samples;
    float ring_radius = radius_uv * float(r) / float(ring_count);
    for (int i = 0; i < count; i++) {
      float angle = (float(i) + 0.5f * float(r)) * (6.2831853f / float(ring_samples));
      float2 uv = center_uv + ring_radius * float2(cos(angle), sin(angle));
      if (any(lessThan(uv, float2(0.0f))) || any(greaterThanEqual(uv, float2(1.0f)))) {
        continue;
      }
      int2 s_texel = int2(uv * float2(extent));
      if (texelFetch(srt.gbuf_header_tx, int3(s_texel, 0), 0).r == 0u) {
        continue;
      }
      float s_depth = texelFetch(hiz.hiz_tx, s_texel, 0).r;
      float3 s_P = view.point_screen_to_world(float3((float2(s_texel) + 0.5f) / float2(extent),
                                                      s_depth));
      if (any(notEqual(stroke::find_cell(s_P * inv_size, stretch).id, cell.id))) {
        continue;
      }
      N_sum += gbuffer::normal_unpack(texelFetch(srt.gbuf_normal_copy_tx, int3(s_texel, 0), 0).rg);
    }
  }

  if (dot(N_sum, N_sum) < 1e-8f) {
    /* The cell centre is hidden or off screen: keep the surface normal. */
    return;
  }

  const float3 N = gbuffer::normal_unpack(
      texelFetch(srt.gbuf_normal_copy_tx, int3(texel, 0), 0).rg);
  const float3 N_stroke = normalize(N_sum);
  const float3 N_out = normalize(mix(N, N_stroke, saturate(srt.stroke_strength)));
  imageStore(srt.gbuf_normal_img, int3(texel, 0), float4(gbuffer::normal_pack(N_out), 0.0f, 0.0f));
}

PipelineCompute deferred_stroke_normal(stroke_normal_comp);

}  // namespace mnpr
