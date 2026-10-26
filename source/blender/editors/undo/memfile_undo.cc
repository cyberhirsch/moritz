/* SPDX-FileCopyrightText: 2023 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup edundo
 *
 * Wrapper between `ED_undo.hh` and `BKE_undo_system.hh` API's.
 */

#include "BLI_sys_types.hh"

#include "BLI_ghash.hh"
#include <string>

#include <fmt/format.h>

#include "BLI_map.hh"
#include <cstdio>

#include "BLI_path_utils.hh"
#include "BLI_time.hh"
#include "BLI_listbase.hh"

#include "DNA_ID.h"
#include "DNA_collection_types.h"
#include "DNA_layer_types.h"
#include "DNA_mesh_types.h"
#include "DNA_node_types.h"
#include "DNA_object_force_types.h"
#include "DNA_object_types.h"
#include "DNA_scene_types.h"
#include "DNA_sequence_types.h"

#include "BKE_blender_undo.hh"
#include "BKE_compositor.hh"
#include "BKE_context.hh"
#include "BKE_lib_query.hh"
#include "BKE_main.hh"
#include "BKE_modifier.hh"
#include "BKE_node.hh"
#include "BKE_preview_image.hh"
#include "BKE_scene.hh"
#include "BKE_scene_runtime.hh"
#include "BKE_undo_system.hh"

#include "../depsgraph/DEG_depsgraph.hh"

#include "WM_api.hh"
#include "WM_types.hh"

#include "ED_render.hh"
#include "ED_undo.hh"
#include "ED_util.hh"

#include "../blenloader/BLO_undofile.hh"

#include "undo_intern.hh"

