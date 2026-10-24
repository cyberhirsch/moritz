# Core patches

Every change Moritz makes to Blender's own code, for rebasing onto upstream. Moritz is based on `blender-v5.3-release` at `4768a6eac54`. Each patch is marked with a `Moritz:` comment in the code.

## Own config folders (Windows)

Moritz keeps its settings in `%APPDATA%\Moritz\<version>` so it never shares them with a Blender install.

- `intern/ghost/intern/GHOST_SystemPathsWin32.cc` — system and user dirs

Still open: `GHOST_SystemPathsUnix.cc`, `GHOST_SystemPathsCocoa.mm`.

## Tabbed docking

Areas dock into each other as tabs, Adobe-style; dragging empty header space moves an area.

- `source/blender/editors/screen/area.cc` — tab strip drawing and hit testing
- `source/blender/editors/screen/screen_intern.hh` — tab declarations
- `source/blender/editors/screen/screen_ops.cc` — header drag and dock-as-tab in `screen.area_join`
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
- `source/blender/windowmanager/intern/wm_window.cc` — window title "Moritz 0.1 Alpha (Blender 5.3.0 Beta)"
- Logo in GenEi Kiwami Gothic, credit line in Medula One (both SIL OFL, `moritz/branding/src/fonts/`), built by `make_logo.py`

## Repository

- `.lfsconfig` — Git LFS objects come from upstream; the fork stores none of its own
- `.gitattributes` — files under `moritz/`, the Moritz splash, logo and app icon are plain git, not LFS
- `moritz/` — roadmap, tasks, research and this file

The Max workflow is not part of Moritz: it is the separate add-on [Maximize](https://github.com/cyberhirsch/maximize).
