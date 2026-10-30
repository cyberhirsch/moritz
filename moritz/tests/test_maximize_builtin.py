# Run: moritz.exe --factory-startup -b --python moritz/tests/test_maximize_builtin.py
# Maximize is a built-in part of Moritz (Seb, 2026-10-30): on from the start, also with factory
# settings, the user cannot disable it, it is not in Preferences > Add-ons, and its settings are
# in Moritz's own Preferences sections.
import addon_utils
import bpy

failures = []


def check(name, ok, *info):
    print("MXBI", "OK" if ok else "FAIL", name, *info, flush=True)
    if not ok:
        failures.append(name)


check("Maximize is installed", addon_utils.is_builtin("maximize"))
check("on from the start", addon_utils.check("maximize")[1] and "maximize" in bpy.context.preferences.addons)
check("other add-ons are not built in", not addon_utils.is_builtin("io_scene_fbx"))

addon_utils.disable("maximize", default_set=True)
check("the user cannot disable it", addon_utils.check("maximize")[1] and
      "maximize" in bpy.context.preferences.addons)
check("its operators are there", hasattr(bpy.ops.maximize, "chamfer") and bpy.ops.maximize.chamfer.poll is not None)


class Layout:
    """A stand-in for UILayout that records the properties drawn."""

    def __init__(self, drawn):
        self.drawn = drawn
        self.use_property_split = self.use_property_decorate = self.active = self.enabled = True

    def prop(self, data, name, **_kw):
        self.drawn.append(name)

    def __getattr__(self, _name):
        return lambda *a, **k: Layout(self.drawn)


def drawn_by(panel_name):
    drawn = []
    panel = getattr(bpy.types, panel_name)
    panel.draw_centered(None, bpy.context, Layout(drawn))
    return drawn


prefs = bpy.context.preferences.addons["maximize"].preferences
editors = drawn_by("USERPREF_PT_interface_editors")
viewport = drawn_by("USERPREF_PT_viewport_display")
check("editing settings in Interface > Editors",
      {"tool_settings_style", "use_hover_highlight", "use_startup_layout"} <= set(editors), editors)
check("cage colors in Viewport > Display", {"cage_color", "cage_selected_color"} <= set(viewport), viewport)
keymap_props = [p.identifier for p in prefs.bl_rna.properties]
check("every setting has a place", all(
    name in editors + viewport + ["name_scheme", "first_run_done", "moritz_keymap_done", "rna_type", "bl_idname"]
    for name in keymap_props), keymap_props)

# The Add-ons list: the module loop skips built-in parts (both list implementations).
import inspect  # noqa: E402
from bl_ui import space_userpref  # noqa: E402
src = inspect.getsource(space_userpref.USERPREF_PT_addons)
check("legacy Add-ons list skips it", "addon_utils.is_builtin(addon_module_name)" in src)
try:
    from bl_pkg import bl_extension_ui
    check("Add-ons list skips it", "addon_utils.is_builtin(module_name)" in
          inspect.getsource(bl_extension_ui.addons_panel_draw_items))
except ImportError:
    check("Add-ons list skips it", False, "bl_pkg not importable")

print("MXBI FAILURES", len(failures), failures)
