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
- [ ] CI on every push (needs a self-hosted runner: a hosted one is likely too small for a full build)

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
- [x] Both shortcuts in menus and tooltips (Max key and Blender key), so Blender tutorials stay usable (core: `WM_keymap_lookup_blender_begin`)
- [x] Preferences: Maya navigation, F frames selection, Blender modal keys (Preferences > Keymap, under the Max and Moritz keymaps)
- [x] Editors: Graph Editor / Dope Sheet, shader editor, Outliner F2
- [x] Moritz column in the comparison page; assert keys in the background test (`test_keymap_options.py`); 146 of 216 Max keys, 0 conflicts. Also Shift+Z/Y view undo, Alt+` Show End Result, F5–F8 axis constraints

### Cameras (Seb, 2026-10-25) — all add-on work (Maximize), files unaffected
- [ ] **Point-of-view menu** (Max's "[Camera001]" / "[Top]" label menu), also on V over a viewport. Entries: the scene's cameras (look through), Perspective, Orthographic, Top/Bottom/Front/Back/Left/Right, and:
  - [ ] **Select Camera**: selects the camera you are looking through (in Blender today: click the camera frame's edge, or the Outliner)
  - [ ] **Lock Camera to View**, on by default: pan, orbit and zoom in a camera view move the camera instead of leaving camera view (Blender's sidebar > View > View Lock > Camera to View)
  - [ ] **Lock Camera**: the camera can't be moved by accident (location, rotation and scale locks; Blender's camera-to-view sync already respects them)
- Suggestions, not decided yet:
  - [ ] Camera navigation tools in camera view: Dolly (camera / target / both), Truck, Orbit, Pan Camera, Roll, Field of View, Perspective; button strip at the bottom right
  - [ ] Target camera: drag from camera position to target; target is an empty with a Track To constraint
  - [ ] Vertical tilt correction (2-point perspective) through lens shift
  - [ ] Max's 45° default viewport field of view (lens 43.5 mm); larger far clip for cm archviz scenes
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
- [ ] Border and Element as real select modes in the core
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
- [ ] Decide: Max-style caddy (an add-on popup at the mouse with OK / Apply and Continue / Cancel)
  or Blender's Adjust Last Operation panel
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
- [ ] **Fix Cap** (Seb, 2026-10-25): `maximize.cap` runs Blender's Fill (`mesh.fill`), which fills
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
- [ ] Still without a Max button: Material IDs select by name, Slice Plane, Insert Vertex, edge
  Crease / Weight, vertex Crease
- [ ] Missing, to build (Seb, 2026-10-25; Outline done): Max-style edge / border / vertex
  Extrude (Height and Width), Extrude Along Spline, Slice Plane's Split and Reset Plane, Named Selections Copy / Paste,
  Material ID Clear Selection, Show Cage (with its two colors), Hinge From Edge (low priority);
  Apply and Continue for Blender's Adjust Last Operation panel
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
### Sculpt modifier (Seb's decision, 2026-10-25; after Phase 3b)

One **Sculpt** modifier that unifies Blender's Multires modifier and the sculpt brush settings,
modeled on 3ds Max's Retopology modifier: it can sit mid-stack, with limitations.
- [ ] The modifier panel holds both the Multires controls (levels for viewport / sculpt / render,
  Subdivide, Simple, Linear, Unsubdivide, Delete Higher, Apply Base, Rebuild Subdivisions) and the
  brush settings (brush, radius, strength, falloff, symmetry, Dyntopo), so sculpting is set up
  in one place. Selecting it and entering its level starts Sculpt Mode on it.
- [ ] **Dyntopo on** applies the current subdivisions first (bakes the Multires levels into the mesh),
  then sculpts with dynamic topology. Ask before applying (it can't keep the levels).
- [ ] **Mid-stack:** allowed, with a warning symbol next to the modifier in the stack list
  (tooltip says why: what's below must keep its topology; Dyntopo and remesh are off there).
  Sculpt edits are stored as per-vertex offsets (like Edit Poly's Deform mode) on the stack below.
- [ ] Limitations to spell out, as in Max's Retopology: a topology change below invalidates the
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
- [x] Line tool: click for corner, drag for Bezier, with grid snapping (Add > Shapes > Line). AutoGrid (on surfaces) open
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
  convertible); new ones are Bezier. Egg is not built yet.*
- [~] **Interpolation as in Max**: Steps per shape (default 6 = Blender resolution 7) done.
  Optimize: core flag `CU_OPTIMIZE` / `Curve.use_optimize` (`curve_legacy_convert.cc` turns
  segments whose handles lie on the chord into vector segments, so they evaluate to their end points),
  on for new shapes; written, waiting for the rebuild. *Files: a new bit in `Curve.flag`; stock
  Blender ignores it and draws straight segments with Steps points, so the shape looks the same.*
  Adaptive: open (Blender has one resolution per curve, not per segment).
- [x] **Max vertex types** (done 2026-10-25, `spline_tools.py`; Edit Spline quad menu and the
  Max Spline Tools menu; the Modify tab entry comes with Phase 6) in the quad menu and the Modify tab: Corner, Smooth, Bezier, Bezier
  Corner (Blender's Vector, Auto, Aligned, Free handles), Reset Tangents, Make First, Reverse.
  *Files: unaffected (Blender's own handle types).*
- [~] **Editable Spline levels 1 Vertex, 2 Segment, 3 Spline** (done 2026-10-25, `spline_tools.py`):
  a click at 2/3 picks a whole segment or spline (Ctrl adds, Alt removes), transforms of the picked
  vertices, Delete per level, Divide, Detach, Explode, Close, Mirror, Weld (joins or closes
  splines), Fuse, Attach (object level), Reset Tangents / Make First / Reverse, Trim / Extend /
  Fillet / Chamfer / Outline / Break / Connect; in the Edit Spline quad and the Modify tab
  (Rendering, Interpolation, Selection, Geometry rollouts). Pressing 1/2/3 on a parametric shape
  converts it first. **Open:** Cross Insert, Bind/Unbind, Show Selected Segments (Blender draws
  selected points, not segments in red), Lock Handles Alike/All, and a hover highlight for segments.
- [~] **Creation as in Max** (done 2026-10-25): Line with Initial Type (Corner/Smooth) and Drag
  Type (Corner/Smooth/Bezier), Backspace removes the last vertex, Shift for 90 degrees, clicking
  the first vertex asks "Close spline?", Start New Shape off adds to the selected shape; Keyboard
  Entry for every primitive and shape; AutoGrid (Create menus; surface under the mouse); Text
  (Blender's text object), Freehand (Blender's Draw tool on a new shape), Section (plane through
  the 3D cursor cuts the selected meshes). Egg (done, measured).
  **Open:** Section as a live, movable plane object (today one cut at the cursor).
- [x] **Rendering as in Max** (done 2026-10-25, `spline_render.py`): Enable In Renderer / In
  Viewport, Radial (Thickness, Sides, Angle) and Rectangular (Length, Width, Angle), Auto Smooth with
  threshold, Generate Mapping Coords, for shapes and editable splines, as a "Rendering" Geometry
  Nodes modifier. *Files: a normal Geometry Nodes modifier; stock Blender renders it the same.*
- [~] **Edit Spline modifier**: stage 0 done in Maximize (2026-10-25, `edit_spline.py`): edits
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
  - [ ] Stage 2: edit on the object itself in Edit Mode (no stand-in object), as Edit Poly's
    session does
  - [ ] Stage 3 rest: migrate stage-0 (Geometry Nodes) Edit Spline setups to the native modifier
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
- [ ] Not in the 3b list yet: Create Line, Insert, Cycle, Hide / Unhide All, Attach Mult., Cross
  Section, Area Selection, Segment End, Select By, Named Selections Copy / Paste, Show Vertex
  Numbers, Connect Copy, Reorient, Tangent Copy / Paste, Detach's Same Shp / Reorient / Copy options, Explode's To Splines / Objects choice
  (check what the 3b Detach and Explode already do). Soft Selection is Blender's proportional editing.

## Phase 4 — Core gaps no add-on can fill

Smallest first. Three of them turned out to be possible in Maximize after all (marked).
- [x] **Imperial fractions**: unit display and parsing (`blenkernel/intern/unit.cc`), Scene > Units > Fractional Inches
- [x] **Freeze**: objects with selection disabled draw gray (workbench); Freeze Selection / Unfreeze All in the quad menu; the Outliner's selectable column is the Freeze column
- [x] **Smoothing groups** *(Maximize, `smoothing.py`)*: face attribute `smoothing_groups`, the 32-button panel, Auto Smooth, Select By SG, Groups From Sharp Edges; sharp edges follow the groups, FBX writes them as smoothing groups
- [x] **Instance vs Reference** *(Maximize)*: instances and references share the mesh and the original's modifier stack (a Shared Stack Geometry Nodes modifier); Make Unique. Open: modifiers added to an instance don't reach the original
- [x] **Modifier gizmos** *(Maximize, `modifier_gizmos.py`)*: Simple Deform (Bend, Twist, Taper, Stretch) dial and arrow; FFD stays Blender's Lattice
- [x] **Performance**: profile a 10k-object scene (Outliner, undo, selection): `moritz/docs/performance.md`
- [x] Undo hotspot: keep the depsgraph relations when an undo step changed none (800 ms -> 85 ms at 10k objects; `memfile_undo.cc`, `test_undo_relations.py`)
- [x] Whole-window redraw at 10k objects measured per region (see `docs/performance.md`): the Outliner tree rebuild is half of it and only runs on structural changes; no change needed
- [ ] Scene fingerprint so undo/redo pairs also keep relations (blocked: the depsgraph keys the master collection by its address, which changes when the scene is re-read)

## Phase 5 — Pipeline and release

- [x] Max scene exchange without a closed-format parser: Max writes the scene with `maximize/max_side/moritz_export.ms`, Maximize imports it (File > Import > Max Scene (.mxscene), `max_scene.py`): polygons, UVs, Multi/Sub IDs, smoothing groups, hierarchy, pivots, units, layers, frozen/hidden, cameras, lights; `tests/test_max_scene.py` (tested with 3ds Max 2026 on the same kitchen: 33 objects, 228k vertices, textures, in 3.7 s; `3dsmaxbatch.exe moritz_export.ms -sceneFile x.max` with `MORITZ_EXPORT_PATH` exports without a dialog)
- [x] V-Ray/Corona/Physical/Standard → Principled converter (`max_materials.py`), used by the import
- [x] License check of the direct `.max` importer: "Import Autodesk MAX (.max)" 1.9.2 (extensions.blender.org/add-ons/io-scene-max, Sebastian Sille et al.) is GPL-3.0-or-later, compatible with Moritz; imports meshes, UVs and Standard/Physical/V-Ray/Corona materials, Blender 4.2+
- [x] Bundled unmodified in `release/extensions/system/io_scene_max` (the System extensions repository), enabled by default (File > Import > Autodesk MAX (.max)); tested on a real 33 MB kitchen scene: 22 meshes, 233k vertices in 10 s; Physical material textures fail inside the extension (upstream bug), so the exporter route stays the better one when Max is at hand
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

- [ ] **Rename the Properties editor to "Command Panel"** (editor type menu, header, tooltips,
  manual links). Only the label changes: `SpaceProperties` and the Python type `'PROPERTIES'` stay,
  so scripts and add-ons that look for it keep working. *Files: UI only, unaffected.*
- [ ] **Rename the Modifiers tab to "Modify"** (label and tooltip of `BCONTEXT_MODIFIER`). *Files:
  UI only, unaffected.*
- [ ] **Modify tab as in Max**: the Max-style stack list on top (newest modifier first, base object
  at the bottom, on/off toggles, Edit Poly rows expand into the five sub-object levels, click to
  make a level active, reorder), the selected modifier's settings below; Blender's full modifier
  panels stay available underneath. *Files: UI only, unaffected.*

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
- [x] Stage 1, Python (`bl_ui/properties_data_modifier.py`, committed d71c9ca72de; reviewed
  by the main session): list newest first, on/off toggle, base object row, Edit Poly levels below
  the list. Blender's modifier panels stay below.
- [ ] Stage 2, Python: expandable sub-object levels per row, level icon, italic instances, warning
  symbol, right-click menu, the button row, Delete key, modifier clipboard (Copy / Paste; Blender
  only has Copy to Selected)
- [ ] Paste Instanced: modifiers shared between objects (one modifier's settings drive all its
  instances, kept in sync by Maximize like the shared Edit Poly on instances; *files: plain
  modifiers, stock Blender sees independent copies*)
- [ ] Stage 3: only the selected modifier's settings. Python-only route: collapse the other
  modifier panels (`show_expanded`) when one is selected; core route: an `active_only` option for
  `template_modifiers`. Decide which.
- [ ] Stage 4: the flat Add Modifier menu (all modifiers at once, incompatible ones left out, type
  to filter)
- [ ] Drag to reorder: Blender's UI lists can't drag rows; needs a small core change (or Move Up /
  Down buttons and Ctrl+Up / Down until then). Warn before the core change.
- *Files: UI only. The only stored values are the modifiers' own expand flags (`show_expanded`) and
  their order, which stock Blender reads the same way.*
- [ ] **New "Create" tab** (new `BCONTEXT_CREATE`, first in the tab column, shown with or without
  a selected object), Max's categories: Geometry, Shapes, Lights, Cameras, Helpers, Space Warps,
  Systems; "Object Type" buttons and Name and Color, as in Max. All parametric objects live here:
  the editable primitives (Box, Sphere, Cylinder, Cone, Tube, Torus, Plane), the parametric shapes
  (Rectangle, Circle, Ellipse, Arc, NGon, Star, Helix, Donut, Line), Loft, lights, cameras,
  empties. *Files: the open tab is saved as a number (`SpaceProperties.mainb`); stock Blender does
  not know the new one and falls back to the Object tab (`buttons_context.cc`), so nothing breaks
  in either direction. Objects made here are ordinary Blender objects (the parametric ones are
  Geometry Nodes modifiers, which stock Blender evaluates).*
- [ ] Move Maximize's sidebar Create and Modify panels (Max tab) into the Command Panel tabs; keep
  the sidebar Max tab for the other tools
- [ ] Without Maximize, the Create tab offers Blender's own primitives (not parametric after the
  first redo); with it, the parametric ones
- [ ] Docs: `max_users.md` (Command Panel, Create, Modify), PATCHES.md, tests for the tab order and
  the renamed labels

## Phase 7 — Outliner with Max's Scene Explorer features (plan, 2026-10-25)

Rule: only what Max does better. Kept from Blender: the Outliner itself, collections as layers
(active collection = Max's current layer), search, sync selection, drag and drop to parent, batch
rename (Ctrl+F2, Max's Rename Objects), F2 rename (done).

No-brainers (approved by Seb, 2026-10-25):
- [ ] **Freeze column** with Max's snowflake icon and name (today the selectable column does the job;
  done in Phase 4). *UI only.*
- [ ] **Type filter row in the header**, as Max's Scene Explorer toolbar: one click per Geometry,
  Shapes, Lights, Cameras, Helpers, Space Warps, Bones, instead of Blender's filter popover. Python
  (`space_outliner.py`); needs Shapes split out of "Others" (curves, text) — small core change for a
  new filter flag. *Files: a new bit in the Outliner's filter flags; stock ignores it.*
- [ ] **Display as Box** and **See-Through** columns (per object: `display_type = 'BOUNDS'`, and
  X-ray per object), as in Max; core (Outliner columns are C). *Files: the columns' on/off flags
  are new bits in the Outliner space, stock ignores them; the object values are stock data.*
- [ ] **Renderable** column under Max's name (Blender's render column, relabeled). *UI only.*
- [ ] **Double-click an object selects it and its children** (Max), as in the viewport; rename stays
  on F2 and Ctrl+click. Python keymap. *UI only.*
- [ ] **Unhide All / Unfreeze All** in the Outliner's context menu and header. *UI only.*
- [ ] **Layer properties by layer**: Max's "By Layer" for color, freeze and render; Blender's
  collection color tags drive the object color in the viewport. Medium; check first.
- Maybe, not no-brainers: Selection Sets as an Outliner view (Maximize's named sets), sorting by
  column (Blender sorts by name only), Max's separate Layer Explorer (Blender's View Layer mode
  already shows collections).

## Upstream maintenance (recurring)
- [ ] Merge each Blender release branch into `moritz/main` (last: 31 fixes from `blender-v5.3-release`, 2026-10-25, no conflicts, tests pass)
- [ ] Re-run the test suite and a smoke test of Maximize after each merge
