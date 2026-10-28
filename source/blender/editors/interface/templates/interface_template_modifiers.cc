/* SPDX-FileCopyrightText: 2024 Blender Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup edinterface
 *
 * Template for building the panel layout for the active object's modifiers.
 */

#include "BKE_context.hh"
#include "BKE_modifier.hh"
#include "BKE_screen.hh"

#include "BLI_listbase.hh"
#include "BLI_string.hh"
#include "BLI_vector.hh"

#include "ED_object.hh"

#include "RNA_access.hh"
#include "RNA_prototypes.hh"

#include "UI_interface.hh"
#include "UI_interface_layout.hh"

namespace blender::ui {

static void modifier_panel_id(void *md_link, char *r_name)
{
  ModifierData *md = static_cast<ModifierData *>(md_link);
  BKE_modifier_type_panel_id(md->type, r_name);
}

/* Moritz: whether the instanced panels are those of `shown`, in order. Like
 * #panel_list_matches_data, for a subset of the modifiers. */
static bool panels_match_modifiers(ARegion *region, const Span<ModifierData *> shown)
{
  int i = 0;
  for (Panel &panel : region->panels) {
    if (panel.type == nullptr || !(panel.type->flag & PANEL_TYPE_INSTANCED)) {
      continue;
    }
    if ((panel.flag & PNL_INSTANCED_LIST_ORDER_CHANGED) || i >= shown.size()) {
      return false;
    }
    char panel_idname[MAX_NAME];
    modifier_panel_id(shown[i], panel_idname);
    if (!STREQ(panel_idname, panel.type->idname)) {
      return false;
    }
    i++;
  }
  return i == shown.size();
}

void template_modifiers(Layout * /*layout*/, bContext *C, const bool only_active, const char *exclude)
{
  ARegion *region = CTX_wm_region(C);

  Object *ob = ed::object::context_active_object(C);
  ListBaseT<ModifierData> *modifiers = &ob->modifiers;

  /* Moritz: `only_active` shows one modifier's settings at a time, as Max does. */
  Vector<ModifierData *> shown;
  for (ModifierData &md : *modifiers) {
    const ModifierTypeInfo *mti = BKE_modifier_get_info(md.type);
    if (mti->panel_register == nullptr) {
      continue;
    }
    if (only_active && !(md.flag & eModifierFlag_Active)) {
      continue;
    }
    /* Moritz: a modifier shown another way (a parametric base's own settings). */
    if (exclude && exclude[0] && STREQ(md.name, exclude)) {
      continue;
    }
    shown.append(&md);
  }

  const bool panels_match = panels_match_modifiers(region, shown);

  if (!panels_match) {
    panels_free_instanced(C, region);
    for (ModifierData *md : shown) {
      char panel_idname[MAX_NAME];
      modifier_panel_id(md, panel_idname);

      /* Create custom data RNA pointer. */
      PointerRNA *md_ptr = MEM_new<PointerRNA>(__func__);
      *md_ptr = RNA_pointer_create_id_subdata(ob->id, RNA_Modifier, md);

      panel_add_instanced(C, region, &region->panels, panel_idname, md_ptr);
    }
  }
  else {
    /* Assuming there's only one group of instanced panels, update the custom data pointers. */
    Panel *panel = region->panels.first();
    for (ModifierData *md_p : shown) {
      ModifierData &md = *md_p;

      /* Move to the next instanced panel corresponding to the next modifier. */
      while ((panel->type == nullptr) || !(panel->type->flag & PANEL_TYPE_INSTANCED)) {
        panel = panel->next;
        BLI_assert(panel !=
                   nullptr); /* There shouldn't be fewer panels than modifiers with UIs. */
      }

      PointerRNA *md_ptr = MEM_new<PointerRNA>(__func__);
      *md_ptr = RNA_pointer_create_id_subdata(ob->id, RNA_Modifier, &md);
      panel_custom_data_set(panel, md_ptr);

      panel = panel->next;
    }
  }
}

}  // namespace blender::ui
