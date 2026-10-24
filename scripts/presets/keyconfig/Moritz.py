# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

# Moritz: the Moritz keymap. Max 2026 keys on top of the Industry Compatible keymap, with Blender's selection ideas where Max has nothing comparable.
# Keys for the Maximize add-on's tools (quad menu, clone, align, sub-object levels...) are only
# bound while it is enabled; the add-on reloads this keymap when it is enabled or disabled.

import os
import bpy

DIRNAME, FILENAME = os.path.split(__file__)
IDNAME = os.path.splitext(FILENAME)[0]


def update_fn(_self, _context):
    load()


industry_compatible = bpy.utils.execfile(os.path.join(DIRNAME, "keymap_data", "industry_compatible_data.py"))
moritz_max = bpy.utils.execfile(os.path.join(DIRNAME, "keymap_data", "moritz_max_data.py"))


def _available(idname, props):
    """True when an operator, menu or panel exists (Maximize's ones only while it is enabled)."""
    module, _, name = idname.partition(".")
    if module == "maximize" and not hasattr(bpy.types, "MAXIMIZE_OT_" + name):
        return False
    target = props.get("name", "")
    return not (isinstance(target, str) and target.startswith("MAXIMIZE_") and not hasattr(bpy.types, target))


def load():
    from sys import platform
    from bl_keymap_utils.io import keyconfig_init_from_data

    prefs = bpy.context.preferences

    kc = bpy.context.window_manager.keyconfigs.new(IDNAME)
    params = industry_compatible.Params(use_mouse_emulate_3_button=prefs.inputs.use_mouse_emulate_3_button)
    keyconfig_data = moritz_max.generate_keymaps(industry_compatible, params, moritz=True, available=_available)

    if platform == "darwin":
        from bl_keymap_utils.platform_helpers import keyconfig_data_oskey_from_ctrl_for_macos
        keyconfig_data = keyconfig_data_oskey_from_ctrl_for_macos(keyconfig_data)

    keyconfig_init_from_data(kc, keyconfig_data)


if __name__ == "__main__":
    load()
