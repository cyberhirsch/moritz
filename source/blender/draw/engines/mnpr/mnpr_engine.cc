/* SPDX-FileCopyrightText: 2021 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup mnpr
 */

#include "BLI_rect.hh"

#include "GPU_framebuffer.hh"

#include "ED_screen.hh"
#include "ED_view3d.hh"

#include "DRW_render.hh"

#include "RE_pipeline.h"

#include "mnpr_engine.h" /* Own include. */

#include "draw_view_data.hh"

#include "mnpr_instance.hh"

namespace blender {

namespace mnpr {

DrawEngine *Engine::create_instance()
{
  return new Instance();
}

void Engine::free_static()
{
  ShaderModule::module_free();
}

}  // namespace mnpr

using namespace blender::mnpr;

static void mnpr_render(RenderEngine *engine, Depsgraph *depsgraph)
{
  Instance *instance = nullptr;

  auto mnpr_render_to_image = [&](RenderEngine *engine, RenderLayer *layer, const rcti /*rect*/) {
    Render *render = engine->re;
    Object *camera_original_ob = RE_GetCamera(engine->re);
    const char *viewname = RE_GetActiveRenderView(engine->re);
    int size[2] = {engine->resolution_x, engine->resolution_y};

    /* Avoid leaking in the case of multiview. (see #145743) */
    delete instance;
    /* WORKAROUND: Fails if created in the parent scope. Must be because of lack of active
     * `DRWContext`. To be revisited. */
    instance = new Instance();

    rctf view_rect;
    rcti rect;
    RE_GetViewPlane(render, &view_rect, &rect);
    rcti visible_rect = rect;

    instance->init(size, &rect, &visible_rect, engine, depsgraph, camera_original_ob, layer);
    instance->render_frame(engine, layer, viewname);
  };

  auto mnpr_store_metadata = [&](RenderResult *render_result) {
    instance->store_metadata(render_result);
  };

  DRW_render_to_image(engine, depsgraph, mnpr_render_to_image, mnpr_store_metadata);

  delete instance;
}

static void mnpr_render_update_passes(RenderEngine *engine, Scene *scene, ViewLayer *view_layer)
{
  Instance::update_passes(engine, scene, view_layer);
}

RenderEngineType DRW_engine_viewport_mnpr_type = {
    /*next*/ nullptr,
    /*prev*/ nullptr,
    /*idname*/ "MORITZ_MNPR",
    /*name*/ N_("mNPR"),
    /*flag*/ RE_INTERNAL | RE_USE_PREVIEW | RE_USE_STEREO_VIEWPORT | RE_USE_GPU_CONTEXT,
    /*update*/ nullptr,
    /*render*/ &mnpr_render,
    /*render_frame_finish*/ nullptr,
    /*draw*/ nullptr,
    /*bake*/ nullptr,
    /*view_update*/ nullptr,
    /*view_draw*/ nullptr,
    /*view_pause*/ nullptr,
    /*view_resume*/ nullptr,
    /*update_script_node*/ nullptr,
    /*update_render_passes*/ &mnpr_render_update_passes,
    /*update_custom_camera*/ nullptr,
    /*rna_ext*/
    {
        /*data*/ nullptr,
        /*srna*/ nullptr,
        /*call*/ nullptr,
    },
};

}  // namespace blender
