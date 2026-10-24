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

## Repository

- `.lfsconfig` — Git LFS objects come from upstream; the fork stores none of its own
- `.gitattributes` — files under `moritz/` (logos and other branding) are plain git, not LFS
- `moritz/` — roadmap, tasks, research and this file

The Max workflow is not part of Moritz: it is the separate add-on [Maximize](https://github.com/cyberhirsch/maximize).
