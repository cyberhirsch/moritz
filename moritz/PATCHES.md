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

## Repository

- `.lfsconfig` — Git LFS objects come from upstream; the fork stores none of its own
- `.gitattributes` — files under `moritz/`, the Moritz splash, logo and app icon are plain git, not LFS
- `moritz/` — roadmap, tasks, research and this file

The Max workflow is not part of Moritz: it is the separate add-on [Maximize](https://github.com/cyberhirsch/maximize).
