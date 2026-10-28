# Core patches

Every change Moritz makes to Blender's own code, for rebasing onto upstream. Moritz is based on `blender-v5.3-release` at `4768a6eac54`. Each patch is marked with a `Moritz:` comment in the code.

## Own config folders

Moritz keeps its settings in `%APPDATA%\Moritz\<version>` so it never shares them with a Blender install.

- `intern/ghost/intern/GHOST_SystemPathsWin32.cc` — system and user dirs

- `intern/ghost/intern/GHOST_SystemPathsUnix.cc` — user settings in `~/.config/moritz/<version>` (system data stays in `share/blender`, matching the install layout)
- `intern/ghost/intern/GHOST_SystemPathsCocoa.mm` — `~/Library/Application Support/Moritz/<version>`

Linux and macOS are changed but not built or tested yet.

## Tabbed docking

Areas dock into each other as tabs, Adobe-style; dragging empty header space moves an area.

- `source/blender/editors/screen/area.cc` — tab strip drawing and hit testing
- `source/blender/editors/screen/screen_intern.hh` — tab declarations
- `source/blender/editors/screen/screen_ops.cc` — header drag and dock-as-tab in `screen.area_join`; `tab_space_type` for a dragged tab
- `source/blender/editors/interface/interface_handlers.cc` — dragging a tab button starts the header drag (`but_area_tab_drag`)
- Tab order: bits 3–7 of `SpaceLink.link_flag` (`ED_area_tab_order_get/set`); stock Blender ignores them
- Several tabs of one editor type: tabs are addressed by position (`tab` operator property), `SCREEN_OT_area_tab_duplicate`; stock Blender opening such a file shows the first space of each type
- `source/blender/makesdna/DNA_space_enums.h` — tab flags
- `source/blender/makesdna/DNA_userdef_types.h` — area drag grip (`USER_AREA_CORNER_HANDLE`) on by default
- `scripts/presets/keyconfig/keymap_data/blender_default.py`, `industry_compatible_data.py` — header drag key

## Branding

- `release/datafiles/splash.png` — Moritz splash, built by `moritz/branding/src/make_splash.py` from the white logo
- `release/windows/icons/winblender.ico` — app icon (lower-case Medula One "m"), built by `make_icon.py`
- `source/blender/blenkernel/BKE_moritz_version.h` (+ `CMakeLists.txt`) — Moritz version "0.1 Alpha"; Blender's version stays for files, add-ons and the config folder
- `source/blender/windowmanager/intern/wm_splash_screen.cc` — splash shows the Moritz version; About shows the Moritz logo and version
- `release/datafiles/moritz_logo.png` (+ `editors/datafiles/CMakeLists.txt`, `ED_datafiles.h`) — the white logo, embedded for About
- `scripts/startup/bl_operators/wm.py` — splash and About links: Moritz on GitHub first, Blender links named as Blender's
- `source/blender/windowmanager/intern/wm_window.cc` — window title "Moritz 0.1 Alpha"
- `release/datafiles/icons_svg/blender.svg` — the top-left menu icon, the m as a vector
- `scripts/startup/bl_ui/space_topbar.py` — the top-left menu is called "Moritz"; About is "About Moritz"; "Load Factory Moritz Settings"
- Other visible names: "Quit Moritz" (`wm_operators.cc`), window titles "Moritz Render" (`render_view.cc`), "Moritz Drivers Editor" and "Moritz Info Log" (`screen_ops.cc`), "Moritz File View" (`wm_event_system.cc`), "Load Factory Moritz Preferences" (`wm_files.cc`, `space_userpref.py`), restart and file-association labels (`space_userpref.py`)
- `release/text/readme.html` — Moritz section with the source link
- Programs `moritz.exe` and `moritz-launcher.exe`: `OUTPUT_NAME` in `source/creator/CMakeLists.txt` (targets keep their names), `moritz.pdb`, the launcher (`blender_launcher_win32.c`), and the places that look for the executable by name: `GHOST_SystemWin32.cc`, `GHOST_WindowWin32.cc`, `winstuff.cc`, `system_win32.cc`
- Logo in GenEi Kiwami Gothic, credit line in Medula One (both SIL OFL, `moritz/branding/src/fonts/`), built by `make_logo.py`