namespace blender {

/* -------------------------------------------------------------------- */
/** \name Implements ED Undo System
 * \{ */

struct MemFileUndoStep {
  UndoStep step;
  MemFileUndoData *data;
};

static bool memfile_undosys_poll(bContext *C)
{
  /* other poll functions must run first, this is a catch-all. */

  if ((U.uiflag & USER_GLOBALUNDO) == 0) {
    return false;
  }

  /* Allow a single memfile undo step (the first). */
  UndoStack *ustack = ED_undo_stack_get();
  if ((ustack->step_active != nullptr) && (ED_undo_is_memfile_compatible(C) == false)) {
    return false;
  }
  return true;
}

static bool memfile_undosys_step_encode(bContext * /*C*/, Main *bmain, UndoStep *us_p)
{
  MemFileUndoStep *us = reinterpret_cast<MemFileUndoStep *>(us_p);

  /* Important we only use 'main' from the context (see: BKE_undosys_stack_init_from_main). */
  UndoStack *ustack = ED_undo_stack_get();

  if (bmain->is_memfile_undo_flush_needed) {
    ED_editors_flush_edits_ex(bmain, true);
  }

  /* can be null, use when set. */
  MemFileUndoStep *us_prev = reinterpret_cast<MemFileUndoStep *>(
      BKE_undosys_step_find_by_type(ustack, BKE_UNDOSYS_TYPE_MEMFILE));
  us->data = BKE_memfile_undo_encode(bmain, us_prev ? us_prev->data : nullptr);
  us->step.data_size = us->data->undo_size;

  /* Store the fact that we should not re-use old data with that undo step, and reset the Main
   * flag. */
  us->step.use_old_bmain_data = !bmain->use_memfile_full_barrier;
  bmain->use_memfile_full_barrier = false;

  return true;
}

static int memfile_undosys_step_id_reused_cb(LibraryIDLinkCallbackData *cb_data)
{
  ID *self_id = cb_data->self_id;
  ID *owner_id = cb_data->owner_id;
  ID **id_pointer = cb_data->id_pointer;
  /* Embedded IDs do not get tagged with #ID_TAG_UNDO_OLD_ID_REUSED_UNCHANGED currently (could be,
   * but would add extra processing, and by definition they always share that state with their
   * owner, as they are stored as 'regular data' in blend-files, not as independent IDs).
   *
   * NOTE: It seems that local IDs using embedded ones are never 'reused unchanged', this was
   * never caught before. However, if using `self_id` here, this assert gets triggered with
   * upcoming packed data. Probably because while packed data remains unchanged, it is handled like
   * regular local data by undo code, and like regular linked data. */
  BLI_assert((owner_id->tag & ID_TAG_UNDO_OLD_ID_REUSED_UNCHANGED) != 0);
  UNUSED_VARS_NDEBUG(owner_id);

  ID *id = *id_pointer;
  if (id != nullptr && !ID_IS_LINKED(id) && (id->tag & ID_TAG_UNDO_OLD_ID_REUSED_UNCHANGED) == 0) {
    bool do_stop_iter = true;
    if (self_id->id_type() == ID_OB) {
      Object *ob_self = id_cast<Object *>(self_id);
      if (ob_self->type == OB_ARMATURE) {
        if (ob_self->data == id) {
          BLI_assert(id->id_type() == ID_AR);
          if (ob_self->pose != nullptr) {
            /* We have a changed/re-read armature used by an unchanged armature object: our beloved
             * Bone pointers from the object's pose need their usual special treatment. */
            ob_self->pose->flag |= POSE_RECALC;
          }
        }
        else {
          /* Cannot stop iteration until we checked ob_self->data pointer... */
          do_stop_iter = false;
        }
      }
    }

    return do_stop_iter ? IDWALK_RET_STOP_ITER : IDWALK_RET_NOP;
  }

  return IDWALK_RET_NOP;
}


/* Moritz: `MORITZ_UNDO_TIMING=1` prints the time of each phase of an undo step (profiling). */
static double undo_timing_last = 0.0;
static void undo_timing(const char *phase)
{
  static const bool enabled = BLI_getenv("MORITZ_UNDO_TIMING") != nullptr;
  if (!enabled) {
    return;
  }
  const double now = BLI_time_now_seconds();
  if (phase != nullptr) {
    printf("MORITZ_UNDO %-28s %8.1f ms\n", phase, (now - undo_timing_last) * 1000.0);
  }
  undo_timing_last = now;
}

/* -------------------------------------------------------------------- */
/** \name Moritz: keep the depsgraph relations across undo
 *
 * Restoring the depsgraph after a memfile undo step rebuilds all its relations, which takes about
 * half a second with 10k objects, also when the step only moved an object. The rebuild is
 * skipped when the step provably changed no relation:
 * - the set of IDs is the same, and every ID was reused or re-read at its old address;
 * - every re-read ID is an object with the same relation fingerprint (parent, data, instancing,
 *   modifier types and the IDs they use) and none of the things whose relations are not
 *   fingerprinted (constraints, pose, particles, rigid body, animation data), or a scene with
 *   the same scene fingerprint (camera, world, master collection contents, view layers and
 *   their collections and bases; scenes with a set, rigid body world, sequencer strips or
 *   animation data always rebuild), or a collection with the same flags, objects and children.
 * A re-read scene gets a new master collection (embedded, so re-allocated): its depsgraph node is
 * re-keyed to the new pointer with #DEG_graph_id_replace_orig.
 * \{ */

static void relation_fingerprint_id_cb(void *user_data,
                                       Object * /*ob*/,
                                       ID **idpoin,
                                       LibraryForeachIDCallbackFlag /*cb_flag*/)
{
  std::string &text = *static_cast<std::string *>(user_data);
  text += fmt::format(" id:{}", fmt::ptr(*idpoin));
}

/** Empty means: relations not covered by the fingerprint, always rebuild. */
static std::string object_relation_fingerprint(Object *ob)
{
  /* Force field settings are allocated as soon as anything reads them; only an actual field
   * (fingerprinted below) has relations. */
  const char *excluded = ob->pose                                     ? "pose" :
                         ob->adt                                      ? "animation data" :
                         !BLI_listbase_is_empty(&ob->constraints)     ? "constraints" :
                         !BLI_listbase_is_empty(&ob->particlesystem)  ? "particles" :
                         (ob->rigidbody_object || ob->rigidbody_constraint) ? "rigid body" :
                         ob->soft                                     ? "soft body" :
                                                                        nullptr;
  if (excluded) {
    if (BLI_getenv("MORITZ_UNDO_TIMING")) {
      printf("MORITZ_UNDO   %s not fingerprinted: %s\n", ob->id.name, excluded);
    }
    return {};
  }
  std::string text = fmt::format("type:{} parent:{} partype:{} parsubstr:{} data:{} instance:{}",
                                 int(ob->type),
                                 fmt::ptr(ob->parent),
                                 int(ob->partype),
                                 ob->parsubstr,
                                 fmt::ptr(ob->data),
                                 fmt::ptr(ob->instance_collection));
  if (ob->pd) {
    text += fmt::format(" field:{}/{}", int(ob->pd->forcefield), int(ob->pd->shape));
  }
  for (const ModifierData &md : ob->modifiers) {
    text += fmt::format(" mod:{}/{}", int(md.type), int(md.mode));
  }
  BKE_modifiers_foreach_ID_link(ob, relation_fingerprint_id_cb, &text);
  return text;
}

static void collection_fingerprint(const Collection *collection, std::string &text)
{
  text += fmt::format(" coll:{}/{}", fmt::ptr(collection), int(collection->flag));

  for (const CollectionObject &cob : collection->gobject) {
    text += fmt::format(" ob:{}", fmt::ptr(cob.ob));
  }
  for (const CollectionChild &child : collection->children) {
    text += fmt::format(" child:{}", fmt::ptr(child.collection));
  }
}

static void layer_collection_fingerprint(const LayerCollection &layer_collection, std::string &text)
{
  text += fmt::format(" lc:{}/{}",
                      fmt::ptr(layer_collection.collection),
                      int(layer_collection.flag));
  for (const LayerCollection &child : layer_collection.layer_collections) {
    layer_collection_fingerprint(child, text);
  }
  text += " /lc";
}

/** Empty means: relations not covered by the fingerprint, always rebuild. The master collection
 * is listed by its contents only, its address changes when the scene is re-read. */
static std::string scene_relation_fingerprint(const Scene *scene)
{
  const char *excluded = scene->set              ? "set" :
                         scene->rigidbody_world  ? "rigid body world" :
                         (scene->ed && !BLI_listbase_is_empty(&scene->ed->seqbase)) ?
                                                   "sequencer strips" :
                         scene->adt              ? "animation data" :
                         !scene->master_collection ? "no master collection" :
                                                    nullptr;
  if (excluded) {
    if (BLI_getenv("MORITZ_UNDO_TIMING")) {
      printf("MORITZ_UNDO   %s not fingerprinted: %s\n", scene->id.name, excluded);
    }
    return {};
  }
  std::string text = fmt::format(
      "camera:{} world:{} master:{}",
      fmt::ptr(scene->camera),
      fmt::ptr(scene->world),
      int(scene->master_collection->flag));
  for (const CollectionObject &cob : scene->master_collection->gobject) {
    text += fmt::format(" ob:{}", fmt::ptr(cob.ob));
  }
  for (const CollectionChild &child : scene->master_collection->children) {
    text += fmt::format(" child:{}", fmt::ptr(child.collection));
  }
  for (const ViewLayer &view_layer : scene->view_layers) {
    text += fmt::format(" view_layer:{}/{}", view_layer.name, int(view_layer.flag));
    for (const LayerCollection &layer_collection : view_layer.layer_collections) {
      /* The top layer collection is the master collection's: by its children, not its address. */
      text += fmt::format(" top:{}", int(layer_collection.flag));
      for (const LayerCollection &child : layer_collection.layer_collections) {
        layer_collection_fingerprint(child, text);
      }
    }
    for (const Base &base : view_layer.object_bases) {
      text += fmt::format(" base:{}", fmt::ptr(base.object));
    }
  }
  return text;
}

struct RelationsSnapshot {
  int64_t id_count = 0;
  Map<const ID *, std::string> objects;
  Map<const ID *, std::string> scenes;
  Map<const ID *, std::string> collections;
  /** Each scene's master collection, to re-key the depsgraphs when the scene is re-read. */
  Map<const ID *, const ID *> master_collections;
};

static RelationsSnapshot relations_snapshot(Main *bmain)
{
  RelationsSnapshot snapshot;
  ID *id;
  FOREACH_MAIN_ID_BEGIN (bmain, id) {
    snapshot.id_count++;
    if (id->id_type() == ID_OB) {
      snapshot.objects.add(id, object_relation_fingerprint(id_cast<Object *>(id)));
    }
    else if (id->id_type() == ID_GR) {
      std::string text;
      collection_fingerprint(id_cast<Collection *>(id), text);
      snapshot.collections.add(id, text);
    }
    else if (id->id_type() == ID_SCE) {
      const Scene *scene = id_cast<Scene *>(id);
      snapshot.scenes.add(id, scene_relation_fingerprint(scene));
      if (scene->master_collection) {
        snapshot.master_collections.add(id, &scene->master_collection->id);
      }
    }
  }
  FOREACH_MAIN_ID_END;
  return snapshot;
}

static void relations_debug(const char *reason, const ID *id)
{
  static const bool enabled = BLI_getenv("MORITZ_UNDO_TIMING") != nullptr;
  if (enabled) {
    printf("MORITZ_UNDO relations rebuilt: %s %s (tag %x)\n", reason, id->name, unsigned(id->tag));
  }
}

static bool relations_unchanged(Main *bmain, const RelationsSnapshot &before)
{
  int64_t id_count = 0;
  bool unchanged = true;
  ID *id;
  FOREACH_MAIN_ID_BEGIN (bmain, id) {
    id_count++;
    if (!unchanged) {
      continue;
    }
    if (id->tag & (ID_TAG_UNDO_OLD_ID_REUSED_UNCHANGED | ID_TAG_UNDO_OLD_ID_REUSED_NOUNDO)) {
      continue;
    }
    if (!(id->tag & ID_TAG_UNDO_OLD_ID_REREAD_IN_PLACE) ||
        !ELEM(id->id_type(), ID_OB, ID_SCE, ID_GR))
    {
      unchanged = false;
      relations_debug("not reused", id);
      continue;
    }
    const std::string *old = nullptr;
    std::string now;
    switch (id->id_type()) {
      case ID_SCE:
        old = before.scenes.lookup_ptr(id);
        now = scene_relation_fingerprint(id_cast<Scene *>(id));
        break;
      case ID_GR:
        old = before.collections.lookup_ptr(id);
        collection_fingerprint(id_cast<Collection *>(id), now);
        break;
      default:
        old = before.objects.lookup_ptr(id);
        now = object_relation_fingerprint(id_cast<Object *>(id));
        break;
    }
    if (old == nullptr || old->empty() || *old != now) {
      unchanged = false;
      relations_debug("relations differ", id);
      if (old && BLI_getenv("MORITZ_UNDO_TIMING")) {
        printf("MORITZ_UNDO   before: %s\nMORITZ_UNDO   after:  %s\n", old->c_str(), now.c_str());
      }
    }
  }
  FOREACH_MAIN_ID_END;
  if (unchanged && id_count != before.id_count && BLI_getenv("MORITZ_UNDO_TIMING")) {
    printf("MORITZ_UNDO relations rebuilt: ID count %d -> %d\n", int(before.id_count), int(id_count));
  }
  return unchanged && id_count == before.id_count;
}

/** Re-key the depsgraph nodes of master collections re-allocated by re-reading their scene. */
static void relations_rekey_master_collections(Main *bmain, const RelationsSnapshot &before)
{
  for (Scene &scene : bmain->scenes) {
    const ID *old_master = before.master_collections.lookup_default(&scene.id, nullptr);
    if (old_master == nullptr || scene.master_collection == nullptr ||
        old_master == &scene.master_collection->id)
    {
      continue;
    }
    for (ViewLayer &view_layer : scene.view_layers) {
      if (Depsgraph *depsgraph = BKE_scene_get_depsgraph(&scene, &view_layer)) {
        DEG_graph_id_replace_orig(depsgraph, old_master, &scene.master_collection->id);
      }
    }
    DEG_id_tag_update_ex(bmain, &scene.master_collection->id, ID_RECALC_SYNC_TO_EVAL);
    if (BLI_getenv("MORITZ_UNDO_TIMING")) {
      printf("MORITZ_UNDO   %s master collection re-keyed\n", scene.id.name);
    }
  }
}

/** \} */

static void memfile_undosys_step_decode(
    bContext *C, Main *bmain, UndoStep *us_p, const eUndoStepDir undo_direction, bool /*is_final*/)
{
  BLI_assert(undo_direction != STEP_INVALID);

  bool use_old_bmain_data = true;

  if (USER_DEVELOPER_TOOL_TEST(&U, use_undo_legacy) || !(U.uiflag & USER_GLOBALUNDO)) {
    use_old_bmain_data = false;
  }
  else if (undo_direction == STEP_REDO) {
    /* The only time we should have to force a complete redo is when current step is tagged as a
     * redo barrier.
     * If previous step was not a memfile one should not matter here, current data in old bmain
     * should still always be valid for unchanged data-blocks. */
    if (us_p->use_old_bmain_data == false) {
      use_old_bmain_data = false;
    }
  }
  else if (undo_direction == STEP_UNDO) {
    /* Here we do not care whether current step is an undo barrier, since we are coming from
     * 'the future' we can still re-use old data. However, if *next* undo step
     * (i.e. the one immediately in the future, the one we are coming from)
     * is a barrier, then we have to force a complete undo.
     * Note that non-memfile undo steps **should** not be an issue anymore, since we handle
     * fine-grained update flags now.
     */
    UndoStep *us_next = us_p->next;
    if (us_next != nullptr) {
      if (us_next->use_old_bmain_data == false) {
        use_old_bmain_data = false;
      }
    }
  }

  /* Extract depsgraphs from current bmain (which may be freed during undo step reading),
   * and store them for re-use. */
  undo_timing(nullptr);
  GHash *depsgraphs = nullptr;
  RelationsSnapshot relations_before;
  if (use_old_bmain_data) {
    depsgraphs = BKE_scene_undo_depsgraphs_extract(bmain);
    relations_before = relations_snapshot(bmain);
  }
  undo_timing("depsgraphs extract");

  ED_editors_exit(bmain, false);
  undo_timing("editors exit");
  /* Ensure there's no preview job running. Unfinished previews will be scheduled for regeneration
   * via #PRV_TAG_RESTART_RENDERING in BKE_previewimg_blend_read. */
  ED_preview_kill_jobs_for_undo(CTX_wm_manager(C), bmain);
  const bool need_preview_render_restart = bmain->need_preview_render_restart;

  MemFileUndoStep *us = reinterpret_cast<MemFileUndoStep *>(us_p);
  BKE_memfile_undo_decode(us->data, undo_direction, use_old_bmain_data, C);
  undo_timing("memfile decode (read)");

  for (UndoStep *us_iter = us_p->next; us_iter; us_iter = us_iter->next) {
    if (BKE_UNDOSYS_TYPE_IS_MEMFILE_SKIP(us_iter->type)) {
      continue;
    }
    us_iter->is_applied = false;
  }
  for (UndoStep *us_iter = us_p; us_iter; us_iter = us_iter->prev) {
    if (BKE_UNDOSYS_TYPE_IS_MEMFILE_SKIP(us_iter->type)) {
      continue;
    }
    us_iter->is_applied = true;
  }

  /* bmain has been freed. */
  bmain = CTX_data_main(C);
  ED_editors_init_for_undo(bmain);
  undo_timing("editors init");

  /* Cancelled preview jobs set this on the old bmain, carry it over to
   * restart previews that were interrupted. */
  bmain->need_preview_render_restart |= need_preview_render_restart;

  if (use_old_bmain_data) {
    /* Restore previous depsgraphs into current bmain. */
    const bool keep_relations = relations_unchanged(bmain, relations_before);
    BKE_scene_undo_depsgraphs_restore(bmain, depsgraphs, !keep_relations);
    if (keep_relations) {
      relations_rekey_master_collections(bmain, relations_before);
      undo_timing("relations kept");
    }
    undo_timing("depsgraphs restore");

    /* We need to inform depsgraph about re-used old IDs that would be using newly read
     * data-blocks, at least evaluated copies need to be updated... */
    ID *id = nullptr;
    FOREACH_MAIN_ID_BEGIN (bmain, id) {
      if (id->tag & ID_TAG_UNDO_OLD_ID_REUSED_UNCHANGED) {
        BKE_library_foreach_ID_link(
            bmain, id, memfile_undosys_step_id_reused_cb, nullptr, IDWALK_READONLY);
      }

      if (id->id_type() == ID_SCE) {
        Scene *scene = reinterpret_cast<Scene *>(id);
        /* TODO: We should be able to restore these depsgraphs properly as part of
         * #BKE_scene_undo_depsgraphs_restore but this is currently only done for depsgraphs in the
         * scene.depsgraph_hash map. So the safest option is to just delete the following
         * depsgraphs for now. */
        if (bke::compositor::is_enabled(*scene, bke::compositor::ExecutionMode::Preview)) {
          /* Ensure undo calls from the UI update the interactive compositor preview depsgraph, see
           * #compo_initjob. */
          bke::CompositorRuntime &compositor_runtime = scene->runtime->compositor;
          DEG_graph_free(compositor_runtime.preview_depsgraph);
          compositor_runtime.preview_depsgraph = nullptr;
        }

        if (scene->runtime->sequencer.depsgraph) {
          /* Ensure that the depsgraph created in #get_depsgraph_for_scene_strip are updated. */
          bke::SequencerRuntime &seq_runtime = scene->runtime->sequencer;
          DEG_graph_free(seq_runtime.depsgraph);
          seq_runtime.depsgraph = nullptr;
        }
      }

      /* NOTE: Tagging `ID_RECALC_SYNC_TO_EVAL` here should not be needed in practice, since
       * modified IDs should already have other depsgraph update tags anyway.
       * However, for the sake of consistency, it's better to effectively use it,
       * since content of that ID pointer does have been modified. */
      uint recalc_flags = id->recalc | ((id->tag & ID_TAG_UNDO_OLD_ID_REREAD_IN_PLACE) ?
                                            ID_RECALC_SYNC_TO_EVAL :
                                            IDRecalcFlag(0));
      /* Tag depsgraph to update data-block for changes that happened between the
       * current and the target state, see direct_link_id_restore_recalc(). */
      if (recalc_flags != 0) {
        DEG_id_tag_update_ex(bmain, id, recalc_flags);
      }

      bNodeTree *nodetree = bke::node_tree_from_id(id);
      if (nodetree != nullptr) {
        recalc_flags = nodetree->id.recalc;
        if (id->tag & ID_TAG_UNDO_OLD_ID_REREAD_IN_PLACE) {
          recalc_flags |= ID_RECALC_SYNC_TO_EVAL;
        }
        if (recalc_flags != 0) {
          DEG_id_tag_update_ex(bmain, &nodetree->id, recalc_flags);
        }
      }
      if (id->id_type() == ID_SCE) {
        Scene *scene = id_cast<Scene *>(id);
        if (scene->master_collection != nullptr) {
          recalc_flags = scene->master_collection->id.recalc;
          if (id->tag & ID_TAG_UNDO_OLD_ID_REREAD_IN_PLACE) {
            recalc_flags |= ID_RECALC_SYNC_TO_EVAL;
          }
          if (recalc_flags != 0) {
            DEG_id_tag_update_ex(bmain, &scene->master_collection->id, recalc_flags);
          }
        }
      }
    }
    FOREACH_MAIN_ID_END;

    FOREACH_MAIN_ID_BEGIN (bmain, id) {
      /* Clear temporary tag. */
      id->tag &= ~(ID_TAG_UNDO_OLD_ID_REUSED_UNCHANGED | ID_TAG_UNDO_OLD_ID_REUSED_NOUNDO |
                   ID_TAG_UNDO_OLD_ID_REREAD_IN_PLACE);

      /* We only start accumulating from this point, any tags set up to here
       * are already part of the current undo state. This is done in a second
       * loop because DEG_id_tag_update may set tags on other datablocks. */
      id->recalc_after_undo_push = 0;
      bNodeTree *nodetree = bke::node_tree_from_id(id);
      if (nodetree != nullptr) {
        nodetree->id.recalc_after_undo_push = 0;
      }
      if (id->id_type() == ID_SCE) {
        Scene *scene = id_cast<Scene *>(id);
        if (scene->master_collection != nullptr) {
          scene->master_collection->id.recalc_after_undo_push = 0;
        }
      }
    }
    FOREACH_MAIN_ID_END;
    undo_timing("tag reused IDs");
  }

  WM_event_add_notifier(C, NC_SCENE | ND_LAYER_CONTENT, CTX_data_scene(C));
}

static void memfile_undosys_step_free(UndoStep *us_p)
{
  /* To avoid unnecessary slow down, free backwards
   * (so we don't need to merge when clearing all). */
  MemFileUndoStep *us = reinterpret_cast<MemFileUndoStep *>(us_p);
  if (us_p->next != nullptr) {
    UndoStep *us_next_p = BKE_undosys_step_same_type_next(us_p);
    if (us_next_p != nullptr) {
      MemFileUndoStep *us_next = reinterpret_cast<MemFileUndoStep *>(us_next_p);
      BLO_memfile_merge(&us->data->memfile, &us_next->data->memfile);
    }
  }

  BKE_memfile_undo_free(us->data);
}

void ED_memfile_undosys_type(UndoType *ut)
{
  ut->identifier = "GLOBAL_UNDO";
  ut->poll = memfile_undosys_poll;
  ut->step_encode = memfile_undosys_step_encode;
  ut->step_decode = memfile_undosys_step_decode;
  ut->step_free = memfile_undosys_step_free;

  ut->flags = 0;

  ut->step_size = sizeof(MemFileUndoStep);
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Utilities
 * \{ */
bool ED_undosys_autosave_compatible(UndoStack *ustack)
{
  if (!ustack->step_active) {
    return false;
  }

  return ELEM(ustack->step_active->type, BKE_UNDOSYS_TYPE_MEMFILE, BKE_UNDOSYS_TYPE_IMAGE);
}

void ED_undosys_stack_memfile_id_changed_tag(UndoStack *ustack, ID *id)
{
  UndoStep *us = ustack->step_active;
  if (id == nullptr || us == nullptr || us->type != BKE_UNDOSYS_TYPE_MEMFILE) {
    return;
  }

  MemFile *memfile = &(reinterpret_cast<MemFileUndoStep *>(us))->data->memfile;
  for (MemFileChunk &mem_chunk : memfile->chunks) {
    if (mem_chunk.id_session_uid == id->session_uid) {
      mem_chunk.is_identical_future = false;
      break;
    }
  }
}

/** \} */

}  // namespace blender
