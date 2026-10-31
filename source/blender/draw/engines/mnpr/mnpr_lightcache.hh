/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup mnpr
 */

#pragma once

#include "BLI_vector.hh"
#include <string>
struct MNPR_LightBake;
namespace blender {

struct wmWindowManager;
struct wmWindow;
struct Main;
struct ViewLayer;
struct Scene;
struct Object;
struct wmJob;
struct wmJobWorkerStatus;

/** Opaque type hiding mnpr::LightBake. */
/* -------------------------------------------------------------------- */
/** \name Light Bake Job
 * \{ */

/**
 * Create the job description.
 * This is called for asynchronous (modal) bake operator.
 * The actual work will be done by `MNPR_lightbake_job()`.
 * IMPORTANT: Must run on the main thread because of potential GPUContext creation.
 */
wmJob *MNPR_lightbake_job_create(wmWindowManager *wm,
                                  wmWindow *win,
                                  Main *bmain,
                                  ViewLayer *view_layer,
                                  Scene *scene,
                                  Vector<Object *> original_probes,
                                  std::string &report,
                                  int delay_ms,
                                  int frame);

/**
 * Allocate dependency graph and job description (MNPR_LightBake).
 * Dependency graph evaluation does *not* happen here. It is delayed until
 * `MNPR_lightbake_job` runs.
 * IMPORTANT: Must run on the main thread because of potential GPUContext creation.
 * Return `MNPR_LightBake *` but cast to `void *` because of compatibility with existing
 * EEVEE function.
 */
void *MNPR_lightbake_job_data_alloc(Main *bmain,
                                     ViewLayer *view_layer,
                                     Scene *scene,
                                     Vector<Object *> original_probes,
                                     std::string &report,
                                     int frame);

/**
 * Free the job data.
 * NOTE: Does not free the GPUContext. This is the responsibility of `MNPR_lightbake_job()`
 */
void MNPR_lightbake_job_data_free(/*MNPR_LightBake*/ void *job_data);

/**
 * Callback for updating original scene light cache with bake result.
 * Run by the job system for each update step and the finish step.
 * This is called manually by `MNPR_lightbake_job()` if not run from a job.
 */
void MNPR_lightbake_update(/*MNPR_LightBake*/ void *job_data);

/**
 * Do the full light baking for all samples.
 * Will call `MNPR_lightbake_update()` on finish.
 */
void MNPR_lightbake_job(/*MNPR_LightBake*/ void *job_data, wmJobWorkerStatus *worker_status);

/** \} */

}  // namespace blender