## Keymaps

- `scripts/presets/keyconfig/Max.py`, `Moritz.py` — the Max and Moritz keymaps; Maximize's operators are bound only while it is enabled
- `scripts/presets/keyconfig/keymap_data/moritz_max_data.py` — copy of Maximize's `keymap_max.py`, keep in sync
- `source/blender/blenkernel/intern/blendfile.cc` — the Moritz keymap is the factory default
- `scripts/startup/bl_operators/wm.py` — Quick Setup offers Blender / Max / Moritz as buttons
- `Max.py`, `Moritz.py` keymap preferences: Maya navigation, F frames selection, Blender modal keys
- Both shortcuts in the UI: menus show Blender's key in parentheses and tooltips add "Blender Shortcut" when the active keymap uses another key. `WM_keymap_lookup_blender_begin/end` (`WM_keymap.hh`, `wm_keymap.cc`) make shortcut look-ups use Blender's own keymap (the default key configuration, which is always loaded); `but_event_blender_string` and `button_string_get_blender_keymap` (`interface.cc`, `UI_interface_c.hh`), `interface_region_tooltip.cc`

## Modeling and scene

- Fractional inches: `USER_UNIT_OPT_FRACTIONS` (`DNA_scene_types.h`), `UnitSettings.use_fractions` (`rna_scene.cc`), display as feet and 1/16 inches and parsing of mixed numbers such as `4 1/2` (`unit.cc`), the option in Scene > Units (`properties_scene.py`)
- Freeze: objects with selection disabled draw in plain gray in Solid shading (`workbench_state.cc`, `workbench_engine.cc`, `workbench_private.hh`)
- `scripts/startup/bl_ui/space_view3d.py` — `VIEW3D_HT_header.select_mode_draw`: an add-on (Maximize) can replace the Edit Mode select-mode buttons with Max's five sub-object levels

## Pipeline

