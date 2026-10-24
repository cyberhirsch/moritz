# Moritz Tasks

Working list for [ROADMAP.md](ROADMAP.md). Paths are relative to `blender/`.
Status: `[ ]` open · `[~]` in progress · `[x]` done.

## Phase 0 — Foundation

### Repository
- [x] Clone Blender source (`blender-v5.3-release` @ `4768a6eac54`, 5.3 beta)
- [x] `git fetch --unshallow` (full history is needed for upstream merges and bisecting)
- [x] Create the Moritz repository (github.com/cyberhirsch/moritz, private); `origin` = Moritz, `upstream` = projects.blender.org/blender/blender
- [x] Branch model: `moritz/main` on top of upstream; one topic branch per core patch
- [x] `.lfsconfig` points Git LFS at upstream, so the fork stores no LFS objects of its own
- [x] `PATCHES.md`: list every core change with files touched, for rebasing

### Build
- [x] Install Visual Studio 2022 Build Tools, CMake and Git LFS
- [x] `make update` (fetches precompiled libs into `lib/`)
- [x] First build: `make.bat release`; gentle rebuilds run through `build_gentle.cmd` (low priority, 2 jobs)
- [ ] Debug build plus a VS solution for core work (`make.bat full nobuild 2022`)
- [ ] CI: Windows build on push (GitHub Actions or self-hosted)

### Rebrand
- [x] Window title and Moritz version 0.1 Alpha (`BKE_moritz_version.h`, alongside the Blender version)
- [x] Splash: `release/datafiles/splash.png`, Moritz links in the splash menu
- [x] App icon: `release/windows/icons/winblender.ico`
- [x] `.blend` file icon (`winblenderfile.ico`) and the top-left menu icon (`icons_svg/blender.svg`)
- [x] Separate config directory on Windows (`%APPDATA%\Moritz\<version>`, `%PROGRAMDATA%\Moritz\<version>`): `intern/ghost/intern/GHOST_SystemPathsWin32.cc`
- [x] Same for Linux and macOS (`GHOST_SystemPathsUnix.cc`, `GHOST_SystemPathsCocoa.mm`); not built or tested there yet
- [x] About dialog: Moritz logo and version, "Based on Blender"
- [x] Executable name `moritz.exe` and `moritz-launcher.exe`
- [ ] Check that no Blender logo or trademark text is left in the UI

### Legal
- [x] Keep `COPYING` and the license headers; add a Moritz `README.md` with a source link
- [ ] A source link in every release package

## Basics — Adobe-style docking (core)

- [x] Header grip on by default (`USER_AREA_CORNER_HANDLE` in `DNA_userdef_types.h`)
- [x] Drag empty header space to move/dock an area: `header_drag` mode of `SCREEN_OT_area_join` (`screen_ops.cc`), bound to LMB click-drag in the "Region Context Menu" keymap (`blender_default.py`, `industry_compatible_data.py`)
- [x] Tabbed areas: `SPACE_FLAG_TAB` (`DNA_space_enums.h`); tab strip next to the editor-type menu (`ED_area_header_switchbutton`, `area.cc`); `SCREEN_OT_area_tab_activate`, `SCREEN_OT_area_tab_close` (header context menu)
- [x] Center drop stacks as a tab instead of replacing the target; a header drag of a tabbed area moves only the active tab (edge drop, own-area split, tear-out to a new window)
- [x] Fix: releasing a header drag left of the window opened the corner menu instead of tearing out
- [x] Tested with simulated events (`--enable-event-simulate`): center drop, tab switch, edge drop, re-stack, tear-out, no self-split
- [ ] Check by hand with a real mouse and a multi-monitor setup
- [ ] Drag a tab button itself to tear it off (narrow areas have no empty header space)
- [ ] Tab order by insertion, not by editor type; close button on tabs
- [ ] More than one tab of the same editor type (an area stores one space per type)

## Phase 1 — Feels like Max (`maximize` add-on)

