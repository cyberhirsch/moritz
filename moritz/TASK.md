# Moritz Tasks

Working list for [ROADMAP.md](ROADMAP.md). Paths are relative to `blender/`.
Status: `[ ]` open · `[~]` in progress · `[x]` done.

## Decisions (Seb, 2026-10-25)

- **First release is Moritz 0.2** (not 1.0), on the Blender 5.3 base.
- **CI:** a self-hosted GitHub runner on Seb's PC, but no build runs without his permission
  (manual dispatch only, no build on push). Ask before installing the runner service.
- **Scene undo:** the faster full-scene undo comes as a preference, off by default.
- **Border / Element:** they stay in Maximize; no core selection modes.
- **Installer:** per user (no admin rights), keeping the first-start setup.
- **Edit Poly on instances:** as in Max, shared. Adding or editing it on one instance applies to all
  (the add-on keeps the modifiers in sync; files stay plain Blender data).
- **Repos stay private.**
- **Phase 3b:** do every item in order, then report.

- *(2026-10-29)* **Moritz is a Blender alternative, not Blender plus an add-on.** Seb: "moritz
  should not feel like a blender alternative that ships with an addon. it should just feel like a
  blender alternative." In Moritz there is **no "Max" sidebar tab**; it stays only in Maximize on
  stock Blender. Its contents move to native places in Moritz (proposal):
  - Modifier Stack (Edit Poly, Collapse To / All): into the Modify tab's stack.
  - Hierarchy (Affect Pivot Only, Center to Object, Align to World, Reset XForm): ~~a Hierarchy
    tab~~ no tab, see the Utilities decision below.
  - Utilities (Transform Type-In, Align, Array, Spacing Tool, Clone, UVW Map, Select by Name): a
    **Utilities** tab, as in Max, or the menus they belong in (Object, Edit), with the keys.
    **Decided (Seb, 2026-10-29): a new Command Panel tab "Utilities"** holds **Align** (with a
    "pivot only" option), **Array**, **Spacing Tool** and **Object Paint**, combined. The rest
    goes to the menus or to Blender's own command (see the comparison below).
    - **Object Paint** (new; from Seb's screenshot of Max 2026's Object Paint tab), Max's
      features:
      - Paint Objects: a list of objects to paint with (pick, edit list), Fill # (place N along
        the last stroke).
      - Paint On: Grid / Surface / Selection (like Freeform's Draw On) and Offset.
      - Brush Settings: Commit / Cancel; Align to the surface normal with axis X / Y / Z and flip;
        Spacing; scatter U / V / W; rotation X / Y / Z; scale X / Y / Z in %, with a uniform lock.
      - Blender has no built-in object painter (only Geometry Nodes scattering), so this is our
        own tool. Reuse the Draw On code from `freeform.py`.
    - Align's pivot-only option: align only the object's pivot (origin), not the object.
    - **No Hierarchy tab for now (Seb, 2026-10-29).** Affect Pivot Only and Reset XForm sit in the
      **quad menu**. **Align to World, Center to Object and Affect Pivot Only** also go into
      **Align** in the Utilities tab.
    - Tab: teal like Create and Modify. *Core: a new `BCONTEXT`, **rebuild**; files fine.*
  - Named Selection Sets: the main toolbar / header, as in Max, or the Outliner.
  - Keymap switch: Preferences and the Quick Setup only.
  - Also check other places where the add-on shows ("Maximize" or "Max" in labels, the add-on
    list, menus): in Moritz they read as built-in. Possibly ship Maximize's code as part of Moritz
    instead of as an enabled add-on.
  - *Core: new Command Panel tabs (like Create) and their order mean a **rebuild**; files are
    fine (stock Blender falls back to the Object tab, as with Create).*
  - *(2026-10-29)* Which Max-tab tools Blender already does better: Center to Object (Set
    Origin), Reset XForm (Apply), Transform Type-In (sidebar, typed values), Clone (Shift+D /
    Alt+D). About equal: Affect Pivot Only (Affect Only Origins, needs a visible button), Select by
    Name (Outliner filter), Collapse All (Convert to Mesh). Max better, keep as tools: Align,
    Spacing Tool, UVW Map, Named Selection Sets, Collapse To, Array (separate objects).
  - **Transform Type-In (Seb, 2026-10-29):** always visible at the **bottom left** while a
    transform tool (Move, Rotate, Scale) is active, like Max's X / Y / Z fields in the status
    bar. Includes **relative** (Max's Offset mode, an Absolute / Offset toggle). No dialog, no
    sidebar needed. Possible places: Blender's status bar (Python-drawable, so no rebuild) or a
    viewport overlay. Watch out: Blender's Adjust Last Operation panel also sits bottom left in
    the viewport. F12 stays as the shortcut that puts the cursor into the fields.
  - **Reset XForm (Seb, 2026-10-29): keep Blender's Apply**; no own Reset XForm tool. In the
    **quad menu** the entry is named "Reset XForm" and runs Blender's Apply (All Transforms).

## UX rules (Seb)

- *(2026-10-29)* **Modal tools and brushes never block the UI.** While a tool or brush runs (for
  example the Conform brush), clicks on buttons and other UI still work. The click does what the
  button does, and may end the tool if that button calls for it (another tool, another mode, a
  sub-object level). Right-click ends the tool. Clicking elsewhere can end it too, depending on
  where: in the viewport the click belongs to the tool; in panels, the Outliner or menus it goes to
  the UI. Like Max. Applies to all Moritz and Maximize tools. First case: the Conform brush.

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
- [x] VS solution: `build_windows_Full_x64_vc17_Release/Blender.sln` (Debug, Release, RelWithDebInfo); `build_gentle.cmd Debug` and `build_when_idle.ps1 -Config Debug` build the Debug config at low priority into `bin/Debug`
- [x] CI: Windows build workflow, started by hand (`.github/workflows/moritz-windows.yml`): build, Moritz and Maximize tests, portable zip, on a hosted or self-hosted runner
- [x] *(Seb, 2026-10-26: manual dispatch only, never on push)* Self-hosted runner on the workstation: `D:/actions-runner-moritz` (runner 2.338.2, labels `self-hosted, windows, moritz`; not a service: `start_runner.cmd` starts it at low priority, a queued run waits for it). The workflow's self-hosted path clones Maximize from `G:/Code/Maximize`, builds against the local libraries through `LIBDIR` and keeps its build folder on D: for incremental runs. First run not done yet (needs Seb's go)

### Rebrand
- [x] Window title and Moritz version 0.1 Alpha (`BKE_moritz_version.h`, alongside the Blender version)
- [x] Splash: `release/datafiles/splash.png`, Moritz links in the splash menu
- [x] App icon: `release/windows/icons/winblender.ico`
- [x] `.blend` file icon (`winblenderfile.ico`) and the top-left menu icon (`icons_svg/blender.svg`)
- [x] Separate config directory on Windows (`%APPDATA%\Moritz\<version>`, `%PROGRAMDATA%\Moritz\<version>`): `intern/ghost/intern/GHOST_SystemPathsWin32.cc`
- [x] Same for Linux and macOS (`GHOST_SystemPathsUnix.cc`, `GHOST_SystemPathsCocoa.mm`); not built or tested there yet
- [x] About dialog: Moritz logo and version, "Based on Blender"
- [x] Executable name `moritz.exe` and `moritz-launcher.exe`
- [x] Check that no Blender logo or trademark text is left in the UI (menu, quit, window titles, factory settings; Blender's own links stay named as Blender's)

### Legal
- [x] Keep `COPYING` and the license headers; add a Moritz `README.md` with a source link
- [x] A source link in every release package (`release/text/readme.html`)

### Docking (Adobe-style, core)

- [x] Header grip on by default (`USER_AREA_CORNER_HANDLE` in `DNA_userdef_types.h`)
- [x] Drag empty header space to move/dock an area: `header_drag` mode of `SCREEN_OT_area_join` (`screen_ops.cc`), bound to LMB click-drag in the "Region Context Menu" keymap (`blender_default.py`, `industry_compatible_data.py`)
- [x] Tabbed areas: `SPACE_FLAG_TAB` (`DNA_space_enums.h`); tab strip next to the editor-type menu (`ED_area_header_switchbutton`, `area.cc`); `SCREEN_OT_area_tab_activate`, `SCREEN_OT_area_tab_close` (header context menu)
- [x] Center drop stacks as a tab instead of replacing the target; a header drag of a tabbed area moves only the active tab (edge drop, own-area split, tear-out to a new window)
- [x] Fix: releasing a header drag left of the window opened the corner menu instead of tearing out
- [x] Tested with simulated events (`--enable-event-simulate`): center drop, tab switch, edge drop, re-stack, tear-out, no self-split
- [ ] Check by hand with a real mouse and a multi-monitor setup
- [x] Drag a tab button itself to move, dock or tear it off (`but_area_tab_drag` in `interface_handlers.cc`, `tab_space_type` of `SCREEN_OT_area_join`)
- [x] Tab order by insertion, not by editor type (kept in free bits of `SpaceLink.link_flag`, no file format change); close button on each tab, closing activates the neighbor
- [x] More than one tab of the same editor type: tabs are addressed by position (`tab` property of the tab operators and `screen.area_join`, `ED_area_tab_activate` swaps regions directly); Duplicate as Tab in the header context menu (`SCREEN_OT_area_tab_duplicate`); `moritz/tests/test_tabs_multi.py`

## Phase 1 — Feels like Max (Maximize + Moritz keymaps)

Separate repository: [github.com/cyberhirsch/maximize](https://github.com/cyberhirsch/maximize) (private). Moritz does not depend on it: Moritz ships its own Blender / Max / Moritz keymap presets, and the add-on adds its operators (quad menu, Max tools, 1–6) while enabled. In stock Blender the add-on writes the presets into the user's `presets/keyconfig` itself.

- [x] Add-on skeleton
- [x] **Max keymap** (`keymap_max.py`): Industry Compatible plus Max 2026 keys (views T/B/F/L/P/U/C, Z / Ctrl+Alt+Z / Ctrl+Shift+Z zoom extents, Alt+W, Alt+Q, Alt+X, F3/F4, G, 7, S/A snaps, H, Alt+A, F12, Insert, M, F9/F10/Shift+Q, K/N, `/` `,` `.` Home/End, Ctrl+Y redo, `;` repeat, Ctrl+V clone, Ctrl+C camera from view, 1–6 sub-object levels, Edit Poly keys); Ctrl+click adds and Alt+click removes from the selection; default keymap
- [x] Keymap switch: Preferences > Add-ons > Maximize, Max menu > Keymap, sidebar > Max > Keymap; the splash screen lists "Max" with the other keymap presets
- [x] **Quad menu** (`quad_menu.py`): right-click pie with Display, Viewport, Tools / Edit Poly and Transform quadrants, per mode
- [x] **Viewport navigation**: MMB pan, Alt+MMB orbit, Ctrl+Alt+MMB zoom; orbit around the selection and zoom about the mouse are set on first enable
- [x] **Max layout for new files** (`viewport.py`, load_post handler): quad view, centimeters, sidebar on the Max tab (preference "Max Layout for New Files"). Done in the add-on instead of an app template.
- [x] **Max English** (`vocabulary.py`): about 40 Blender labels renamed (Merge by Distance → Weld, Bevel → Chamfer, Join → Attach…), preference "Max English", default on
- [x] *(done 2026-10-29, Maximize `vocabulary.py`: preference Names = Follow Keymap / Blender / Max /
  Moritz, also in the Quick Setup and the Keymap preferences; needs the interface translation on,
  which the scheme switches on. Modifier names: see Phase 6)* *(Seb, 2026-10-29: "we have keyboard shortcut schemes, can we have name schemes too?" →
  "good idea")* **Name schemes**, like the keymap presets, replacing the "Max English" switch:
  - **Blender:** Blender's names, unchanged.
  - **Max:** Max's names wherever Max has one.
  - **Moritz:** Max's names, with Blender's name in the tooltip so tutorials and F3 search still
    work. This matches the two shortcuts shown in menus.
  - Chosen in the Quick Setup and in Preferences next to the keymap; by default it follows the
    chosen keymap.
  - Still a translation (`bpy.app.translations`), so files and the Python API are unchanged and
    stock Blender is unaffected.
  - Check whether it needs Blender's interface-translation setting switched on.
  - The Max table needs to grow well beyond today's ~40 labels.
  - In Moritz it reads as built-in, not as an add-on option (see Decisions).
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
- [x] Fix the 4 conflicts and bind the 33 unbound keys: 136 of 216 Max keys OK, 0 conflicts, 0 unbound (the other 80 need features Moritz does not have yet)
- [x] Keymap presets Blender / Max / Moritz in Moritz itself (`presets/keyconfig/Max.py`, `Moritz.py`, data copied from Maximize); chosen in the Quick Setup on first start; Moritz is the default. Maximize's keys (quad menu, tools, 1–6) are bound only while the add-on is enabled
- [x] Moritz selection behavior from the plan: Ctrl+click toggle, double-click loop/children, Ctrl+Alt+double-click ring, Ctrl+Shift+click shortest path, window/crossing by drag direction (`region_select.py`), Q cycling region shapes, hover highlight (`hover.py`), visible-only sub-objects with Alt+Shift+X to select through
- [x] Restore free Blender keys (numpad views)
- [x] *(done 2026-10-29, Maximize 92afaa8, Moritz cc59f46f5ee: plain middle mouse stripped from the
  "3D View Tool:" keymaps; app test: all six tool/keymap cases pan)* *(Seb, 2026-10-29: "when a transform tool is selected, the middle mouse button no longer
  controls the viewport")* **Bug: middle mouse stops panning with a tool active.** Cause:
  Industry Compatible (the base of the Max and Moritz keymaps) copies every non-select tool's
  left-drag to middle mouse, Maya-style (`industry_compatible_data.py` around line 3907, loop
  over the "Tool:" keymaps; also `transform.translate` on MIDDLEMOUSE CLICK_DRAG around line
  1010). Those tool keymaps win over `view3d.move` on MIDDLEMOUSE. Max always pans with the
  middle mouse, so the **Max and Moritz keymaps drop these middle-mouse copies**. It's a Python
  keymap change, so no rebuild. Update `keymap_max.py`, the core copy `moritz_max_data.py`, and
  the coverage check.
- [x] *(done 2026-10-29: Tab toggles Edit Mode in Object Non-modal; Space is `maximize.space_key` in
  Frames: maximizes over a 3D View, plays elsewhere, stops playback; Max's Selection Lock stays on
  its Max key)* *(Seb, 2026-10-29)* **Moritz keymap only** (not the Max one):
  - **Tab** still toggles Object / Edit Mode, in addition to the number keys 1–6.
  - **Space** maximizes the viewport, in addition to Alt+W.
  - Check what Space does now in the Moritz keymap and what it loses (in Max: Selection Lock
    Toggle; Blender's own Space binding). Freeform's modal tools also use Space to finish, and that
    stays inside the tool.
- [x] Both shortcuts in menus and tooltips (Max key and Blender key), so Blender tutorials stay usable (core: `WM_keymap_lookup_blender_begin`)
- [x] Preferences: Maya navigation, F frames selection, Blender modal keys (Preferences > Keymap, under the Max and Moritz keymaps)
- [x] Editors: Graph Editor / Dope Sheet, shader editor, Outliner F2
- [x] Moritz column in the comparison page; assert keys in the background test (`test_keymap_options.py`); 146 of 216 Max keys, 0 conflicts. Also Shift+Z/Y view undo, Alt+` Show End Result, F5–F8 axis constraints

### Hold / Fetch (Seb asked, 2026-10-28) — add-on work (Maximize), files unaffected
*Done 2026-10-28 (Maximize `hold.py`). Needed one small core option after all: Save As copy with
`recovery=True` stores the open file's path in the copy, as autosave does, and Fetch loads it through
Recover Auto Save. The held copy is an ordinary .blend.*
- [x] **Hold** (Ctrl+H, Max's key; today it hides the selection, and Alt+H already hides): save a
  copy of the scene to Moritz's temp folder; the open file and its path stay as they are
- [x] **Fetch** (Ctrl+Alt+F): ask "Restore the held scene?", then load the copy. It must keep the
  current file's path and name, so Ctrl+S still saves to the user's file, not to the temp copy. Also
  in Edit > Hold / Fetch.
- Blender today: undo history, File > Revert, Auto Save; no deliberate snapshot

### Cameras (Seb, 2026-10-25) — all add-on work (Maximize), files unaffected
- [x] *(2026-10-26, Maximize `cameras.py`; V in Object Mode, Edit Mode keeps Blender's V; also View > Cameras)* **Point-of-view menu** (Max's "[Camera001]" / "[Top]" label menu), also on V over a viewport. Entries: the scene's cameras (look through), Perspective, Orthographic, Top/Bottom/Front/Back/Left/Right, and:
  - [x] **Select Camera**: selects the camera you are looking through (in Blender today: click the camera frame's edge, or the Outliner)
  - [x] **Lock Camera to View**, on by default (new files with the Max layout): pan, orbit and zoom in a camera view move the camera instead of leaving camera view (Blender's sidebar > View > View Lock > Camera to View)
  - [x] **Lock Camera**: the camera can't be moved by accident (location, rotation and scale locks; Blender's camera-to-view sync already respects them)
- Suggestions, not decided yet:
  - [x] *(2026-10-26: Field of View drag and Roll in the Point-of-View menu; with Lock Camera to View, orbit / pan / zoom are Max's Orbit / Truck / Dolly. button strip at the bottom right (Dolly, Field of View, Pan, Orbit, Roll) and Dolly Camera / Target / Both in the menu, Maximize 7d85898)* Camera navigation tools in camera view: Dolly (camera / target / both), Truck, Orbit, Pan Camera, Roll, Field of View, Perspective; button strip at the bottom right
  - [x] *(2026-10-26)* Target camera: drag from camera position to target; target is an empty with a Track To constraint
  - [x] *(2026-10-26, Camera Correction)* Vertical tilt correction (2-point perspective) through lens shift
  - [x] *(2026-10-26, new files)* Max's 45° default viewport field of view (lens 43.5 mm); larger far clip for cm archviz scenes
  - Kept from Blender: Walk/Fly navigation, camera properties, the 3D view's own orbit/pan/zoom

## Phase 2 — Edit Poly in the stack

Rule: only what Max does better. Blender's modifier panel stays (no Max-style stack list); Blender's UV editor stays (no Unwrap UVW modifier).

### 2a — Prototype in Maximize (add-on) — done (`edit_poly.py`, `tests/test_edit_poly.py`)
- [x] "Edit Poly" Geometry Nodes modifier: stores the base mesh it was made from and the edited mesh; applies the edit as per-element offsets while the input topology is unchanged (Max's index-based behavior); warns when the topology below changes
- [x] Edit with 1–5: a stand-in object takes the place of the object while you edit; 6 or Tab comes back
- [x] Collapse To / Collapse All
- [x] Opening in stock Blender works unchanged (it is only Geometry Nodes)
- [x] Background tests: edits kept, follow the stack below, extruded vertices follow, topology warning, re-base, collapse
- [ ] Hand test of the workflow (Seb) before the core version

### 2b — Core (once the workflow is right)
- [x] **Spike:** read the modifier evaluation path (`blenkernel/intern/mesh_data_update.cc`, `modifier.cc`, `modifiers/intern/MOD_*.cc`, `DNA_modifier_types.h`, `rna_modifier.cc`) and write the design note (`moritz/docs/edit_poly_core_design.md`)
- [x] `eModifierType_EditPoly` (200) and `EditPolyModifier` RNA with `store(input, edited)`, `edit_mode`, `result`; `MOD_edit_poly.cc` with Deform (offsets) and Topology (stored mesh + `mx_orig`) modes, topology fingerprint and warnings; add-menu entry
- [x] Maximize drives the native modifier in Moritz (stand-in editing, then `store()`; GN prototype stays for stock Blender)
- [x] Edit Mode directly on the modifier's result, no stand-in object (core session: `session_begin`, enter/evaluate/load/exit branches; `moritz/tests/test_edit_poly_session.py`)
- [x] Speed on heavy meshes: one stack evaluation to begin (`session_begin(input)` applies the stored edit in core); entering and leaving a level on 393k vertices takes as long as Tab (about 230 / 75 ms; `Maximize/tests/bench_edit_poly.py`)
- [x] Opening in stock Blender: the modifier is a plain `ModifierData` with its data in `system_properties`, so stock keeps it (disabled), keeps the modifiers above and saves the data back; Moritz revives it (`BKE_modifier_blend_read_data`). Tested through stock 5.2 (`moritz/tests/test_edit_poly_native.py`)
- [x] Header: Max's five sub-object levels (Vertex, Edge, Border, Polygon, Element) in place of Blender's three select-mode buttons, through the `VIEW3D_HT_header.select_mode_draw` hook that Maximize fills
- [x] ~~Border and Element as real select modes in the core~~ (Seb's decision 2026-10-25: they stay in Maximize)
- [x] Sub-object levels 1–6 without the add-on: core `object.subobject_level` (`bl_operators/moritz_subobject.py`), bound by the Max keymap while Maximize is off; Border and Element act as Edge and Polygon there (`moritz/tests/test_subobject_core.py`)
- [x] Tests for evaluation and file round trips (`moritz/tests/test_edit_poly_native.py`, incl. stock Blender); undo in Edit Mode follows with the edit session

### Edit Poly Modify panel by priority (Seb's screenshots of Max's Edit Poly, all five levels, 2026-10-25)

Max's rollouts: Edit Poly Mode, Selection, Soft Selection, Edit (Vertices / Edges / Borders /
Polygons / Elements, per level), Edit Geometry, Paint Deformation, and at Polygon / Element level
Material IDs and Smoothing Groups. Order the Modify tab's Edit Poly rollouts and their buttons by
this list (most used first); rare controls go into closed sub-panels. The small box next to a
button opens its settings caddy (Max's "Settings"), so each of those tools needs a redo panel.
Max's caddy (Seb's Weld Vertices screenshot): a small panel at the selection in the viewport with
the tool's values (live preview), a result line ("Before: 97, After: 97"), and three buttons: OK,
Apply and Continue (apply, then run the tool again on the result), Cancel. Blender's Adjust Last
Operation panel covers the live values but sits in the corner and has no Apply and Continue
(today: Shift+R) and no Cancel (today: Ctrl+Z).
- [x] *(Seb, 2026-10-26: both, selectable in Preferences > Tool Settings; Maximize `caddy.py`, default Blender's panel)* Decide: Max-style caddy (an add-on popup at the mouse with OK / Apply and Continue / Cancel)
  or Blender's Adjust Last Operation panel. Caddy mode: a settings button next to each Edit Poly tool runs it with its last values and opens the caddy (live values, Before / After vertex count); hand test pending
1. Daily:
   - Selection: the five levels, Grow / Shrink, Ring / Loop, Backface culling (Ignore Backfacing)
   - Polygons: Extrude, Inset, Bevel, Bridge, Outline, Flip
   - Edges: Chamfer, Connect, Remove, Extrude, Bridge, Split
   - Vertices: Remove, Weld, Target Weld, Chamfer, Connect, Break
   - Borders: Cap, Bridge, Extrude
   - Edit Geometry: Repeat Last, Attach, Detach, Collapse, Cut, QuickSlice, Hide Selected / Unhide
     All / Hide Unselected
   - Material IDs: Set ID, Select ID; Smoothing Groups: the 32 groups, Auto Smooth
2. Weekly:
   - Edit Geometry: Slice Plane (Split, Slice, Reset Plane), Make Planar and X / Y / Z, Relax,
     MSmooth, Tessellate, Constraints (None / Edge / Face / Normal), Preserve UVs, Named Selections
     Copy / Paste, Delete Isolated Vertices
   - Polygons: Hinge From Edge, Extrude Along Spline, Insert Vertex
   - Edges: Create Shape, Insert Vertex, Weld, Target Weld, Edge Properties (Crease, Weight, Hard /
     Smooth), Turn
   - Vertices: Extrude, Remove Isolated Vertices
   - Borders: Chamfer, Connect, Create Shape, Insert Vertex
   - Selection: By Angle, Soft Selection (Use, Falloff, Pinch, Bubble, Edge Distance, Affect
     Backfacing)
   - Smoothing Groups: Select By SG, Clear All; Material IDs: select by name, Clear Selection
3. Rare:
   - Edit Poly Mode: Model / Animate, Commit, Settings, Cancel, Show Cage (with its two colors)
   - Selection: Use Stack Selection, Get Stack Selection, By Vertex, Occluded culling, Preview
     Selection (Off / SubObj / Multi)
   - Soft Selection: Shaded Face Toggle, Lock Soft Selection, Paint Soft Selection (Paint, Blur,
     Revert, Selection Value, Brush Size, Brush Strength, Brush Options)
   - Paint Deformation: Push/Pull, Relax, Revert, Push/Pull Direction (Original / Deformed Normals,
     Transform axis X / Y / Z), Push/Pull Value, Brush Size, Brush Strength, Brush Options, Commit /
     Cancel
   - Edit Geometry: Create, View Align, Grid Align
   - Edges: Edge Properties Depth, Display Hard Edges (with color), Edit Tri.
   - Vertices: Remove Unused Map Verts, vertex Weight / Crease
   - Polygons / Elements: Edit Triangulation, Retriangulate, Turn
- [x] Checked against Maximize's code (2026-10-25). Built as Max tools: levels, Grow / Shrink /
  Loop / Ring, Ignore Backfacing, Extrude, Inset, Bevel, Bridge, Flip, Chamfer (edge and vertex),
  Connect, Remove, Weld, Target Weld, Cap, Repeat Last, Attach, Detach, Collapse, Cut, QuickSlice,
  Swift Loop, Hide / Unhide, Make Planar, Relax, Tessellate, Soft Selection toggle, smoothing groups
  (Auto Smooth, Select By SG, Clear All), hover preview.
- [x] **Fix Cap** (Seb, 2026-10-25; done, `maximize.cap` modes QUAD / NGON / INSET): `maximize.cap` runs Blender's Fill (`mesh.fill`), which fills
  the border with triangles. New behavior (Seb's choice; Max itself makes a single polygon):
  - **Click: quad cap** by default, a quad grid (Grid Fill, `mesh.fill_grid`); with an odd number
    of border edges the grid gets one triangle to make it fit
  - **Ctrl+click: n-gon**, one polygon (Make Edge/Face, `mesh.edge_face_add`), as Max does
  - **Shift+click: quad cap + inset**: first an inset ring along the border, then the quad grid
    inside it, so the cap's edge flow stays clean
  - The same three variants for the Cap key and the quad menu entry; the redo panel can switch
    between them
- [x] Max buttons for Blender tools (Maximize, tests/test_poly_tools.py), in per-level Edit
  rollouts (Edit Vertices / Edges / Borders / Polygons / Elements): edge Split, vertex Break,
  Material IDs (Set ID, Select ID with Clear Selection), Preserve UVs, Hard / Smooth, Turn, Remove
  Isolated Vertices, Create, Display Hard Edges; also built: Select By Angle, Make Planar X / Y / Z,
  Create Shape
- [x] Still without a Max button: Material IDs select by name, Slice Plane, Insert Vertex, edge
  Crease / Weight, vertex Crease (done, `poly_tools.py`)
- [x] Built (Seb, 2026-10-25; `poly_tools.py`, tests `test_poly_tools*.py`): Max-style edge /
  border / vertex Extrude (Height and Width), Extrude Along Spline, Slice Plane's Split and Reset
  Plane, Named Selections Copy / Paste, Material ID Clear Selection, Show Cage (on / off), Hinge
  From Edge
- [x] *(2026-10-26, Maximize c48608c)* Show Cage's two colors (preferences, and next to Show
  Cage), a live Slice Plane (move and rotate gizmos; Slice, Split, Reset Plane), Apply and Continue
  (the + next to each Edit rollout's title runs the last tool again)
- Omitted (Seb agreed, 2026-10-25), because Blender does it as well or it is Max-only:
  - Edit Poly Mode (Model / Animate, Commit, Settings, Cancel): rare; Blender has shape keys
  - Paint Deformation: Blender's Sculpt Mode is better (at most a button that switches to it)
  - Soft Selection extras (Paint, Blur, Revert, Lock, Shaded Face Toggle): Blender's proportional
    editing covers the daily part
  - Use / Get Stack Selection, By Vertex, Preview Selection Multi: rare
  - Remove Unused Map Verts: Blender's UVs are per corner, no orphan map vertices
  - Edit Triangulation, Retriangulate, edge Depth: Blender's Triangulate and Rotate Edge (Turn keeps
    its Max name)
  - View Align, Grid Align: rare; scale to 0 on an axis
  - MSmooth: Blender's Subdivision Surface / smooth subdivide
  - Constraints Edge / Face / Normal: map Edge to vertex / edge slide (G G) and Normal to Shrink /
    Fatten (Alt+S), no rebuild
  - Delete Isolated Vertices option: deleting faces already removes loose vertices
  - Full Max caddies: Blender's Adjust Last Operation panel plus Apply and Continue instead
### Edit Poly: Max's Modeling ribbon (Seb, 2026-10-28)

Decision (Seb, 2026-10-28): no ribbon. Conform / retopology features go into the new Retopo
modifier (below); **everything else from the ribbon goes into the Edit Poly modifier**, in its
sections: selection tools (Modify Selection, the Selection tab's picks) in Selection; Loops tools
in a Loops section at Edge level; the per-level tools in Edit Vertices / Edges / Borders /
Polygons; Geometry (All), Align, Subdivision, Triangulation and Properties in Edit Geometry and
the Polygon sections. Rare ones in closed sub-panels, ordered by the priority list above.

What the ribbon (Graphite Modeling Tools) offers beyond the Edit Poly panel, against Blender.
Panel list from Autodesk's 2012-2016 help plus newer tools from memory; check against the 2026
ribbon (Seb's screenshots) before building.
- [x] *(done 2026-10-28, Maximize: Selection gets Dot Loop / Dot Ring, Similar, Fill, Outline and a
  closed "Select By" (NonQuads, Open, Random, Symmetry); a Loops section at Edge level (Insert Loop,
  Remove Loop); Edit Geometry gets closed "Geometry (All)" (Quadrify All / Selection, Symmetrize) and
  "Subdivision" (MeshSmooth, Tessellate); Smoothing Groups moved into Edit Poly at Polygon level
  with Smooth / Smooth 30 / Hard. Already there: Cap, Swift Loop, Hard / Smooth edges, Outline,
  Hinge, Extrude on Spline (Edit Polygons). Left: By Normal, Freeform's to Retopo)*
  Blender has it in some form, needs a Max button / name: Quadrify All / Selection (Tris to
  Quads), Symmetry Tools (Symmetrize), Similar, Outline selection (Select Boundary Loop), Dot Loop
  / Dot Ring (Checker Deselect), Fill selection (shortest path fill), NURMS (Subdivision Surface),
  Cap Poly (Fill), Insert Loop (Loop Cut), Remove Loop (Dissolve Edge Loop), Hard / Smooth / Smooth
  30 (Shade Auto Smooth), Selection tab's NonQuads (Faces by Sides), Open (Non Manifold), Random,
  Symmetry (Select Mirror), By Normal; Freeform's Draw On (face snapping) and Step Build (Poly
  Build); Distribute and Loop Tools (Center, Space, Curve, Circle, Straighten) are in the free
  LoopTools extension, not in Blender itself
- [x] **Smart Extrude** *(done 2026-10-28, Maximize `smart_extrude.py`, first in Edit Polygons: drag
  along the normal (Ctrl: steps; Distance in the redo panel). Out into free space a plain extrude;
  inward a cut with the exact boolean (pocket, notch, hole through); out into other geometry a
  union. One undo step. Shift+drag of polygons with the Move or Transform tool (also on the gizmo)
  runs it: a real Move of a preview extrusion (gizmo axis, X / Y / Z, snapping), then Smart Extrude
  along that move, one undo step; other tools keep Shift+drag. Merges with flush walls weld the
  boolean's slivers and drop its flat edges, leaving clean quads (2026-10-28))*
- [x] **Set Flow** *(done 2026-10-28, Maximize `poly_tools.py`, Edge level > Loops: the selected edges'
  vertices go onto a curve through the two vertices on each side across the loop; Amount, Auto
  Loop. Skips poles and vertices without a clear crossing loop)*
- [x] **The rest of Edit Poly** *(done 2026-10-28, Maximize `poly_ribbon.py`, test
  `test_poly_ribbon.py`)*: Grow / Shrink Loop and Ring one step, Random Loops, Loop / Ring click
  modes (a click picks the whole loop or ring), Build End (two quads become three, the loops end;
  pick the two vertices, entry first), Build Corner (turn edges inside their quads), Distribute,
  LoopTools' Center / Straighten / Circle / Curve as our own (with Auto Loop), GeoPoly, Generate
  Topology (Quads, Diamonds, Fan, Triangles, Inset), To View / To Grid, Previous / Next Modifier,
  Paint Connect (Blender's Knife), Selection tab Top / Bottom / Left / Right, Half, By Perspective,
  By View, Pivot Distance, By Numeric. Outline, Hinge, Extrude Along Spline, Make Planar X / Y / Z
  and Auto Loop were already there. Viewport tools started from a panel button (Cut, Paint Connect,
  the view-based selections) use the active viewport: the one whose view changed last. Not done:
  Max's Paint Connect auto-midpoints (the Knife needs Ctrl)
- [x] **Freeform modifier** *(Seb, 2026-10-28: "we already have retopo modifiers, let's make one
  called Freeform"; Maximize `freeform.py`, test `test_freeform.py`)*: a Geometry Nodes modifier
  named "Freeform" keeps the mesh on a Draw On surface (Surface object, Offset, Conform strength);
  stock Blender evaluates it. Its panel holds Max's PolyDraw: Drag (Move with surface snapping),
  Step Build / Extend / Optimize (Blender's Poly Build), Conform (put the selection onto the
  surface now), Strips, Surface, Shapes, Topology (lines across each other become quads), Branches
  (extrude the selection along a stroke, Branch Taper), Splines (new spline objects), Min Distance,
  Solve Surface with its Angle, New Object (an empty Freeform mesh on the selected object), and the
  Retopology overlay under Display. Not done: Max's Optimize brush (Poly Build's Shift+click
  instead), drawing that snaps onto existing borders beyond welding nearby vertices, Paint Deform
  (Sculpt modifier). Automatic retopology stays Blender's Remesh / QuadriFlow.
- [x] *(done 2026-10-29, Maximize 4685a44)* *(Seb, 2026-10-29: "conform brush works nicely")* **Conform brush: choose the normal.** A
  setting in the Conform brush options for the direction vertices move along: the **target's**
  normal (the Draw On surface) or the **active object's** own normal (the mesh being conformed).
  Also follow the new UX rule (see UX rules): clicks on buttons work while the brush runs.
  *(Built by the main session: `conform_direction`, Target / Active Object, in `freeform.py`.)*
  *(Seb, 2026-10-29: add **Nearest** and **View** too.)* Four choices for every Conform brush:
  Target (along the surface's normal), Active Object (along the mesh's own normals), Nearest
  (straight to the closest point on the surface), View (along the view direction, as if
  projected from the camera). Today's Target description also says "to the nearest point":
  split the two cleanly. *(Seb: show it as a **dropdown**, not a row of buttons.)*
  *Built as a dropdown with the four: Target uses **one shared direction**, the surface normal
  under the brush (for Conform All: nearest the selection's middle), because "along the
  surface's normal" per vertex is mathematically the same as Nearest. Active Object = vertex
  normals, Nearest = closest point, View = view direction.*
- [x] *(done 2026-10-29, Maximize 85d694d)* *(Seb, 2026-10-29: "where are the other conform brushes?")* **The other Conform brushes are
  missing.** Only the Conform brush and the one-shot Conform exist (`freeform.py`). Max's Freeform
  tab has four more next to Conform: Conform Move, Conform Rotate, Conform Scale, and a fourth
  (drawn as Conform Relax in the icon set; check its exact name and job in Max 2026). They move,
  rotate or scale the vertices under the brush while keeping them on the target surface. The
  icons already exist (`ff_conform_move` / `_rotate` / `_scale` / `_relax`).
  *(Built: Conform Move / Rotate / Scale / Relax in `CONFORM_BRUSHES`, `freeform.py`.)*
- [x] *(2026-10-29, checked against Seb's screenshot of Max 2026's Freeform tab)* **What the
  Freeform tab has that Moritz still lacked** *(done 2026-10-29 except the open points below)*:
  - *(done, Maximize 347a9e3)* PolyDraw **Draw On: Grid / Surface / Selection**, for PolyDraw and
    the Conform brushes. Grid = the ground, or in Top / Front / Side the view's plane through the
    origin.
  - *(done, Maximize c16f511: a Paint Deform rollout in Edit Poly, own brushes on the mesh, not
    Sculpt Mode; Shift, Shift Rotate, Shift Scale, Push/Pull, Relax/Soften, Flatten,
    Pinch/Spread, Smudge, Noise, Exaggerate, Revert; right-click or Enter commits, Esc cancels,
    Ctrl inverts; Size, Strength, Push/Pull Value)* **Paint Deform** (Shift, Shift Rotate, Shift Scale, Push/Pull, Relax/Soften, Flatten,
    Pinch/Spread, Smudge, Noise, Exaggerate; Pick, Commit / Cancel / Revert, brush presets).
    `freeform.py` says the Sculpt modifier covers it, but Max uses these as brushes on a low-poly
    Edit Poly mesh, from buttons. Blender's sculpt brushes come close (Grab / Elastic, Draw /
    Inflate, Smooth, Flatten, Pinch, Snake Hook); Noise and Exaggerate have no counterpart. Seb
    wants the buttons in Edit Poly (icons `pd_*` are done). Decide: buttons that start Blender's
    sculpt brushes on the Edit Poly mesh, or own brushes like Conform.
  - Everything else on the tab is built: Drag, Conform and its four brushes, Step Build, Extend,
    Optimize, Shapes, Splines, Surface, Topology, Strips, Branches.
- [ ] **Freeform, still open:** Paint Deform's Pick (lock an object), brush presets (Max's
  Defaults), Mirror; the `ff_*` / `pd_*` icons aren't integrated (where icons go is still Seb's
  decision). All 38 test files pass, but nothing has been tried with a real mouse yet: Seb to
  try the brushes.
- [x] *(done 2026-10-29, Maximize 85d694d: every Conform brush starts from Object Mode, enters Edit
  Mode for the session and goes back at the end)* *(Seb, 2026-10-29: "why does conform brush only work in edit mode?")* **Conform brushes in
  Object Mode too**, as in Max, where Freeform works at any level. Simplest way: started in
  Object Mode, the brush enters Edit Mode for the stroke and returns when it ends. Watch out: it
  edits the base mesh, so a Moritz Edit Poly modifier above it can make what you see differ from
  what you paint.
- Freeform's Blender equivalents today: Step Build / Extend = Poly Build, Draw On = face snapping
  plus the Retopology overlay and Shrinkwrap, Splines = the curve Draw tool on surfaces, Strips /
  Surface / Topology = the Bsurfaces extension (roughly); nothing for Shapes and Branches; Optimize
  is roughly Dyntopo's simplify brush
- Left out: Paint Deform (Sculpt Mode, decided), Object Paint (Geometry Nodes scattering is the
  nearest; decide later), Populate (crowds, out of scope)

### Sculpt modifier (Seb's decision, 2026-10-25; after Phase 3b)

One **Sculpt** modifier that unifies Blender's Multires modifier and the sculpt brush settings,
modeled on 3ds Max's Retopology modifier: it can sit mid-stack, with limitations.
- [x] *(2026-10-26, Maximize `sculpt.py`, `tests/test_sculpt.py`; no core change needed)* The modifier panel holds both the Multires controls (levels for viewport / sculpt / render,
  Subdivide, Simple, Linear, Unsubdivide, Delete Higher, Apply Base, Rebuild Subdivisions) and the
  brush settings (brush, radius, strength, falloff, symmetry, Dyntopo), so sculpting is set up
  in one place. Selecting it and entering its level starts Sculpt Mode on it.
- [x] **Dyntopo on** applies the current subdivisions first (bakes the Multires levels into the mesh),
  then sculpts with dynamic topology. Ask before applying (it can't keep the levels).
- [x] *(a native Edit Poly in Deform mode named Sculpt, sculpted on a stand-in; warning icon in the stack)* **Mid-stack:** allowed, with a warning symbol next to the modifier in the stack list
  (tooltip says why: what's below must keep its topology; Dyntopo and remesh are off there).
  Sculpt edits are stored as per-vertex offsets (like Edit Poly's Deform mode) on the stack below.
- [x] *(in the rollout and the add message)* Limitations to spell out, as in Max's Retopology: a topology change below invalidates the
  sculpt (warn and offer to rebase, as Edit Poly does); mid-stack evaluation is slower; Dyntopo
  only at the bottom of the stack.
- Engine: core change (Multires and Sculpt Mode are core; the Edit Poly session shows the way:
  `session_begin`, offsets written back on exit). Warn before starting: needs a rebuild.
- *Files: keep it a Multires modifier underneath where possible, so stock Blender opens it as a
  normal Multires; a mid-stack sculpt layer needs Edit Poly-style storage (stock keeps it disabled
  and saves it back). Check and warn about both directions before building.*
- Open: what the brush settings in the modifier do when two Sculpt modifiers are in one stack (shared
  tool settings in Blender, per modifier in the panel?)

## Phase 3 — Splines

Rule: only what Max does better. Kept from Blender: handle types, curve extrude and bevel (Renderable Spline), Screw (Lathe), text objects.
- [x] Legacy Curve objects for editable splines (Blender's curve Edit Mode); the tools are in Maximize (`shapes.py`, `spline_tools.py`, `tests/test_splines.py`)
- [x] Parametric shapes: Rectangle (corner radius), Circle, Ellipse, Arc, NGon, Star, Helix, Donut — drag-created and editable like the primitives, with Thickness; 1 converts to an editable spline
- [x] Line tool: click for corner, drag for Bezier, with grid snapping (Add > Shapes > Line). AutoGrid (on surfaces) done (Creation below)
- [x] Fillet and Chamfer on spline vertices
- [x] Outline
- [x] Refine (Blender's Pen tool, in the Max Spline Tools menu)
- [x] Trim/Extend, Break, Connect (Connect is Blender's Make Segment)
- [x] 2D shape booleans (union, subtract, intersect) through an exact mesh boolean of slabs, no C++ clipper needed
- [x] Loft (path plus shape, both stay live)

### Phase 3b — Splines exactly like Max (plan, 2026-10-25)

Found: the parametric shapes are Geometry Nodes poly curves with a fixed point count ("Steps"),
not Bezier splines. A Circle is 32 corner points, where Max's is 4 smooth Bezier vertices;
converting gives those 32 corners. Only the Rectangle's corner radius and the Line tool make real
Bezier handles. Goal: creating, editing and converting splines behaves exactly as in Max. The Boss
asked for Max's behavior here, so this overrides "only what Max does better" for splines.

- [x] **Shapes are real Bezier splines with Max's vertex counts and handles** (done 2026-10-25),
  so 1 (Convert to Editable Spline) gives what Max gives: Circle, Ellipse, Arc, Donut, Rectangle,
  NGon, Star and Helix with every parameter, matching a Max 2026 dump to 1e-5
  (`Maximize/tests/test_shapes_max.py`; rules in [docs/splines_max_design.md](docs/splines_max_design.md)).
  Engine: a Curve object whose splines the add-on rebuilds when a parameter changes (parameters
  on the curve data, `maximize/shapes.py`). Steps = curve resolution, Thickness = round bevel.
  *Files: plain Blender Bezier curves; stock Blender shows the shape and only loses the parameter
  editing. Shapes saved before stay Geometry Nodes poly curves and keep working (editable,
  convertible); new ones are Bezier. Egg is built too.*
- [x] **Interpolation as in Max**: Steps per shape (default 6 = Blender resolution 7) done.
  Optimize: core flag `CU_OPTIMIZE` / `Curve.use_optimize` (`curve_legacy_convert.cc` turns
  segments whose handles lie on the chord into vector segments, so they evaluate to their end points),
  on for new shapes; written, waiting for the rebuild. *Files: a new bit in `Curve.flag`; stock
  Blender ignores it and draws straight segments with Steps points, so the shape looks the same.*
  Adaptive: done 2026-10-26 (Maximize `spline_more.py`): about 6 degrees per step, one count per
  spline (Blender has one resolution per spline, not per segment), for shapes and editable splines.
- [x] **Max vertex types** (done 2026-10-25, `spline_tools.py`; Edit Spline quad menu and the
  Max Spline Tools menu; the Modify tab entry comes with Phase 6) in the quad menu and the Modify tab: Corner, Smooth, Bezier, Bezier
  Corner (Blender's Vector, Auto, Aligned, Free handles), Reset Tangents, Make First, Reverse.
  *Files: unaffected (Blender's own handle types).*
- [x] *(open rest listed below)* **Editable Spline levels 1 Vertex, 2 Segment, 3 Spline** (done 2026-10-25, `spline_tools.py`):
  a click at 2/3 picks a whole segment or spline (Ctrl adds, Alt removes), transforms of the picked
  vertices, Delete per level, Divide, Detach, Explode, Close, Mirror, Weld (joins or closes
  splines), Fuse, Attach (object level), Reset Tangents / Make First / Reverse, Trim / Extend /
  Fillet / Chamfer / Outline / Break / Connect; in the Edit Spline quad and the Modify tab
  (Rendering, Interpolation, Selection, Geometry rollouts). Pressing 1/2/3 on a parametric shape
  converts it first. Show Selected Segs done 2026-10-26 (red overlay). Bind / Unbind, Lock Handles
  Alike / All and the hover highlight were done since (`spline_more.py`, commit 417eef2).
- [x] **Creation as in Max** (done 2026-10-25): Line with Initial Type (Corner/Smooth) and Drag
  Type (Corner/Smooth/Bezier), Backspace removes the last vertex, Shift for 90 degrees, clicking
  the first vertex asks "Close spline?", Start New Shape off adds to the selected shape; Keyboard
  Entry for every primitive and shape; AutoGrid (Create menus; surface under the mouse); Text
  (Blender's text object), Freehand (Blender's Draw tool on a new shape), Section (plane through
  the 3D cursor cuts the selected meshes). Egg (done, measured). Section as a live plane object
  (done 2026-10-26).
- [x] **Rendering as in Max** (done 2026-10-25, `spline_render.py`): Enable In Renderer / In
  Viewport, Radial (Thickness, Sides, Angle) and Rectangular (Length, Width, Angle), Auto Smooth with
  threshold, Generate Mapping Coords, for shapes and editable splines, as a "Rendering" Geometry
  Nodes modifier. *Files: a normal Geometry Nodes modifier; stock Blender renders it the same.*
- [x] **Edit Spline modifier**: stage 0 done in Maximize (2026-10-25, `edit_spline.py`): edits
  on a parametric shape follow its parameters while the knot count below holds. Stage 1 done
  (2026-10-25): the native `EDIT_SPLINE` modifier (type 201, `MOD_edit_spline.cc`) stores the
  edited splines with each knot's input index; edits follow the splines below while their knots
  hold, and stay as they were (flagged) when the knot count below changes. Stage 3 partly done:
  Maximize adds and stores into the native modifier when the build has it (no helper objects).
  Tests: `moritz/tests/test_edit_spline_native.py`, Maximize `tests/test_edit_spline_native.py`.
  *Files: stock Blender keeps the modifier disabled with its data and shows the unedited splines;
  Moritz revives it on load.*
  - [x] The Interpolation rollout (Steps, Optimize, Adaptive) on the Edit Spline modifier, as Max
    shows it there (Seb, 2026-10-25)
  - [x] Stage 2 (2026-10-25): edit on the object itself in Edit Mode, no stand-in object. A
    session (`EditSplineModifier.session_begin`) makes Edit Mode build the edit-nurbs from the
    modifier's result; leaving writes back into the modifier, knots mapped through the edit-nurbs'
    key index; the object's own splines stay as they were. Test:
    `moritz/tests/test_edit_spline_session.py`.
  - [x] Stage 3 rest (2026-10-26): Convert to Native, a button on stage-0 (Geometry Nodes) Edit
    Spline modifiers, keeps the edit and removes the helper objects. Not automatic on load:
    *stock Blender shows a Geometry Nodes Edit Spline's edit, but not a native one's.*
- [x] Tests: `test_shapes_max.py` (every shape against Max 2026, rendering, optimize),
  `test_splines.py` (levels, tools, creation), `test_max_shapes_import.py` (Max round trip)
- [x] Max scene exchange carries splines (done 2026-10-25): the exporter writes knots with in/out
  vectors, vertex and segment types and the shape, interpolation and rendering parameters; the
  importer rebuilds Circle, Rectangle, Ellipse, Arc, NGon, Star, Helix and Donut parametrically and
  other shapes as exact Bezier splines (Max's own handles kept; line segments straight). Round trip
  checked with 3ds Max 2026.

#### Editable Spline Modify panel by priority (Seb's screenshot of Max's Line panel, 2026-10-25)

Lay out the Modify tab's spline rollouts in this order (most used first); rarely used controls go
into closed sub-panels.
1. Daily: sub-object levels (Vertex / Segment / Spline); vertex types (Corner, Smooth, Bezier,
   Bezier Corner); Rendering: Enable In Renderer / In Viewport, Radial Thickness and Sides; Attach;
   Refine; Fillet; Outline (with Center); Weld (threshold); Break; Interpolation Steps.
2. Weekly: Create Line, Connect, Insert, Fuse, Chamfer, Trim / Extend (Infinite Bounds), Boolean,
   Close, Delete, Detach (Copy), Divide (count), Make First, Reverse, Mirror (Copy, About Pivot), Optimize, Rectangular
   rendering (Length, Width, Angle, Aspect), Generate Mapping Coords, Auto Smooth, Hide / Unhide All,
   Soft Selection.
3. Rare: Attach Mult., Cross Section, CrossInsert, Cycle, Bind / Unbind, Lock Handles (Alike / All),
   Area Selection, Segment End, Select By, Named Selections Copy / Paste, Show Vertex Numbers,
   End Point Auto-Welding, Connect Copy, Reorient, Tangent Copy / Paste, Adaptive, Use Viewport
   Settings, Real-World Map Size, Twist Correction, Cap / Quad Cap options, Explode (to Splines /
   Objects), Detach options Same Shp and Reorient, Show Selected Segs.
- [x] **Required (Seb, 2026-10-25), even though they are rare** (Maximize 40b3ecc,
  tests/test_spline_required.py):
  - [x] End Point Auto-Welding (Automatic Welding, Threshold Dist): after each finished Move
    (key, gizmo or tool) a moved end within the threshold snaps onto the other end and welds. It is
    its own undo step after the move.
  - [x] CrossInsert (threshold): adds a vertex to both splines where they cross, in local XY;
    the threshold is how far apart they may pass in Z
  - [x] Twist Correction for the rendered spline (Minimum Twist on, Z Up off)
  - [x] Cap options: Cap, Quad Cap, Segments, Sphere (domes on open spline ends; radial only)
- [x] Done 2026-10-26 (Maximize 473bfc8, `spline_more.py`, `tests/test_spline_more.py`): Create
  Line, Insert, Refine (Connect, Linear, Closed), Cycle, Hide / Unhide All, Attach Mult. (Reorient),
  Cross Section, Area Selection, Select By (Segment / Spline), Named Selections Copy / Paste, Show
  Vertex Numbers (Selected Only), Tangent Copy / Paste, Detach (Same Shp, Reorient, Copy), Explode
  (To Splines / Objects), Mirror (Horizontal / Vertical / Both, Copy, About Pivot), Rendering's
  Aspect with its lock and Use Viewport Settings with the Viewport / Renderer switch (Rendering
  group revision 3). Soft Selection is Blender's proportional editing.
- [x] *(2026-10-26, Maximize)* Segment End, Connect Copy (Shift+drag copies get joined to the
  originals), Section as a live plane object (yellow cut while it moves, Create Shape)
- [x] *(2026-10-26, Maximize)* Bind / Unbind: an end vertex stays on a segment's middle (kept by
  the add-on in the curve's `mx_bind` property; stock Blender keeps the vertex where it was)
- [x] *(2026-10-26, Maximize)* Refine's Bind First / Bind Last, Lock Handles (Alike / All: dragging a
  selected vertex's handle), hover highlight for knots, segments and splines

## Phase 4 — Core gaps no add-on can fill

Smallest first. Three of them turned out to be possible in Maximize after all (marked).
- [x] **Imperial fractions**: unit display and parsing (`blenkernel/intern/unit.cc`), Scene > Units > Fractional Inches
- [x] **Freeze**: objects with selection disabled draw gray (workbench); Freeze Selection / Unfreeze All in the quad menu; the Outliner's selectable column is the Freeze column
- [x] **Smoothing groups** *(Maximize, `smoothing.py`)*: face attribute `smoothing_groups`, the 32-button panel, Auto Smooth, Select By SG, Groups From Sharp Edges; sharp edges follow the groups, FBX writes them as smoothing groups
- [x] **Instance vs Reference** *(Maximize)*: instances and references share the mesh and the original's modifier stack (a Shared Stack Geometry Nodes modifier); Make Unique. A modifier added to an instance goes on the shared stack (the original's), as in Max; references keep theirs (2026-10-28)
- [x] **Modifier gizmos** *(Maximize, `modifier_gizmos.py`)*: Simple Deform (Bend, Twist, Taper, Stretch) dial and arrow; FFD stays Blender's Lattice
- [x] **Performance**: profile a 10k-object scene (Outliner, undo, selection): `moritz/docs/performance.md`
- [x] Undo hotspot: keep the depsgraph relations when an undo step changed none (800 ms -> 85 ms at 10k objects; `memfile_undo.cc`, `test_undo_relations.py`)
- [x] Whole-window redraw at 10k objects measured per region (see `docs/performance.md`): the Outliner tree rebuild is half of it and only runs on structural changes; no change needed
- [x] *(2026-10-26, `memfile_undo.cc`, `DEG_graph_id_replace_orig`)* Scene fingerprint so undo/redo pairs also keep relations: scenes and collections fingerprinted, the master collection's depsgraph node re-keyed when the scene is re-read (frame change undo at 10k objects 800 -> 290 ms; `docs/performance.md`)

## Phase 5 — Pipeline and release

- [x] Max scene exchange without a closed-format parser: Max writes the scene with `maximize/max_side/moritz_export.ms`, Maximize imports it (File > Import > Max Scene (.mxscene), `max_scene.py`): polygons, UVs, Multi/Sub IDs, smoothing groups, hierarchy, pivots, units, layers, frozen/hidden, cameras, lights; `tests/test_max_scene.py` (tested with 3ds Max 2026 on the same kitchen: 33 objects, 228k vertices, textures, in 3.7 s; `3dsmaxbatch.exe moritz_export.ms -sceneFile x.max` with `MORITZ_EXPORT_PATH` exports without a dialog)
- [x] V-Ray/Corona/Physical/Standard → Principled converter (`max_materials.py`), used by the import
- [x] License check of the direct `.max` importer: "Import Autodesk MAX (.max)" 1.9.2 (extensions.blender.org/add-ons/io-scene-max, Sebastian Sille et al.) is GPL-3.0-or-later, compatible with Moritz; imports meshes, UVs and Standard/Physical/V-Ray/Corona materials, Blender 4.2+
- [x] Bundled unmodified in `release/extensions/system/io_scene_max` (the System extensions repository), enabled by default (File > Import > Autodesk MAX (.max)); tested on a real 33 MB kitchen scene: 22 meshes, 233k vertices in 10 s; Physical material textures fail inside the extension (upstream bug), so the exporter route stays the better one when Max is at hand
- [x] **Fix the Physical material textures in the .max importer** *(done 2026-10-28, our copy
  patched, see PATCHES.md "Pipeline". The real cause was one step earlier: the importer reads the
  asset paths from the 11th stream, but with the Summary Information streams present that is
  `DocumentSummaryInformation`, and `FileAssetMetaData3` is the 12th, so every lookup missed. Now
  found by name; plus the `None` fix, per-slot reads and full paths. kitchen.max: 0 errors, 5 of the
  Physical textures load (was 0), 15 s. The Dishwasher's USD Preview Surface material is read now
  too (its four OSL bitmap maps load; 2026-10-28, not offered upstream yet). Offered upstream with Seb's OK:
  https://github.com/nrgsille76/io_scene_max/pull/50; drop our patch once a release has it)* (Seb, 2026-10-28). Error on every
  Physical material: `'PhysicalMtl' Error: argument should be a str or an os.PathLike object ...,
  not 'dict'` (kitchen.max and the Torus exporter test scene). **Cause found:** `get_metadata()`
  (`import_max.py` line 863) ends with `return pathdata`; when the bitmap's index isn't in the
  metadata table, it falls through and returns the whole table (a dict) instead of `None`, and
  `Path(bitmap)` in `get_physical_material` raises, which loses all of the material's textures, not
  just the missing one. Fix: return `None` there, and resolve each slot on its own so one bad slot
  doesn't drop the others. Then check why the index is missing: fixed slot numbers (1, 2, 4, 21, 24)
  that may not match Max 2026's Physical material, or maps wrapped in Color Correction, Normal Bump
  or OSL bitmaps. Steps: reproduce with the kitchen .max and the console, compare the slots with a
  Physical material saved in Max 2026, patch our copy (GPL allows it; record it in PATCHES.md and
  `MORITZ.txt`, which says "unmodified" today), then offer the fix upstream
  (github.com/nrgsille76/io_scene_max) only with Seb's OK
- [x] FBX presets: "To 3ds Max" / "From 3ds Max" (scene units, smoothing groups, no leaf bones)
- [x] Portable zip: `moritz/tools/make_portable_zip.py` (add-on copied in, no debug symbols or build tools); smoke-tested
- [x] Windows installer: `moritz/tools/make_msi.py` (WiX 5, Program Files\Moritz, Start Menu shortcut, own upgrade code, no file associations)
- [x] Docs: "Moritz for Max users" cheat sheet (Max term → Moritz location): [docs/max_users.md](docs/max_users.md)
- [x] CI for Maximize: background tests on Blender 5.3 (GitHub Actions)
- [ ] 0.2 release (Seb, 2026-10-25: the first release is Moritz 0.2, on Blender 5.3)

## Phase 6 — Command Panel (plan, 2026-10-25)

Max's Command Panel replaces the look of Blender's Properties editor: the same editor, renamed, with
Max's two most used tabs first. Standing rule: say for every step whether it breaks files coming
from Blender (or going back to it).

- [x] **Rename the Properties editor to "Command Panel"** (editor type menu, header, tooltips,
  manual links). Only the label changes: `SpaceProperties` and the Python type `'PROPERTIES'` stay,
  so scripts and add-ons that look for it keep working. *Files: UI only, unaffected.*
- [x] **Rename the Modifiers tab to "Modify"** (label and tooltip of `BCONTEXT_MODIFIER`). *Files:
  UI only, unaffected.*
- [x] *(stage 1)* **Modify tab as in Max**: the Max-style stack list on top (newest modifier first, base object
  at the bottom, on/off toggles, Edit Poly rows expand into the five sub-object levels, click to
  make a level active, reorder), the selected modifier's settings below; Blender's full modifier
  panels stay available underneath. *Files: UI only, unaffected.*

### Max 2026's modifier list against Blender (Seb, 2026-10-29: "let's go through the 3dsmax modifier list")

Source: Seb's Max 2026, printed by MAXScript (`Modifier.classes` and `SpacewarpModifier.classes`, the
creatable ones): 139 object-space and 13 world-space modifiers. No tyFlow modifiers are listed, so
tyFlow isn't installed there. Status per group, to go through with Seb:
- **Blender has it** (use Blender's, Max name in the name scheme): Array, Bend / Taper / Twist /
  Stretch (Simple Deform), Boolean, Chamfer (Bevel), Cloth, Conform (Shrinkwrap), Crease /
  CreaseSet (crease attributes), Displace, Edit Normals (Normal Edit), FFD (Lattice, but needs a
  lattice object), Lathe (Screw), Linked XForm (Hook), Mirror / Symmetry (Mirror with Bisect),
  MeshSmooth / TurboSmooth / OpenSubdiv / Subdivide / Tessellate (Subdivision Surface), Morpher
  (shape keys), MultiRes / Optimize / ProOptimizer (Decimate), Path Deform (Curve), Skin / Physique
  (Armature), Skin Wrap / SurfDeform / PatchDeform (Surface Deform, Mesh Deform), Point Cache
  (Mesh Cache), Relax (Laplacian / Corrective Smooth), Smooth (Smooth by Angle), Retopology
  (Remesh / QuadriFlow; Moritz Freeform), Ripple / Wave (Wave), Shell (Solidify), Spherify (Cast),
  UVW Xform (UV Warp), Camera Map (UV Project), Vertex Weld / Welder (Weld), Weighted Normals,
  Attribute Transfer (Data Transfer), MassFX RBody (Rigid Body), Hair and Fur (hair curves).
- **Moritz has it:** Edit Poly, Edit Spline, UVW Map; Edit Mesh / Edit Patch are covered by Edit
  Poly.
- **Missing, worth discussing:**
  - Selection modifiers that pass a sub-object selection up the stack: Mesh Select, Poly Select,
    Vol. Select, SplineSelect, FFD Select. Blender's stack has no selection passing (only vertex
    groups / Geometry Nodes).
  - FFD as a real stack modifier with its own control points (no separate lattice object),
    including FFD(cyl).
  - XForm (a gizmo transform in the stack), Affect Region, Push, Skew, Squeeze, Melt, Noise (as one
    modifier), Slice, Cap Holes, Face Extrude, Quadify Mesh, Delete Mesh, Normal (flip), Mesh
    Cleaner, Preserve, Lattice (struts and joints; Blender's Wireframe has no joints), Substitute,
    Material / MaterialByElement, MapScaler (real-world map size), Unwrap UVW as a stack item.
  - **Spline modifiers.** Blender curves have no modifier stack of their own: Extrude, Bevel, Bevel
    Profile, Sweep, Renderable Spline, CrossSection, Surface, Spline Chamfer, Spline Mirror, Spline
    Overlap, Spline Relax, Normalize Spline, Optimize Spline, Trim/Extend, Spline Morph, Spline
    Influence, Spline IK Control, DeleteSpline. Some exist as curve settings (extrude, bevel
    depth / object) or Geometry Nodes.
- **Skip** (renderer, plugin or legacy): the seven Arnold modifiers, Civil View Extrude Building,
  Garment Maker, mCloth, Flex, Particle Face Creator / Skinner, PFlow Collision Shape, the Patch
  modifiers (Patch Select, DeletePatch, Turn to Patch), HSDS, Disp Approx, Displace NURBS, Surface
  Mapper, Attribute Holder, Data Channel / Select By Channel, the UV as Color / HSL modifiers,
  Filter Mesh Colors By Hue, Turn to Mesh / Poly, UVW Mapping Add / Clear, VertexPaint, STL Check,
  Skin Morph, Surface Select, Projection, Spline IK Control? (check).

- *(Seb, 2026-10-29)* **"Moritz list" column, a proposal** (Blender / Max / Mix / Skip per
  modifier). The list's labels follow the name scheme. **The editable list is the artifact
  [Moritz Modifier List](https://claude.ai/artifact/UJ3umZx3yP95ychyW6HwDd)**: all 152 rows with
  the name in Blender, where it lives in Blender, the Moritz column (editable) and a comment per
  row, in its database (`lists/modifiers`). Seb comments there; read it back before deciding.
- *(Seb's comments in the list, read 2026-10-29)* Everything not named here stays as proposed.
  - **Extrude, Bevel, Bevel Profile become one modifier:** Extrude with three buttons on top
    (Extrude / Bevel / Profile), like Simple Deform's mode buttons.
  - **Cap Holes:** Max version, with a quad cap option (like Edit Poly's Cap).
  - **Conform:** keep Blender's Shrinkwrap as it is.
  - **Edit Mesh → Mix:** Edit Poly needs Edit Mesh's **Explode** feature, and maybe a **Show
    Normals** display option.
  - **Lathe:** Seb finds "Screw" a bad name. Blender's Screw modifier does make real screws
    (Screw offset + iterations give threads and springs), so **both**: Lathe (no offset) and Screw
    (with offset), one Blender modifier underneath. **Corrected (Seb, 2026-10-29): keep the Screw
    modifier as it is**, one entry. Only the name scheme changes it: in the Max scheme it
    displays as **Lathe**, in the Blender scheme as Screw.
  - **Noise → Max**, **Normal → Max** (own modifiers, not only Blender's under a Max name).
  - **ProOptimizer:** Max's algorithm is better; try to match it (Decimate underneath isn't
    enough).
  - **Retopology:** Max's algorithm is better; try to match it (Remesh isn't enough).
  - **Quadify Mesh** and **Unwrap UVW:** not later, plan them now (both native, rebuild).
  - **STL Check → Max**, **VertexPaint → Max**.
  - **Turn to Poly → Mix:** what Seb needs from it is removing vertices on straight edges that
    only have two edges. Proposal: a **mesh cleaning modifier** with that option (and others).
  - **Camera Map (WSM) → Max:** what Seb needs is Max's **Camera Map Per Pixel** (a map, not a
    modifier, a 3ds Max plugin). Blender's shaders can do it with the Texture Coordinate node's
    Window / Camera output; plan it as a Moritz material map or node group.
- *(Seb, 2026-10-29: "when we search in the modifier list for bend, can it show simple deform?")*
  **Search keywords for the Add Modifier filter.** Each entry matches its Max name, its Blender
  name and a few words for what it does. For example, "bend" finds Bend and Simple Deform (Simple
  Deform's keywords: bend, taper, twist, stretch), and "solidify" finds Shell in the Max scheme.
  This works in our own flat list; Blender's menu search only matches labels.
- *(2026-10-29)* **Name clashes** to label differently in the Max scheme: Skin (Max = Armature,
  Blender = Skin modifier), Smooth (Max = Smooth by Angle, Blender = vertex smoothing), Lattice
  (Max = struts and joints, Blender = Max's FFD), Bevel (Max = spline bevel, Blender = Max's
  Chamfer).

### Max-style modifier stack in the Modify tab (plan, Seb, 2026-10-25)

Layout from top to bottom, as in Max's Modify panel:
1. **Name and color** of the object (Max's name field and wire color swatch).
2. **Add Modifier button** (Seb: keep Blender's button, not Max's list): one flat menu with every
   modifier at once, no submenus, as in Blender before 4.x; modifiers that don't work on the object
   type are left out; typing the first letters shrinks the list.
3. **The stack**, newest on top, the base object at the bottom ("Editable Poly", "Line", "Box" with
   its parameters):
   - each row: eye (on/off, Seb: the eye, not Max's light bulb), expand triangle, name; italic name
     for instanced (shared) modifiers; on the right, the icon of the active sub-object level (as in
     Seb's screenshots); disabled rows grayed; a warning symbol where a modifier has a problem
     (Edit Poly topology changed below, Sculpt mid-stack)
   - expanding a row shows its sub-object levels: Edit Poly Vertex / Edge / Border / Polygon /
     Element, UVW Map Gizmo, Bend Gizmo / Center, FFD Control Points / Lattice; clicking a level
     enters it
   - click selects the modifier (its settings appear below); drag to reorder; Delete removes;
     Ctrl+click selects several for copy
   - right-click menu: Rename (also double-click), Delete, Copy, Paste, Paste Instanced, Make Unique,
     Collapse To, Collapse All, Off in Renderer
   - **Paste Instanced** (Seb: keep): the pasted modifier stays shared with the copied one, also
     on copies (not only instances), so editing one changes all; shown with an italic name;
     Make Unique breaks the link
4. **Button row** under the stack: Show End Result (Maximize's `show_end_result`), Make Unique,
   Remove Modifier.
- Left out (Seb, 2026-10-25): Max's light bulb (the eye instead), Configure Modifier Sets and the
  modifier-set button grid (the flat Add Modifier menu replaces them), Pin Stack (Blender's pin is
  in the header), Cut (Copy and Delete), the draggable bar (Blender's lists have a resize grip).
5. **Settings of the selected entry only**: the selected modifier's rollouts, or the base
   object's parameters when the base is selected (Max shows one entry at a time).

Steps:
- [x] **Fixes from Seb's look at the Modify tab (2026-10-27)** *(done 2026-10-27; UI only, files
  unaffected: "base selected" is simply no active modifier, which stock Blender also allows)*:
  - [x] Remove Maximize's "Modifier List" dropdown: it duplicates Add Modifier; keep Add Modifier
    (UVW Map and the Max-named modifiers moved into Add Modifier)
  - [x] No "Max" panel: Maximize's tools (Selection, Edit Geometry…) belong in the Edit Poly
    modifier's own settings, shown when Edit Poly is selected in the stack (Maximize rollouts in a
    header-less subpanel of the Edit Poly, Edit Spline and Multires panels)
  - [x] When the base object is a parametric primitive or shape, its Parameters (Length, Width,
    Height, Segments…) show as the base entry's settings: the base row is clickable, named after
    the kind ("Box"), and the Parameters modifier is hidden from the stack (hooks
    `DATA_PT_modifiers.moritz_base_draw` / `moritz_base_entry`). Editable Poly and Editable Spline
    bases show their rollouts the same way. The base's own modifier panel no longer shows under its
    rollouts (new `template_modifiers(exclude=...)`, 2026-10-28)
  - [x] The five level buttons appear twice (text row under the stack, icons in "Selection"): keep
    them in one place, Edit Poly's Selection section, plus the levels in the stack row
  - [x] **Target look** *(done 2026-10-28: stack drawn by hand with left-aligned rows (new
    `UILayout.use_text_left`), levels under an open entry, `template_modifiers(only_active=True)`
    shows only the selected entry's panel, so the hidden Parameters panel is gone; Show Cage at the
    top of Edit Poly, its two colors stay in Edit Geometry. Also fixed: Edit Poly / Edit Spline
    sessions ended right after starting in the app. UI only, files unaffected)* (Seb's Max screenshot): the stack box with one row per entry (eye,
    expand triangle, name; the selected row highlighted; the base object, e.g. "Box", last with no
    eye); under it one row of icon buttons (Show End Result highlighted when on, Make Unique,
    Remove Modifier), no text buttons; then the selected modifier's sections in Max's order: for
    Edit Poly, Show Cage (with its two colors) at the top, then **Selection** with the five level
    icons (Vertex, Edge, Border, Polygon, Element) as one icon row, then the other Edit Poly
    sections. Edit Poly Mode's Model / Animate, Commit, Settings and Cancel stay left out (decided
    2026-10-25), so only Show Cage is left of that section.
- [x] Stage 1, Python (`bl_ui/properties_data_modifier.py`, committed d71c9ca72de; reviewed
  by the main session): list newest first, on/off toggle, base object row, Edit Poly levels below
  the list. Blender's modifier panels stay below.
- [x] Stage 2, Python (2026-10-26): sub-object levels under the stack (Edit Poly, Edit Spline; Blender's lists can't nest rows), level icon, italic instances, warning
  symbol, right-click menu, the button row, modifier clipboard (Copy / Paste; Blender
  only has Copy to Selected). Instanced rows show a link icon (no italics in Blender's lists). The Delete
  (and X) key in the Modify tab deletes the modifier under the mouse, else the one selected in the stack
- [x] Paste Instanced (2026-10-26, `bl_operators/moritz_modifier_stack.py`; Edit Poly and Edit Spline paste as copies): modifiers shared between objects (one modifier's settings drive all its
  instances, kept in sync by Maximize like the shared Edit Poly on instances; *files: plain
  modifiers, stock Blender sees independent copies*)
- [x] Stage 3 (2026-10-26, the Python route): only the selected modifier's settings. Python-only route: collapse the other
  modifier panels (`show_expanded`) when one is selected; core route: an `active_only` option for
  `template_modifiers`. Decide which.
- [x] Stage 4 (2026-10-26, `OBJECT_MT_modifier_add_flat`, also on Ctrl+A): the flat Add Modifier menu (all modifiers at once, incompatible ones left out, type
  to filter)
- [x] *(Move Up / Down buttons next to the stack, 2026-10-26; dragging still open)* Drag to reorder: Blender's UI lists can't drag rows; needs a small core change (or Move Up /
  Down buttons and Ctrl+Up / Down until then). Warn before the core change.
- *Files: UI only. The only stored values are the modifiers' own expand flags (`show_expanded`) and
  their order, which stock Blender reads the same way.*
- [ ] *(Seb, 2026-10-29)* **Tab order and color:** Modify moves to second place, right under
  Create, as in Max's Command Panel. The other tabs keep Blender's order (Tool, Render, Output,
  View Layer, Scene, World, Collection, Object, Particles, Physics, Constraints, Data, Material).
  Create and Modify get a **distinct color** of their own, so they stand out from Blender's tabs
  (Blender uses grey for scene tabs, orange for Object, blue for modifiers / physics /
  constraints, green for data, red for material). **Seb picked teal** (Max's accent, which no
  Blender tab uses), 2026-10-29. *Core: the tab order is in `buttons_context.cc` / `space_buttons.cc`, the colors in the
  icon sheet (or new icons for the two tabs); needs a **rebuild**. Files: the tab is saved as a
  number, the numbers don't change, so stock Blender is unaffected.*
- [x] **New "Create" tab** (new `BCONTEXT_CREATE`, first in the tab column, shown with or without
  a selected object), Max's categories: Geometry, Shapes, Lights, Cameras, Helpers, Space Warps,
  Systems; "Object Type" buttons and Name and Color, as in Max. All parametric objects live here:
  the editable primitives (Box, Sphere, Cylinder, Cone, Tube, Torus, Plane), the parametric shapes
  (Rectangle, Circle, Ellipse, Arc, NGon, Star, Helix, Donut, Line), Loft, lights, cameras,
  empties. *Files: the open tab is saved as a number (`SpaceProperties.mainb`); stock Blender does
  not know the new one and falls back to the Object tab (`buttons_context.cc`), so nothing breaks
  in either direction. Objects made here are ordinary Blender objects (the parametric ones are
  Geometry Nodes modifiers, which stock Blender evaluates).*
- [x] **Quad primitives** *(done 2026-10-28, Maximize `quad_caps.py`: Quad Cap / Quad Poles on by
  default, off gives the old caps; Cap Segs added to ChamferCyl, Spindle and Gengon. L-Ext and C-Ext
  caps are split into 2 and 3 convex quads (2026-10-28))* (Seb, 2026-10-28; differs from Max's triangle-fan caps): all primitives
  come with quads. A **Quad Cap** checkbox, on by default, per primitive: an inner quad grid plus
  quad rings to the edge (Cap Segments = rings), clean with Sides a multiple of 4, one triangle to fit
  otherwise (same rule as Edit Poly's Cap). UVs stay clean.
  - Quad caps: Cylinder, Cone, ChamferCyl, Spindle, Gengon, Prism caps
  - Quad poles (quad-sphere style): Sphere, Capsule, OilTank
  - Already quads: Box, ChamferBox, Plane, Tube, Torus, Torus Knot, L-Ext, C-Ext, RingWave, Hose
  - Stay triangles: GeoSphere and Hedra (triangles are the point of them), Pyramid's sloped sides,
    Teapot
  - *Files: unaffected (Geometry Nodes primitives, one more input).*
- [x] **Next, before the Modify stack fixes (Seb, 2026-10-27): every parametric object of Max's
  Create panel**, with Max's sub-category dropdown under the category icons, AutoGrid, Start New
  Shape (shapes), and Name and Color (Max names: Box001). Each one drag-created and editable in
  Modify like the existing primitives. ✅ = built already. *Done 2026-10-27, except tyFlow (below):
  sub-category dropdown via the core hook `PROPERTIES_PT_create_category.subcategory_draw`, AutoGrid
  and Start New Shape checkboxes, buttons in Max's order, Max names without spaces (TorusKnot001).
  Test: Maximize `tests/test_create_primitives.py`.*
  - Standard Primitives: Box ✅, Cone ✅, Sphere ✅, GeoSphere ✅, Cylinder ✅, Tube ✅, Torus ✅,
    Pyramid ✅, Teapot ✅ (Utah patches, Body / Handle / Spout / Lid), Plane ✅, TextPlus ✅ (filled
    Blender text; Text is the outline-only one)
  - Extended Primitives ✅: Hedra, Torus Knot, ChamferBox, ChamferCyl, OilTank, Capsule, Spindle,
    L-Ext, Gengon, C-Ext, RingWave, Hose, Prism. Done 2026-10-28: Hedra Star1 (small stellated
    dodecahedron) / Star2 (great stellated dodecahedron) and Axis Scaling P / Q / R (triangles,
    squares, pentagons pushed out); RingWave Growth (once / cyclic), crawling Major / Minor waves and
    Inner edge breakup; Hose Bound to Object Pivots (Top / Bottom Object, Tension)
  - Splines: Line ✅, Rectangle ✅, Circle ✅, Ellipse ✅, Arc ✅, Donut ✅, NGon ✅, Star ✅,
    Text ✅, Helix ✅, Egg ✅, Section ✅ (live plane still open), Freehand ✅
  - Extended Splines ✅: WRectangle, Channel, Angle, Tee, Wide Flange (one drag sets the size;
    Max's second click for Thickness is still open). Start New Shape off works for Line only so far
  - [x] **tyFlow's objects**: *decided 2026-10-27 with Seb: only the ones that make meshes, and
    nothing named after tyFlow; take from tyFlow only what Max lacks. tyMesher's Blob mode is Max's
    own BlobMesh (Compound Objects), so Maximize builds BlobMesh (Size, Tension, Render / Viewport
    Coarseness, Off in Viewport, Blob Objects with Add / Remove) with tyMesher's extras (Mesh
    Volume, Resample Faces, Variation %, Smoothing, Adaptive). New Compound Objects sub-category.
    Test: Maximize `tests/test_blobmesh.py`. The rest (particles, caches, splines from particles,
    rigs, vehicles, space warps) is not built.* Original note: (Seb, 2026-10-27; tyFlow is a third-party Max plugin, names from
    docs.tyflow.com): tyFlow (the particle system itself), tyCache, tyMesher, tySplines, tySpliner,
    tyActor, tyBitmap, the tyVortex / tyWind space warps, the PhysX vehicle helpers (tyVehicle,
    Chassis, Wheel, Joint, Strut, Tread, Turret…). Scope note: tyFlow itself is a full particle /
    physics system (Blender's nearest: Geometry Nodes simulation zones); decide per object which
    ones to build and how far, starting with the simple ones. tyFlow also adds about 40 modifiers
    (tyBend, tyBoolean, tyConform, tyFaceExtrude, tyMeshToSplines, tySplineMesher, tyWeld, tySlice,
    tyRelax, tyMultifracture…), not part of this item.
  - *Files: like the existing ones, Geometry Nodes or Bezier curve objects that stock Blender shows
    unchanged (only the parameter editing is lost).*
- [x] Move Maximize's sidebar Create and Modify panels (Max tab) into the Command Panel tabs; keep
  the sidebar Max tab for the other tools
- [x] Without Maximize, the Create tab offers Blender's own primitives (not parametric after the
  first redo); with it, the parametric ones
- [x] Docs: `max_users.md` (Command Panel, Create, Modify), PATCHES.md (tests done:
  `moritz/tests/test_command_panel.py`)

### Icons for the Max functions (Seb, 2026-10-28)
- [x] *(Seb approved the fourth draft, 2026-10-29; SVGs handed to the main session)* Own
  icons in Blender's style (16 px, flat white, orange for the part the tool changes), drawn from the
  meaning, not copied from Autodesk's icons. **Only where Max has an icon and Blender has none**
  (Seb: text buttons in Max stay text buttons). **Max's icons are the inspiration** (Seb): same
  picture, Blender's style. Max 2026's icons are in `UI_ln/IconsDark.rcc` (Qt resource, unpacked
  only to look); Border is an open loop, Element a solid cube, spline vertices plus marks,
  Segment dots and a line, Spline a polyline, Show End Result a test tube (half / full), Make
  Unique two shared circles splitting into two. The Scene Explorer column icons are inside
  `SceneExplorer.dll`, not looked at yet. Second draft (2026-10-28): the 9 from Max's pictures;
  Display as Box, See-Through and the four modifier icons still from the first draft. **Border and
  Element: keep the first draft** (cube with the border / one element in orange; Seb: it matches
  Blender's style better than the loop and the solid cube). **Correction (Seb, 2026-10-29):** he
  meant the Border and Element icons Moritz uses now (Maximize `maximize/icons/border.png`,
  `element.png`, in the Selection row). **That's the style for all of them:** Blender's
  select-mode look, thick strokes, the picked part solid white, the context grey, rounded corners,
  no orange. Fourth draft (2026-10-29) in that style, Max's pictures as the idea: plus marks on a
  curve, one white segment, a white polyline, a test tube filling white, grey shared circles
  splitting into white ones, a bounding box around a grey ball, a see-through front face. List:
  - Edit Poly sub-object levels: Border, Element (Blender has vertex, edge, face).
  - Edit Spline sub-object levels: Vertex, Segment, Spline.
  - Stack buttons: Show End Result, Make Unique (Blender has the eye and remove).
  - Outliner columns: Display as Box, See-Through (Blender has Freeze, eye, renderable).
  - The Edit Poly, Edit Spline, Sculpt and Retopo modifiers: no icon in Max, but Blender's stack
    list needs one per modifier type.
- [x] *(Seb approved 2026-10-29; 28 SVGs handed to the main session)* **Freeform ribbon icons** (Seb:
  "do these", screenshot of Max's Freeform tab), same style. They have icons in Max, so they get
  icons here too:
  - PolyDraw, for the Retopo modifier: Drag, Conform, Conform Move / Rotate / Scale / Relax, Step
    Build, Extend, Optimize, Grid, Shapes, Splines, Surface, Topology, Strips, Branches, Pick.
  - Paint Deform, for Edit Poly: Shift, Shift Rotate / Scale, Push/Pull, Relax/Soften, Flatten,
    Pinch/Spread, Smudge, Noise, Exaggerate, Pick (locked).
  - Conform (Seb): a plane conformed to a ball, drawn as a slice (grey cut-through ball, white
    plane bent around its top); the Conform Move / Rotate / Scale / Relax icons use the same
    slice. Seb picked **variant A** (plain plane hugging the ball, 2026-10-29).
  - Commit, Cancel and Revert use Blender's CHECKMARK, X and LOOP_BACK; Defaults (brush presets)
    uses BRUSH_DATA.
- [x] *(Seb approved 2026-10-29; 29 SVGs handed to the main session)* **Modeling ribbon icons** (Seb:
  "make these", screenshot of Max's Modeling tab), same style, for the Edit Poly sections (no
  ribbon, see Phase 2):
  - Polygon Modeling: Soft Selection, Preserve UVs, Collapse Stack. The levels already have icons.
  - Modify Selection: Grow, Shrink, Loop, Ring. Loop / Ring + and - use Blender's ADD and REMOVE.
  - Edit: Repeat Last, NURMS, QSlice, Cut, Swift Loop, P Connect, and the four Constraints (none,
    edge, face, normal).
  - Geometry: Relax, Attach, Create. Subdivision: MeshSmooth, Tessellate, Use Displacement.
  - Align: Make Planar, To View, To Grid; X / Y / Z stay text buttons.
  - Properties: Hard, Smooth, Smooth 30. *(Seb, 2026-10-29: the first ones were unclear. Redrawn
    on a low-poly cylinder: Hard = each facet its own shade; Smooth = one even shade, edges only
    dotted; Smooth 30 = smooth sides, but a hard edge at the cap with an angle mark. Seb: faceted
    and smooth must be clearer, use gradients. Third try: Hard = five flat-shaded facets in
    steps; Smooth = one continuous gradient across the side, cap blended too; Smooth 30 = the
    same smooth side, cap a separate flat shade with a dark edge. Approved and handed to the
    main session, 2026-10-29.)*
  - *(2026-10-29: the other 26 were approved and handed to the main session as SVGs.)*
- [ ] After the OK: decide where they go. In Maximize as PNGs: no rebuild, but only in panels the
  add-on draws. In `release/datafiles/icons_svg`: they work everywhere, but that's a core change
  and needs a **rebuild**. Stock Blender files are unaffected either way.

## Phase 7 — Outliner with Max's Scene Explorer features (plan, 2026-10-25)

Rule: only what Max does better. Kept from Blender: the Outliner itself, collections as layers
(active collection = Max's current layer), search, sync selection, drag and drop to parent, batch
rename (Ctrl+F2, Max's Rename Objects), F2 rename (done).

No-brainers (approved by Seb, 2026-10-25):
- [x] *(2026-10-26)* **Freeze column** with Max's snowflake icon and name (today the selectable column does the job;
  done in Phase 4). *UI only.*
- [x] *(2026-10-26; Maximize `outliner.py`, core `mx_filter`; no Space Warps button: Blender has no such type)* **Type filter row in the header**, as Max's Scene Explorer toolbar: one click per Geometry,
  Shapes, Lights, Cameras, Helpers, Space Warps, Bones, instead of Blender's filter popover. Python
  (`space_outliner.py`); needs Shapes split out of "Others" (curves, text) — small core change for a
  new filter flag. *Files: a new bit in the Outliner's filter flags; stock ignores it.*
- [x] *(both done 2026-10-26, in the filter popover; See-Through is a new object draw flag `OB_DRAW_SEE_THROUGH`, drawn at 30 % alpha by the Solid (workbench) engine, Alt+X and Object > Viewport Display; stock Blender ignores the flag and draws the object opaque)* **Display as Box** and **See-Through** columns (per object: `display_type = 'BOUNDS'`, and
  X-ray per object), as in Max; core (Outliner columns are C). *Files: the columns' on/off flags
  are new bits in the Outliner space, stock ignores them; the object values are stock data.*
- [x] *(2026-10-26)* **Renderable** column under Max's name (Blender's render column, relabeled). *UI only.*
- [x] *(2026-10-26, Maximize)* **Double-click an object selects it and its children** (Max), as in the viewport; rename stays
  on F2 and Ctrl+click. Python keymap. *UI only.*
- [x] *(2026-10-26, Maximize; context menu)* **Unhide All / Unfreeze All** in the Outliner's context menu and header. *UI only.*
- [x] *(color done 2026-10-26: Maximize's Color By Layer, applied once, no live link; freeze and render by layer are Blender's collection toggles already)* **Layer properties by layer**: Max's "By Layer" for color, freeze and render; Blender's
  collection color tags drive the object color in the viewport. Medium; check first.
- Maybe, not no-brainers: Selection Sets as an Outliner view (Maximize's named sets), sorting by
  column (Blender sorts by name only), Max's separate Layer Explorer (Blender's View Layer mode
  already shows collections).

## Upstream maintenance (recurring)
- [ ] Merge each Blender release branch into `moritz/main` (last: 24 fixes from `blender-v5.3-release`, 2026-10-26, no conflicts, tests pass)
- [ ] Re-run the test suite and a smoke test of Maximize after each merge (last: 2026-10-26 after the 24-fix merge: 10 Moritz + 24 Maximize test scripts pass)