- `scripts/presets/operator/export_scene.fbx/To 3ds Max.py`, `import_scene.fbx/From 3ds Max.py` — FBX presets for 3ds Max (smoothing groups, units, no leaf bones)
- `moritz/docs/max_users.md` — where Max's features are in Moritz
- `release/extensions/system/io_scene_max/import_max.py` — the bundled .max importer (1.9.2), patched
  (`Moritz patch` comments): the asset paths stream `FileAssetMetaData` is found by name (with the
  Summary Information streams it isn't entry 11, so every lookup missed); a missed lookup returns
  `None` instead of the whole table (which made every Physical material lose all its maps); each
  Physical map is read on its own; maps keep their full path, so they load from where Max had them
  (still looked for next to the .max file otherwise); USD Preview Surface materials are read (base
  color, metallic, emissive, roughness, IOR and their OSL bitmap maps, plus a metallic map slot in
  the material builder); a node listed as its own parent is not parented

## Repository

- `.lfsconfig` — Git LFS objects come from upstream; the fork stores none of its own
- `.gitattributes` — files under `moritz/`, the Moritz splash, logo and app icon are plain git, not LFS
- `moritz/` — roadmap, tasks, research and this file

The Max workflow is not part of Moritz: it is the separate add-on [Maximize](https://github.com/cyberhirsch/maximize).

## Edit Poly modifier (core)

- `source/blender/makesdna/DNA_modifier_types.h` — `eModifierType_EditPoly = 200` (Moritz only)
- `source/blender/modifiers/intern/MOD_edit_poly.cc`, `MOD_edit_poly.hh`, `MOD_util.cc`, `MOD_modifiertypes.hh`, `CMakeLists.txt`
- `source/blender/makesrna/intern/rna_modifier.cc` — `EditPolyModifier`, enum item `EDIT_POLY`
- `source/blender/blenkernel/intern/modifier.cc` — revive an Edit Poly saved by stock Blender
- `scripts/startup/bl_ui/properties_data_modifier.py` — add-menu entry

## Edit Spline modifier (core)

- `source/blender/makesdna/DNA_modifier_types.h` — `eModifierType_EditSpline = 201` (Moritz only)
- `source/blender/modifiers/intern/MOD_edit_spline.cc`, `MOD_edit_spline.hh`, `MOD_util.cc`, `MOD_modifiertypes.hh`, `CMakeLists.txt`
- `source/blender/makesrna/intern/rna_modifier.cc` — `EditSplineModifier` (`store`, `steps`,
  `use_optimize`, `use_adaptive`), enum item `EDIT_SPLINE`
- `source/blender/blenkernel/intern/modifier.cc` — revive an Edit Spline saved by stock Blender
- `source/blender/blenkernel/intern/displist.cc` — Edit Spline gets the curves, as the nodes
  modifier, instead of forcing a mesh
- `source/blender/blenkernel/intern/object.cc` — Edit Spline on legacy curve objects only
- `scripts/startup/bl_ui/properties_data_modifier.py` — add-menu entry for curves
- Edit Mode session: `editors/curve/editcurve.cc` (edit-nurbs from the modifier's result, load
  back into it), `editors/object/object_edit.cc` (leaving ends the session),
  `blenkernel/intern/displist.cc` (skip the session modifier and those below it in Edit Mode),
  `blenkernel/intern/curve_legacy_convert.cc` + `BKE_curve_legacy_convert.hh`
  (`curves_to_curve_legacy_nurbs`), `editors/curve/CMakeLists.txt`

## Command Panel

The Properties editor is Max's Command Panel: a Create tab first, the Modifiers tab called Modify,
with Max's modifier stack on top.

- `makesrna/intern/rna_space.cc` — editor and tab labels ("Command Panel", "Modify", "Create")
- `makesdna/DNA_space_enums.h` — `BCONTEXT_CREATE`; stock Blender falls back to the Object tab
- `editors/space_buttons/buttons_context.cc`, `space_buttons.cc` — the Create tab, listed with or
  without an object, before the first redraw
- `scripts/startup/bl_ui/properties_create.py` — Max's categories; Blender's primitives without
  Maximize, Maximize's parametric ones with it
- `scripts/startup/bl_ui/properties_data_modifier.py` — the stack (newest first, base object row,
  sub-object levels of Edit Poly and Edit Spline, level icon, instanced and warning marks, button
  row, right-click menu through `UI_MT_list_item_context_menu`); selecting a modifier keeps only
  its panel open; the flat Add Modifier menu (`OBJECT_MT_modifier_add_flat`)
- `scripts/startup/bl_operators/moritz_modifier_stack.py` — Copy / Paste, Paste Instanced (links in
  the object's `mx_modifier_links` custom property, kept in sync by a depsgraph handler), Make
  Unique, Off in Viewport / Renderer, Delete / X in the Modify tab
- Tests: `moritz/tests/test_command_panel.py`, `test_modifier_stack.py`

## Outliner (Max's Scene Explorer)

- `makesdna/DNA_space_types.h`, `DNA_space_enums.h` — `SpaceOutliner.mx_filter` (Shapes filter)
  and `mx_columns` (Display as Box column), taken from padding; stock Blender ignores them
- `makesrna/intern/rna_space.cc` — `use_filter_object_shapes`,
  `show_restrict_column_display_box`; the select and render columns are named Freeze and
  Renderable
- `editors/space_outliner/outliner_tree.cc` — shapes (curve and text objects) are their own type;
  "Others" no longer covers them
- `editors/space_outliner/outliner_draw.cc`, `outliner_utils.cc` — the Freeze column shows Max's
  snowflake (bright when frozen); the Display as Box column (`display_type` Bounds / Textured,
  Shift for children)
- `scripts/startup/bl_ui/space_outliner.py` — the new toggles in the filter popover
- See-Through: `DNA_object_types.h` (`OB_DRAW_SEE_THROUGH` in `Object.dtx`), `rna_object.cc`
  (`Object.show_see_through`), `draw/engines/workbench/workbench_engine.cc` (30 % alpha in Solid
  shading), the Outliner column (`SO_MX_COLUMN_SEE_THROUGH`), `properties_object.py`

## Undo speed

- `source/blender/editors/undo/memfile_undo.cc` — keep the depsgraph relations when an undo step
  changed none; `MORITZ_UNDO_TIMING=1` prints the phases of each step
- `source/blender/editors/undo/ed_undo.cc` — phase timing
- `source/blender/blenkernel/intern/scene.cc`, `BKE_scene.hh` — `update_relations` parameter of
  `BKE_scene_undo_depsgraphs_restore`