Separate repository: [github.com/cyberhirsch/maximize](https://github.com/cyberhirsch/maximize) (private). Moritz does not depend on it: the add-on writes its Max and Moritz keymap presets into the user's `presets/keyconfig` while enabled and switches to the Moritz keymap on first enable.

- [x] Add-on skeleton
- [x] **Max keymap** (`keymap_max.py`): Industry Compatible plus Max 2026 keys (views T/B/F/L/P/U/C, Z / Ctrl+Alt+Z / Ctrl+Shift+Z zoom extents, Alt+W, Alt+Q, Alt+X, F3/F4, G, 7, S/A snaps, H, Alt+A, F12, Insert, M, F9/F10/Shift+Q, K/N, `/` `,` `.` Home/End, Ctrl+Y redo, `;` repeat, Ctrl+V clone, Ctrl+C camera from view, 1–6 sub-object levels, Edit Poly keys); Ctrl+click adds and Alt+click removes from the selection; default keymap
- [x] Keymap switch: Preferences > Add-ons > Maximize, Max menu > Keymap, sidebar > Max > Keymap; the splash screen lists "Max" with the other keymap presets
- [x] **Quad menu** (`quad_menu.py`): right-click pie with Display, Viewport, Tools / Edit Poly and Transform quadrants, per mode
- [x] **Viewport navigation**: MMB pan, Alt+MMB orbit, Ctrl+Alt+MMB zoom; orbit around the selection and zoom about the mouse are set on first enable
- [x] **Max layout for new files** (`viewport.py`, load_post handler): quad view, centimeters, sidebar on the Max tab (preference "Max Layout for New Files"). Done in the add-on instead of an app template.
- [x] **Max English** (`vocabulary.py`): about 40 Blender labels renamed (Merge by Distance → Weld, Bevel → Chamfer, Join → Attach…), preference "Max English", default on
- [x] **Max-named operators** (`vocabulary.py`): 35 aliases (Weld, Target Weld, Swift Loop, Cap, Bridge, Detach, TurboSmooth, Shell…) in the header **Max** menu, so F3 menu search finds them
- [x] **Transform Type-In** (F12): Move, Rotate and Scale; absolute and offset in world space; objects and Edit Poly
- [x] **Pivot tools**: Affect Pivot Only (Insert), Center to Object, Align to World, Reset XForm
- [x] **Align** (Alt+A): pick the target in the viewport; min, center, pivot or max per axis; orientation; match scale
- [x] **Array dialog**: incremental or total move, rotate and scale; 1D, 2D and 3D; copy, instance or reference
- [x] **Spacing tool**: by count or spacing along the active curve, with Follow
- [x] **Select by Name** (H): filterable list dialog
- [x] **Named selection sets**: object level (scene data) and sub-object level (`nss_<name>` mesh attributes)
- [x] **Editable primitives** (`primitives.py`): Box, Sphere, Cylinder, Cone, Tube, Torus and Plane as Geometry Nodes groups (`MX <name>`); parameters in sidebar > Max > Modify; Max names (Box001); collapse with Convert to Editable Poly, or automatically when you press 1–5
- [x] **UVW Map modifier** (`uvw_map.py`): Planar, Box, Cylindrical and Spherical through a cube-empty gizmo, U/V tiling, real-world size, UV channel name
- [x] Clone: Ctrl+V dialog (Copy / Instance / Reference, number of copies); Shift+drag clones, moves and then asks
- [x] Background tests with the built Moritz: keymap, primitives, UVW Map, Array, Spacing, Align, Clone, Type-In, Reset XForm, sub-object levels, selection sets
- [x] UI test in the rebuilt Moritz with simulated events (`--factory-startup --enable-event-simulate`): splash offers the Max keymap, Max keymap active, add-on enabled, quad view + centimeters + sidebar Max tab on new files, quad menu, F12 Type-In, Z zoom extents, H Select by Name, Create and Modify panels with primitive and UVW Map parameters
- [x] Shift+drag on a move, rotate or scale gizmo handle clones, then the gizmo drags the clones (`maximize.clone_gizmo` in the "Generic Gizmo (Maybe) Drag" keymaps); extra copies repeat the whole transform
- [x] Interactive drag creation of primitives, as in Max: drag the base or radius, then move for height or second radius, click to confirm; stays in create mode until right-click; works on the ground plane in perspective and on the view plane in axis views
- [x] UVs for Tube and Torus (seam-aware, shared helper `GroupBuilder.seam_angle`)
- [x] Reference clones are one-way: they share the original's mesh, and modifiers added to them stay on them. Instances share the mesh too; sharing the whole modifier stack is Phase 4 ("Instance vs Reference")
- [x] Existing preferences: Moritz now keeps its own settings in `%APPDATA%\Moritz\<version>` (`GHOST_SystemPathsWin32.cc`), so its first start uses the Moritz defaults (Maximize on, Max keymap) and never reads or changes a Blender install's settings. No versioning is needed.
- [x] Second UI test with simulated events: drag-create a box (base drag + height), Shift+drag on the move gizmo → Clone Options dialog → clone, config folder is `Moritz\5.3`
- [ ] Hand test of the whole add-on with a real mouse (Seb)

### Shortcuts ([docs/shortcut_plan.md](https://github.com/cyberhirsch/maximize/blob/main/docs/shortcut_plan.md))
- [x] Coverage check `tools/check_max_keymap.py` (Maximize repo) → [docs/shortcut_coverage.md](https://github.com/cyberhirsch/maximize/blob/main/docs/shortcut_coverage.md): 99 of 216 Max keys OK
- [ ] Fix the 4 conflicts and bind the 33 unbound keys
- [ ] Selection presets Max / Moritz (default) / Blender, as specified in the plan
- [ ] Restore free Blender keys (numpad views)
- [ ] Preferences: Maya navigation, F frames selection, Blender modal keys
- [ ] Editors: Graph Editor / Dope Sheet, shader editor, Outliner F2
- [ ] Moritz column in the comparison page; assert keys in the background test

## Phase 2 — The stack (core)

- [ ] **Spike:** read the modifier evaluation path (`source/blender/blenkernel/intern/mesh_data_update.cc`, `modifier.cc`, `source/blender/modifiers/intern/MOD_*.cc`, `source/blender/makesdna/DNA_modifier_types.h`, `source/blender/makesrna/intern/rna_modifier.cc`) and write the design note
- [ ] **Spike:** prototype edit storage: store edits as an operation log versus a delta mesh with ID mapping; choose one
- [ ] `eModifierType_EditPoly` in DNA and RNA; `MOD_edit_poly.cc`
- [ ] Tab into the modifier: Edit Mode works on the evaluated mesh from the stack below and writes deltas back
- [ ] Topology tracking: map edits to stable element IDs; rebase by position when tracking fails
- [ ] Stack UI: Max-style list with "Show end result" and collapse-to-here
- [ ] Collapse To / Collapse All operators
- [ ] Opening in stock Blender: unknown modifier → bake on save (`Edit Poly` → mesh), or a documented fallback
- [ ] Unwrap UVW modifier built on the same edit storage
- [ ] Sub-object gizmos for Simple Deform (Bend, Taper, Twist) and Lattice/FFD
- [ ] Tests in `tests/` for evaluation, undo and file round trips
- [ ] Header: Max's five sub-object levels (Vertex, Edge, Border, Polygon, Element) in place of Blender's three select-mode buttons, with Border and Element as real select modes. Not possible in the add-on: Blender's C header draws the three buttons. Icons exist in `maximize/icons`

## Phase 3 — Splines

- [ ] Audit the curve code (`source/blender/blenkernel/intern/curves*`, `source/blender/editors/curves/`) and decide: legacy Curve object versus new Curves
- [ ] Editable Spline tools: Fillet, Chamfer, Outline, Trim/Extend, Weld, Refine, Break, Connect
- [ ] 2D shape booleans (union, subtract, intersect)
- [ ] Vertex types: Corner, Smooth, Bezier, Bezier Corner
- [ ] Shape modifiers: Extrude, Lathe, Sweep, Loft, Renderable Spline
- [ ] Line tool with snapping and AutoGrid

## Phase 4 — Scene and data (core)

- [ ] **Freeze**: object flag in DNA, greyed drawing in the overlay engine (`source/blender/draw/`), unselectable
- [ ] **Scene Explorer** editor: new space type (`source/blender/editors/space_*`); layers, Freeze, Hide, Display as Box, See-Through columns
- [ ] **Instance vs Reference**: a shared modifier stack across objects; Make Unique
- [ ] **Smoothing groups**: face attribute in the core, Shading panel UI, normal computation, FBX import/export (`source/blender/io/fbx/`)
- [ ] **Imperial fractions**: unit display and parsing (`source/blender/blenkernel/intern/unit.cc`)
- [ ] **Performance**: profile a 10k-object archviz scene (Outliner, undo, selection); fix the top three hotspots

## Phase 5 — Pipeline and release

- [ ] Bundle the `.max` importer (Import Autodesk MAX extension), checking its license
- [ ] V-Ray/Corona → Cycles material converter
- [ ] FBX presets: "From/To 3ds Max" (cm/mm, Z-up, smoothing groups)
- [ ] Windows installer and portable zip
- [ ] Docs: "Moritz for Max users" cheat sheet (Max term → Moritz location)
- [ ] 1.0 release

## Upstream maintenance (recurring)
- [ ] Merge each Blender release branch into `moritz/main`
- [ ] Re-run the test suite and a smoke test of the Phase 1 add-on after each merge
