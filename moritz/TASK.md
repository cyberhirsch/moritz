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
- ~~**Repos stay private.**~~ **Both repos are public** (Seb, 2026-10-31; checked without login:
  `cyberhirsch/moritz` and `cyberhirsch/maximize` answer 200). GitHub's hosted runners are free
  for them, macOS included.
- **Moritz 0.3.0 ships for Windows, Linux and macOS** (Seb, 2026-10-31). See Phase 5.
- **Phase 3b:** do every item in order, then report.

- *(2026-10-29)* **Moritz is a Blender alternative, not Blender plus an add-on.** Seb: "moritz
  should not feel like a blender alternative that ships with an addon. it should just feel like a
  blender alternative." *(Sidebar tab done 2026-10-30, Maximize 00a6b13: all 8 "Max" panels poll
  False in Moritz, test `test_no_max_tab.py`; stack, Material IDs and Smoothing live in the Modify
  tab, selection sets and keymap in the header Max menu, quad menu and Preferences. Open: the
  header menu is still called "Max", which also reads like an add-on.)* **(Seb, 2026-10-30: the
  whole header Max menu appears only in Maximize on stock Blender, never in Moritz.** Its entries
  go into Blender's normal menus in Moritz (Object, Edit, Select, Mesh, View …), the quad menu and
  Preferences; Max-named aliases stay findable through F3 search and the name scheme. Same rule
  for anything else that shows the add-on: in Moritz, everything Max-related reads as built in.)*
  - [x] *(Done 2026-10-30, Moritz 435a44d3c56: see the Done note below; no rebuild was needed.)*
    *(Seb, 2026-10-30: "yes, plan it")* **Maximize out of Preferences > Add-ons in Moritz**,
    with the next core batch (**rebuild**). Options: (a) ship Maximize's code as a built-in part
    of Moritz (a startup module, always on, settings in Preferences under its own section, no
    add-on entry); (b) keep it an add-on but have Moritz's add-on list hide it and refuse to
    disable it. (a) fits "a Blender alternative, not Blender plus an add-on" best; Maximize stays a
    separate add-on for stock Blender. Check: updates of Maximize must still reach Moritz, and
    files saved with it must still open in stock Blender (with or without Maximize).
  *(Done 2026-10-30, Maximize: no header Max menu in Moritz. Its entries: Create/Shapes in Add,
  modifiers in Add Modifier, Chamfer/Connect in Mesh > Vertices and Edges, Delete Sub-Objects in
  Mesh > Delete, Type-In and the pivot tools in Object > Transform, Reset XForm in Object > Apply,
  Align/Array/Spacing/Clone in Object, Select by Name and Named Selection Sets in Select, Maximize
  Viewport/Camera from View in View, Render Setup/Material Editor in Render, keymap in
  Preferences. The aliases the name scheme doesn't already give show in the menu of the operator
  they call, with Max or Moritz names only. Also: "Freeform (Max)"/"Sculpt (Max)" are "Freeform"
  and "Sculpt" in Add Modifier, "Max Spline Tools" is "Spline Tools", the new-file layout no
  longer opens the sidebar on a Max tab, and its preference is "Quad View Layout for New Files".
  Test `test_no_max_tab.py`. Still an add-on: Maximize is listed in Preferences > Add-ons; making
  it a built-in part needs core changes.)*
  **(Seb, 2026-10-30: Maximize must not appear in Preferences > Add-ons in Moritz either.)**
  Done 2026-10-30 in Moritz's Python scripts (no compile; the next build installs them, until
  then they are copied into the build's `5.3/scripts` by hand). Built in for the user, still an
  add-on package underneath:
  - [x] **Shipped with Moritz:** the zip and the MSI copy Maximize into `scripts/addons_core`
    (as before). A development build finds it in the user's add-ons, where Seb's is a link to the
    Maximize repository, so every Maximize change reaches it at once. (A CMake install was dropped:
    its copy would have hidden that link until the next build.)
  - [x] **Always on:** `addon_utils.BUILTIN`; `_enable_builtin()` turns it on at startup and on
    script reload, also with factory settings. `addon_utils.disable(..., default_set=True)` (the
    Preferences checkbox) refuses it; a script reload still unloads and reloads it.
  - [x] **Not in the Add-ons list:** both list implementations (`bl_pkg` and the legacy
    `USERPREF_PT_addons`) and the workspace add-on filter skip it.
  - [x] **Its settings in Moritz's own Preferences:** name scheme in Keymap (as before); Tool
    Settings (Caddy), Hover Highlight and Quad View Layout for New Files in Interface > Editors; the
    cage colors in Viewport > Display. Still stored as the add-on's preferences in
    `userpref.blend`, so nothing migrates.
  - [x] **Checks:** files open in stock Blender as before (the add-on still writes plain Blender
    data, nothing in files changed); Maximize on stock Blender is unchanged (it is the same
    folder). Test `moritz/tests/test_maximize_builtin.py`; all 61 test scripts pass (three Moritz
    tests now unload Maximize by script to check Moritz without it).
  - Rejected: turning Maximize into a startup module (option a in its pure form). That would
    mean rewriting its `AddonPreferences`, every `get_prefs` call and the two core readers, and
    keeping two variants of the code apart, for no difference the user can see.
  In Moritz there is **no "Max" sidebar tab**; it stays only in Maximize on
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

- *(Seb, 2026-10-30, screenshot of the Modify tab on an Editable Poly base object)* **Editable
  Poly gets every option of Edit Poly.** Today the base object (no Edit Poly modifier) shows only
  Selection and Paint Deform. As in Max, it shows the same rollouts as the Edit Poly modifier
  (Soft Selection, Edit Geometry, the per-level Edit Vertices / Edges / Borders / Polygons /
  Elements, Loops, Polygon: Material IDs and Smoothing Groups, Subdivision …), working directly on
  the mesh. *(Done 2026-10-30, Maximize: the base and the modifier already drew the same rollouts
  (one function), but in Object Mode both showed only Selection and Paint Deform. Now, as in Max:
  Selection, Soft Selection (new: Blender's proportional editing in Max's words), Edit Geometry
  (in Object Mode Attach, the sub-object tools greyed until a level is picked), then in Edit Mode
  the level's Edit rollout, Loops, Material IDs and Smoothing Groups, and Paint Deform last.)*

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
- [x] *(Seb, 2026-10-30: "there is still a lot of references to blender", "version number bottom
  left / right")* **Second rebrand sweep; the first check missed some.** The status-bar version at
  the bottom right shows "5.3.0 b" (Seb's screenshot; the icon left of it is the offline icon, not
  a logo, and stays): show "Moritz 0.1 Alpha" there instead, with Blender's
  version only in About ("Based on Blender 5.3"). Then grep every user-visible string for "Blender"
  (status bar, tooltips, menu labels such as "Blender Preferences", "Quit Blender", "Save Blender
  File", operator descriptions, error and report messages, the Help menu, the File Browser, the
  installer/MSI texts) and change them to Moritz. Keep as they are: links to Blender's own manual
  and website (named as Blender's), "Based on Blender", the license texts, and anything internal
  (`bpy`, `.blend`, the file header). *Warning: the `.blend` extension and the `BLENDER` file header
  must stay so files open in stock Blender. Changing translated strings means updating the `.po`
  files too. Core change, needs a rebuild.*
  Done: status bar shows "Moritz 0.1 Alpha" (`info_stats.cc`); ~90 strings in 47 files (RNA,
  editors, window manager, Python UI: "Save File", ".blend file", "world units", app references
  → Moritz); the same msgids in 42 `locale/po` files; installer progress text and the Windows
  batch messages. Built, suite 64/64.

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
- [x] *(points 1, 2, 4 and 5 done 2026-10-29, Maximize `quad_menu.py`: flat text rows without
  icons, emboss off; thin lines between groups; the text faces the cursor (row alignment, so
  point 1 needed no core change); a settings square at the outer edge for Extrude, Bevel,
  Chamfer, Inset, Connect, Weld and Bridge when the caddy is on; Convert To as a submenu; the
  current sub-object level framed (a checkmark squeezed the short labels; pressed-in buttons move
  the popover's anchor); unavailable entries gray out through their polls. Test: Maximize
  `tests/test_quad_menu.py`. Point 3 continues below.)* *(Seb, 2026-10-29, from a screenshot of
  Max 2026's quad menu: "looks a little better than what we have")* **Quad menu closer to Max's
  look:**
  1. **Text faces the cursor:** left quadrants right-aligned, right quadrants left-aligned.
     *Possibly core:* Python can't right-align a button's own text.
  2. **Flat menu rows**, not buttons: compact, no icons, thin separators between groups; only the
     small settings box at the outer edge (Extrude ▢, Move ▢) for the caddy / redo panel.
  3. **Quadrant names in the middle** as a dark band (tools 1 / tools 2 left, display / transform
     right), with the four small squares at the center. *Possibly core:* needs custom drawing.
  4. **Submenus with ▸** (Convert To, Viewport Lighting and Shadows) instead of long lists.
  5. **Checkmark on the current level** (Polygon ✓) and **grayed-out entries** when not
     available, so the layout doesn't jump.
  Points 2, 4 and 5 should work in Python (`quad_menu.py`). A pixel-exact look probably needs a
  small core menu type and a **rebuild**; batch it with the other core changes.
- [x] *(done 2026-10-29 in Python after all, Maximize `quad_menu.py`: the quadrant titles are
  boxed rows meeting at the cursor, a band through the middle; the quadrants lost their own boxes
  so the band stands out. Left out: Max's four small squares at the center, cosmetic)* **Quad
  menu, point 3:** the quadrant names as a dark band through the middle with Max's four small
  squares at the center.
- [x] **Viewport navigation**: MMB pan, Alt+MMB orbit, Ctrl+Alt+MMB zoom; orbit around the selection and zoom about the mouse are set on first enable
- [x] **Max layout for new files** (`viewport.py`, load_post handler): quad view, centimeters, sidebar on the Max tab (preference "Max Layout for New Files"). Done in the add-on instead of an app template.
- [x] **Max English** (`vocabulary.py`): about 40 Blender labels renamed (Merge by Distance → Weld, Bevel → Chamfer, Join → Attach…), preference "Max English", default on
- [x] *(table grown 2026-10-29 from 41 to 61 names, Maximize bf40154)* *(done 2026-10-29, Maximize `vocabulary.py`: preference Names = Follow Keymap / Blender / Max /
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
  its Max key)* *(Seb, 2026-10-30: **Tab toggles Object / Edit Mode in both keymaps**, Max and
  Moritz, in both directions. Moritz keymap verified 2026-10-30, Maximize ecc6f92,
  `test_tab_toggle.py`; in the Max keymap Tab was Search (from Industry Compatible), so Search
  moves to X there too, as in Moritz. Done 2026-10-30, Maximize 0146472 / Moritz af16c67fd28: the
  binding is in the shared part of the keymap; `test_tab_toggle.py` passes in both keymaps,
  including after 1-6 and with Edit Poly.)* *(Seb, 2026-10-30: **Moritz starts with the Moritz keymap as
  default**: factory settings, a fresh install and the Quick Setup preselect Moritz. TASK.md
  already said "Moritz is the default", but Seb's Moritz was on Max; check whether the default
  really applies or whether only his saved preferences hold Max. Checked 2026-10-30: factory
  settings start with Moritz (also in a GUI start; the Quick Setup preselects the active keymap,
  and Maximize's first-run setup activates Moritz). Seb's saved userpref.blend holds Max; switch
  in Preferences > Keymap or the Quick Setup. Nothing to fix.)* *(Seb, 2026-10-29)* **Moritz keymap only** (not the Max one):
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
  - [x] **Bug** *(Seb, 2026-10-30: "that seems to work, but when i release it snaps back to the
    before state")*: Shift+drag of polygons shows the preview extrusion while dragging, but on
    release the mesh returns to how it was before. Release path: `_watch_drag` in `smart_extrude.py`
    restores the mesh (`ed.undo` + `before`) and then runs `maximize.smart_extrude(offset=…)`.
    Either that operator cancels or makes no change, the undo takes away more than the Move, or the
    timer never fires (for example if `window.modal_operators` still lists a transform). Reproduce
    in the GUI with the Moritz and the Max keymap, with and without the gizmo. *Fixed 2026-10-30,
    Maximize 72c2e6b, test `test_smart_extrude_drag.py`.*
  - [x] *(Seb, 2026-10-30: "yes ring too, and when using the arrows it should extrude in that
    direction")* **The gizmo's center ring extrudes too:** Shift+drag on the free-move ring
    ("Generic Gizmo" PRESS keymap) runs Smart Extrude like a drag on the polygon. **On an arrow, it
    extrudes along that arrow's axis** in the current Transform Orientation (Normal, Local,
    Global …), not along the polygon normal. Check that the arrow constraint survives the switch
    from the preview Move to Smart Extrude (`offset` is already the move vector; the walls should
    follow it).
    *Done 2026-10-30:* the ring already ran Smart Extrude (the earlier "not covered" came from a
    test that lost Shift). On an arrow, Blender's gizmo turns Shift into a move in the plane across
    the arrow (`transform_gizmo_3d.cc`), so the extrusion went sideways: `gizmo_arrow_move`
    (`transform.py`, Maximize 3419ab0) now starts the Move along the grabbed arrow itself; Clone with Shift+drag on
    an arrow gets the same. A plain Smart Extrude now leaves only the cap selected, as in Max, not
    the new walls. Test: tilted cube, Global, arrow off the normal: the extrusion goes along the
    arrow (dir · axis 1.0, dir · normal 0.94); face drag, ring and arrow pass in both keymaps;
    `test_clone_gizmo_arrow.py`: the clone goes along the X arrow.
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
- [x] *(done 2026-10-29, Maximize 35d622e: Pick is an object field with the eyedropper, the
  brushes then work on that object only; Mirror X / Y / Z in the object's own axes; Defaults is
  Blender's preset menu with Fine / Medium / Broad and Add / Remove. The `ff_*` / `pd_*` icons
  wait for the icon decision below)* **Freeform, still open:** Paint Deform's Pick (lock an object), brush presets (Max's
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
- [x] 0.2 release (Seb, 2026-10-25: the first release is Moritz 0.2, on Blender 5.3). *Released 2026-10-30 as 0.2.0 (Seb: "build a 0.2.0 and release on github"): tag `v0.2.0` on c680148f01b (Maximize tag `v0.2.0` on 3419ab0), private GitHub pre-release https://github.com/cyberhirsch/moritz/releases/tag/v0.2.0 with the zip and msi (also in `G:/Code/Moritz/dist/0.2.0`); suite 65/65, both packages smoke-tested. The hand tests in `moritz/docs/release_0.2_checklist.md` were not done before the release.*

- *(Seb, 2026-10-31: no 0.2.1; the MCP server, CLI, per-user installer and the rest ship with
  0.3.0.)*
- *(Seb, 2026-10-31: "when everything is done release 0.3". This is the go for the release
  workflow runs, the CI dispatch included, once the open items are done: the updater, quad cap
  relax, and anything else open and requested. Release as a pre-release like 0.2.0, macOS
  unsigned with the note. Re-run a failed job as needed. Report the release URL.)*
- [ ] **0.3.0 on Windows, Linux and macOS** (Seb, 2026-10-31: "0.3.0 should be linux, windows
  and mac"). The repos are public, so GitHub's hosted runners are free.
  - **Workflow:** one `workflow_dispatch` workflow with a matrix:
    - Windows: `windows-latest`, as now.
    - Linux x64: `ubuntu-latest` inside Blender's Rocky Linux 8 build image, for glibc
      compatibility.
    - macOS arm64: `macos-14`.
    - macOS x64: `macos-13`, if Intel is wanted.
    Each job downloads Blender's precompiled libraries for its platform (Blender's `make update`
    lib checkout for 5.3) and clones Maximize. A compiler cache (sccache or ccache with
    `actions/cache`) keeps reruns inside the 6 h / ~14 GB limits. Run Maximize's headless tests on
    every platform.
  - **Packages:**
    - Windows: zip and per-user MSI.
    - Linux: `moritz-0.3.0-linux-x64.tar.xz`.
    - macOS: `.dmg` with `Moritz.app`.
  - **Untested platform code:** `GHOST_SystemPathsUnix.cc` and `GHOST_SystemPathsCocoa.mm`
    (config in `~/.config/moritz`, `~/Library/Application Support/Moritz`), the app bundle name,
    `Info.plist` (bundle id, icon `.icns`), the Linux `.desktop` file and icons, and `moritz-cli`
    on both.
  - **macOS signing:** without an Apple Developer account (99 USD a year) the app is only ad-hoc
    signed and not notarized. Gatekeeper then calls it "damaged"; users must run
    `xattr -cr Moritz.app` or open it with right-click > Open. Seb decides whether to get an
    account; until then, ship unsigned with that note in the release text.
  - **Release:** one GitHub release with all packages. *Starting the workflow is a CI run: ask
    Seb before each dispatch, as per the CI rule.*
  **Prepared 2026-10-31, not run (needs Seb's go):** workflow `.github/workflows/moritz-release.yml` (Windows zip+MSI+.mcpb, Linux in a rockylinux:8 container, macOS arm64 on macos-14, ccache, headless tests via `moritz/tools/run_headless_tests.py`, optional draft release). Packaging `moritz/tools/make_unix_package.py` (tar.xz; .dmg with ad-hoc signature). Rebrand for Linux/macOS: program `moritz` / `Moritz.app` (`Moritz`), Info.plist (id `io.github.cyberhirsch.moritz`, Moritz icon `.icns`, .blend files stay Blender's: LSHandlerRank Alternate, imported type), `moritz.desktop` + icons, Wayland app id / X11 class "Moritz", macOS app menu, `moritz-cli` shell launcher. **No Intel Mac:** Blender 5.3 has no `macos_x64` libraries. No GPU kernels on hosted runners (Cycles CPU, or kernels compiled on the user's machine). Nothing of it has been compiled yet: Linux and macOS only build in CI. Risk: the Linux job may run out of the runner's ~14 GB disk.

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
  - [x] *(done 2026-10-29, Maximize `max_modifiers.py`, a Geometry Nodes modifier: Mode Extrude /
    Bevel / Profile; Amount and Segments; Start Outline and three levels of Height and Outline,
    mitered at corners; a picked Profile shape; Cap Start / End, Flip Normals, Smooth; outward
    whichever way the shape was drawn. Test: `tests/test_max_modifiers.py`)* **Extrude, Bevel, Bevel Profile become one modifier:** Extrude with three buttons on top
    (Extrude / Bevel / Profile), like Simple Deform's mode buttons.
  - [x] *(done 2026-10-29, native in Moritz, `modifiers/intern/MOD_max_mesh.cc`; stock Blender keeps it as a disabled "None" modifier and Moritz revives it with its settings. Test: `moritz/tests/test_max_mesh_native.py`, with a round trip through stock Blender 5.2: Quad Cap fills each hole with a quad grid, odd
    borders too; off, one polygon per hole; Smooth)* **Cap Holes:** Max version, with a quad cap
    option (like Edit Poly's Cap).
  - **Conform:** keep Blender's Shrinkwrap as it is.
  - [x] *(done 2026-10-29, Maximize 8001202: Explode in Edit Geometry > Geometry (All), to Objects
    or to Elements by Angle, on the selected polygons or all; Show Normals and Scale in Edit
    Geometry)* **Edit Mesh → Mix:** Edit Poly needs Edit Mesh's **Explode** feature, and maybe a **Show
    Normals** display option.
  - **Lathe:** Seb finds "Screw" a bad name. Blender's Screw modifier does make real screws
    (Screw offset + iterations give threads and springs), so **both**: Lathe (no offset) and Screw
    (with offset), one Blender modifier underneath. **Corrected (Seb, 2026-10-29): keep the Screw
    modifier as it is**, one entry. Only the name scheme changes it: in the Max scheme it
    displays as **Lathe**, in the Blender scheme as Screw.
  - [x] *(Noise done: Seed, Scale, Fractal with Roughness and Iterations, Strength X / Y / Z,
    Animate Noise with Frequency and Phase. Normal done with Flip; Unify and Flip natively since 2026-10-29 (MAX_NORMAL, in the
    native batch; in Moritz the list uses the native one))* **Noise → Max**, **Normal → Max** (own modifiers, not only Blender's under a Max name).
  - [x] *(phase 2 done 2026-10-29: UV seams, material boundaries and hard edges stay in place
    but thin out along their length, held by planes like open borders, instead of frozen;
    Favor Compact Faces (on by default) adds a triangle-quality cost; Prevent Flips was already
    in Blender's collapse. Core: `BM_mesh_decimate_collapse_ex` in `bmesh_decimate_collapse.cc`,
    Blender's Decimate unchanged. Measured 2.5–4.2 s on 261k triangles, so Max's "Calculate
    once, then an instant slider" is not matched: continuing from the last result would make the
    output depend on slider history; a true progressive-mesh cache is a separate item below.
    Test: `test_max_mesh_native.py`, boundary 21 → 12 vertices at 0.0 offset, mean triangle
    quality 0.794 → 0.813)* **ProOptimizer:** Max's algorithm is better; try to match it
    (Decimate underneath isn't enough).
  - [x] *(Done 2026-10-30: over 20000 faces, the collapse order is recorded once down to 1%,
    keyed by object and modifier and invalidated by a hash of the input mesh and the settings;
    each Vertex % replays a prefix (`BM_mesh_decimate_collapse_record` / `_replay` in
    `bmesh_decimate_collapse.cc`). A change of % takes 0.08–0.11 s on 24576 faces; the result
    matches a direct run (`MORITZ_PRO_OPTIMIZER_NO_CACHE`) in face count and surface error.
    Blender's decimation itself is not bit-reproducible: stock Decimate flips between two results a
    face apart, even within one process. Test `moritz/tests/test_pro_optimizer_replay.py`.)*
    **ProOptimizer instant slider:** record the full collapse order once (progressive mesh),
    keyed by the input, and replay a prefix for each Vertex %, attributes included. Only worth
    it for meshes over ~100k triangles; deterministic, unlike reusing the last result. *(2026-10-29: phase 1 done, native in Moritz, `modifiers/intern/MOD_max_mesh.cc`; stock Blender keeps it as a disabled "None" modifier and Moritz revives it with its settings. Test: `moritz/tests/test_max_mesh_native.py`, with a round trip through stock Blender 5.2: Vertex %, Protect Borders, Keep
    Material / UV Boundaries, Keep Normals, Symmetry. The Max match is phase 2 in
    `moritz/docs/max_mesh_modifiers_design.md`: attribute-aware quadrics, Favor Compact Faces,
    Prevent Flips, and a precomputed collapse order so the slider is instant.)*
  - [x] *(done 2026-10-29, native RETOPOLOGY modifier in `MOD_max_mesh.cc`: cleanup (weld, loose,
    degenerate; a voxel pass when non-manifold, where QuadriFlow alone fails), Symmetry X / Y / Z
    (one half solved, conformed, then mirrored, exactly symmetric), Face Count, Auto Edge (sharp
    edges), Preserve Boundary, Conform onto the original with Relax passes, Seed. The Max list's
    Retopology entry uses it. Test: `moritz/tests/test_retopology_native.py`. Not matched: Max's
    background job and guide edges from an Edit Poly selection; ReForm itself is unpublished)*
    **Retopology:** Max's algorithm is better; try to match it (Remesh isn't enough).
    *(2026-10-29: planned in `moritz/docs/max_mesh_modifiers_design.md`: a native RETOPOLOGY
    modifier with Max's pre-processing (cleanup to manifold), feature edges, symmetry, a Face
    Count target, Conform and Relax afterwards, and the solve in a background job. ReForm is
    unpublished: match its results on five test meshes, not its code.)*
  - [x] *(Quadify Mesh done 2026-10-29, native in Moritz, `modifiers/intern/MOD_max_mesh.cc`; stock Blender keeps it as a disabled "None" modifier and Moritz revives it with its settings. Test: `moritz/tests/test_max_mesh_native.py`, with a round trip through stock Blender 5.2: Quad Size % of the object, Preserve
    Sharp / Boundary, Seed; QuadriFlow underneath, so the input must be manifold. Unwrap UVW
    planned in `moritz/docs/max_mesh_modifiers_design.md`: the UVs stored in the stack, edited in
    Blender's UV Editor on a stand-in, Max's tool names in the Max scheme)* **Quadify Mesh** and
    **Unwrap UVW:** not later, plan them now (both native, rebuild).
  - [x] *(STL Check done: open edges, multiple edges and spikes marked with red tubes, and a
    warning in the modifier with the count. VertexPaint done 2026-10-29, native in Moritz, `modifiers/intern/MOD_max_mesh.cc`; stock Blender keeps it as a disabled "None" modifier and Moritz revives it with its settings. Test: `moritz/tests/test_max_mesh_native.py`, with a round trip through stock Blender 5.2;
    Maximize `vertex_paint.py`: Paint opens Vertex Paint on a stand-in with the stack's result,
    Done keeps the colors in the modifier, Cancel, Clear Colors. Test: Maximize
    `tests/test_vertex_paint.py`)* **STL Check → Max**, **VertexPaint → Max**.
  - [x] *(done 2026-10-29: Mesh Clean, native in Moritz, `modifiers/intern/MOD_max_mesh.cc`; stock Blender keeps it as a disabled "None" modifier and Moritz revives it with its settings. Test: `moritz/tests/test_max_mesh_native.py`, with a round trip through stock Blender 5.2: Weld with a distance, Remove
    Straight (two-edge vertices on a straight line, with an angle), Remove Loose, Remove
    Degenerate)* **Turn to Poly → Mix:** what Seb needs from it is removing vertices on straight
    edges that only have two edges. Proposal: a **mesh cleaning modifier** with that option (and
    others).
  - [x] *(done 2026-10-29, Maximize `camera_map.py`: Shader Editor > Add > Texture > Camera Map Per
    Pixel, or `maximize.camera_map_per_pixel`; a node group from the camera's object coordinates,
    with drivers for lens, sensor, shift and frame aspect. Rendered from the camera it gives back
    the image pixel for pixel: `tests/test_camera_map.py`)* **Camera Map (WSM) → Max:** what Seb needs is Max's **Camera Map Per Pixel** (a map, not a
    modifier, a 3ds Max plugin). Blender's shaders can do it with the Texture Coordinate node's
    Window / Camera output; plan it as a Moritz material map or node group.
- [x] *(done 2026-10-29, Moritz 11e6be316c3 `bl_operators/moritz_modifier_list.py`, Maximize
  066b560: Search... at the top of Add Modifier matches the Max name, the Blender name and keywords,
  shown grey on the right; in the Max and Moritz schemes the menu is Max's alphabetical list (Bend,
  Taper, Twist, Stretch are Simple Deform presets) and a new modifier gets the Max name. Test:
  Maximize `tests/test_modifier_list.py`)* *(Seb, 2026-10-29: "when we search in the modifier list for bend, can it show simple deform?")*
  **Search keywords for the Add Modifier filter.** Each entry matches its Max name, its Blender
  name and a few words for what it does. For example, "bend" finds Bend and Simple Deform (Simple
  Deform's keywords: bend, taper, twist, stretch), and "solidify" finds Shell in the Max scheme.
  This works in our own flat list; Blender's menu search only matches labels.
- [x] *(done 2026-10-29 in the modifier list: Skin = Armature, Lattice = Wireframe, FFD = Lattice,
  Smooth = Smooth by Angle; Blender's own become "Skin (Blender)" and "Smooth (Blender)". The
  translation can't do it alone: Smooth, Armature and Wireframe are also used elsewhere (shading,
  the object type, viewport shading). Core follow-up in the native batch below: a "Modifier"
  translation context for modifier type names, so the name scheme renames them everywhere they
  appear and nothing else)* *(2026-10-29)* **Name clashes** to label differently in the Max scheme: Skin (Max = Armature,
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
- [x] *(done 2026-10-29: the tab column starts Create, Modify, Utilities, then Blender's tabs;
  the three have teal icons of their own, `tab_create.svg`, `tab_modify.svg`, `tab_utilities.svg`.
  The new **Utilities** tab (`BCONTEXT_UTILITIES`, `bl_ui/properties_utilities.py`) holds Align
  with the pivot options, Array, Spacing Tool and Object Paint, drawn by Maximize; without
  Maximize it shows Set Origin, Apply Transforms and an Array modifier. Test:
  `moritz/tests/test_utilities_tab.py`)* *(Seb, 2026-10-29)*
  **Tab order and color:** Modify moves to second place, right under
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
- [x] *(Done 2026-10-30, Maximize 3d65d4d / Moritz ce41a7a0e6b: all types at once, a gap between
  the groups; the core's `subcategory_draw` hook is gone.)*
  *(Seb, 2026-10-30: "we don't need those sections, there is enough room for all buttons
  here")* **Drop the sub-category dropdown** (Standard Primitives / Extended Primitives /
  Compound Objects, and the same for Shapes). The Create tab shows **all object types of a
  category at once** in the two-column grid: Max needs the dropdown for its narrow panel, Moritz
  has the room. Keep Max's order (standard first, then extended, then compound); at most a thin
  separator between the groups, no headers or extra clicks.
- [x] *(Done 2026-10-30: Suzanne is its own button after Teapot (Create tab, Add > Standard
  Primitives), `maximize.add_suzanne`, a plain mesh dragged from the center, size baked into the
  mesh at scale 1, test `test_suzanne.py`. Teapot's own icon `MX_CR_TEAPOT` is in Moritz's icon
  set; it shows after the next rebuild, until then Teapot keeps the monkey.)*
  *(Seb, 2026-10-30: "teapot has a monkey face, please add both, susanne and utah teapot")*
  **Teapot and Suzanne as two buttons.** The Teapot button borrows Blender's monkey icon (`MONKEY`).
  Teapot gets its own teapot icon (new, in the approved icon style). Suzanne becomes its own button
  in Standard Primitives, right after Teapot, with the monkey icon. It adds Blender's monkey mesh
  (`primitive_monkey_add`), drag-created like the others, name Suzanne001 in the Max name scheme.
  *Icon is new art, add-on side; files unaffected.*
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
- [x] *(Seb, 2026-10-29: core. Done: the 69 icons are `release/datafiles/icons_svg/mx_*.svg`,
  `ICON_MX_*`, imported by `moritz/tools/import_icons.py` (CSS classes inlined, drawn on Blender's
  1600-unit canvas). Wired: 47 in Maximize, through `mx_icons.mx_icon()`, which falls back to the old
  icon in Blender builds without them; Show End Result and Make Unique under the stack. Not
  placed yet, no button for them: the four constraint icons, NURMS, Use Displacement, Soft
  Selection, Display as Box and See-Through. The Add Modifier list's add-on entries take no icon
  yet, so the MOD_ icons don't show there.)* After the OK: decide where they go. In Maximize as
  PNGs: no rebuild, but only in panels the
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

## Phase 8 — MCP server and CLI (Seb, 2026-10-31: "make an mcp and cli for moritz too")

Agents (Claude and others) and scripts drive Moritz the way the other *craft apps are driven.
- [x] **Moritz MCP server.** Start from Blender Lab's MCP (`projects.blender.org/lab/blender_mcp`,
  GPL-3.0, so it can be forked; installed here as the Claude extension `blender-mcp`: a `uv`
  server `blmcp` plus a Blender add-on that listens in the running app). Fork it as **Moritz
  MCP**: Moritz's name and icon, the add-on built into Moritz (always on, like Maximize, with an
  on/off and port setting in Preferences), and Moritz's own tools on top of the generic ones:
  - Create: every Create-tab object with its Max parameters (Box, Teapot, Suzanne, TorusKnot …,
    shapes), named Box001 etc.
  - Modify: the stack in Max order; add from the Moritz modifier list by Max or Blender name;
    Edit Poly levels 1–5, its tools (Smart Extrude, Chamfer, Weld, Bridge, Cap …), Collapse To.
  - Utilities: Align, Array, Spacing Tool, Object Paint; Transform Type-In values.
  - Scene: Scene Explorer data (layers = collections, freeze, hide), selection sets, Hold / Fetch.
  - Settings: keymap and name scheme; screenshot of a viewport or the window.
  - Every tool goes through the same operators as the UI, so undo works.
  Ship it as a Claude extension (`.mcpb`) next to the release, and document the setup in the
  README. The app's text calls it Moritz's own, not Maximize's.
  **Done 2026-10-31:** add-on `scripts/addons_core/moritz_mcp` (built in, server off until Preferences > System > Moritz MCP, localhost port 9877), 38 Moritz commands in `commands.py` (Create, Modify, Edit Poly, Utilities, Scene Explorer, Settings) next to the generic tools; server `moritz/mcp` (package `mzmcp`), `.mcpb` from `moritz/tools/make_mcpb.py`. Object Paint is not a command (it is interactive). Tests `test_moritz_mcp_commands.py`, `test_moritz_mcp_live.py`.
- [x] **Moritz CLI** (`moritz-cli.exe` next to `moritz.exe`, in the zip and MSI). Two modes:
  - **Headless** (wraps `moritz.exe -b`): `open`, `info` (objects, modifiers, missing files),
    `render` (frame / range / camera), `convert` (FBX, OBJ, glTF, USD, .max via the importer),
    `run` (a Python script), `test` (the suite).
  - **Live**: the same commands against a running Moritz through the MCP add-on's socket
    (`--connect`), plus `command list` / `command run` for every MCP tool, so the CLI and the MCP
    share one command set.
  - JSON output with `--json`, for scripts and agents.
  **Done 2026-10-31:** `scripts/modules/moritz_cli.py` behind the console launcher `moritz-cli.exe` (`source/creator/moritz_cli_win32.c`): info, open, render, convert, run, test, command list/run, serve; `--json`, `--connect`.
- *Add-on and packaging work, no core change. The add-on and CLI ship in the packages, so a new
  release is needed to deliver them. Files unaffected. Security: the socket listens on
  localhost only, and it's off until enabled in Preferences (it runs any Python).*

## Found installing 0.2.0 (2026-10-31)

- [x] **The MSI installs per machine, not per user.** It went to `C:\Program Files\Moritz\`, with
  the Start Menu shortcut in `C:\ProgramData\…`. That goes against the decision "Installer: per user
  (no admin rights)". It should go to `%LOCALAPPDATA%\Programs\Moritz` with `ALLUSERS=""` /
  `MSIINSTALLPERUSER=1` (WiX `Scope="perUser"`), the shortcut in the user's Start Menu.
  **Done 2026-10-31:** `Scope="perUserOrMachine"` (ALLUSERS=2, MSIINSTALLPERUSER=1), registry under HKMU; a launch condition stops it while the per-machine 0.2.0 is installed (uninstall that first). Tables checked; not installed here.
- [x] **`moritz.exe --version` prints "Blender 5.3.0 Beta"**; the rebrand sweep missed it. It
  should print "Moritz 0.2.0 (based on Blender 5.3.0)" (`creator_args.cc`, `print_version_full`).
  *Core, rebuild; batch with the next one.*
  **Done 2026-10-31:** prints "Moritz 0.2.0 (based on Blender 5.3.0 Beta)"; new `bpy.app.moritz_version_string`.

## No Blender in menus and splash (Seb, 2026-10-31)

- [x] *(Seb: "remove all references to Blender, except for the credit, in the programs menus and
  splashscreen")* **This overrides the earlier "Blender's own links stay named as Blender's".**
  In every menu of the app (top bar File / Edit / Render / Window / Help, editor headers, context
  menus, the Preferences window) and on the splash, nothing says "Blender" any more. The only
  exception is the credit: "Based on Blender" in About and one credit line on the splash.
  - **Help menu:** Blender Website, Blender Store, Development Fund, Release Notes, Python API
    Reference, Report a Bug, and the "Blender" items in the Help > Manual entries. Keep **Manual**
    and **Python API Reference** under neutral names (they still open Blender's docs, which are
    the right ones). **Report a Bug** opens Moritz's GitHub issues. Remove the Store, Fund and
    Blender Website items, and point **Release Notes** to Moritz's release page.
  - **Splash:** the links column (Donate, What's New, Blender links) shows Moritz's: Release
    Notes, Manual, Report a Bug. "What's New in Blender" goes. Credit line: "Based on Blender".
  - Also check: the File menu (Import/Export "Blender" entries, "Link / Append from Blender
    file"), Preferences (System > "Blender" labels, Save & Load), "Install Application Template",
    the top-left app menu, and the Windows Start Menu / taskbar names.
  - Keep: version numbers in file-compatibility messages, internals (`.blend`, `bpy`), and the
    license texts.
  - *Core and bundled scripts, so it needs a rebuild; batch it with the --version fix. Files
    unaffected.*
  **Done 2026-10-31:** Help menu, splash, About, theme presets (Dark / Light), Windows version info (moritz.exe "Moritz"). Kept on purpose: the "Blender" keymap and name scheme (they name the compatibility modes). Checked in screenshots.

## Create tab: category buttons in a column (Seb, 2026-10-31)

- [x] *(Seb, screenshot of the Create tab's seven category icons: Geometry, Shapes, Lights,
  Cameras, Helpers, Space Warps, Systems; "those buttons need to be a vertical row on the panel")*
  The category buttons go **one above the other in a vertical column** along the panel's left
  edge, with the object-type grid to its right, instead of the horizontal strip on top. Icons only
  (names in the tooltips), the active one highlighted as now. Python layout (`ui.py` /
  `properties_create`), no rebuild unless the panel itself lives in core; files unaffected.
  **Done 2026-10-31:** `properties_create.py`: icon column on the left, category name and the two-column grid to its right; checked at 230 px panel width.

## Bug: .max importer missing from File > Import (Seb, 2026-10-31)

- [x] *(Seb's screenshot of File > Import in the installed 0.2.0: no "Autodesk MAX (.max)",
  only Max Scene (.mxscene))* **Cause, checked headless:** the importer
  (`bl_ext.system.io_scene_max`) is installed and enabled with factory settings, but Seb's saved
  `%APPDATA%\Moritz\5.3\config\userpref.blend` (from 2026-10-30) doesn't list it, so it stays off.
  Any user with saved preferences hits the same problem. **Fix:** treat it like Maximize, always on
  (`addon_utils.BUILTIN` or enabled once per version at startup, remembering if the user turned it
  off). Seb's workaround for now: Preferences > Add-ons > "Import Autodesk MAX" on.
  **Done 2026-10-31:** `addon_utils.DEFAULT_ON` enables it once for saved preferences that lack it (marker `moritz_default_addons.txt`); turned off later, it stays off. Test `test_default_addons.py`.

## Smart Extrude bugs (Seb, 2026-10-31, two screenshots)

*(Seb: "smart extruding on two axis plane doesn't work yet, please confirm the error in the code,
before you code. also extruding inwards, should be like a boolean substraction, but it is more
like an intersection.")* **Rule: confirm the cause (in the code or by reproducing it) before
changing code.**
- [x] **Plane handle (two axes). Cause confirmed in the code:** in Blender's Move gizmo the
  plane handles are `GIZMO_GT_arrow_3d` gizmos too (`transform_gizmo_3d.cc` line 1703,
  `GIZMO_NEW_ARROW(MAN_AXIS_TRANS_XY)` etc., drawn in the plane style). Maximize's
  `gizmo_arrow_move` (`transform.py` line 656) picks any highlighted `GIZMO_GT_arrow_3d`, so a
  Shift+drag on a plane handle is taken for an arrow and constrained to one axis (the handle's
  Z), not moved in the plane. Fix: skip the plane-style handles there (their `draw_style`) and let
  the gizmo's own plane move run. Blender's Shift flip only affects single-axis handles
  (`transform_gizmo_3d.cc` line 2207), so the plane stays a plane. The same fix covers Clone on
  the plane handles.
  **Done 2026-10-31:** Maximize 9de0a1e (`draw_style != 'NORMAL'` skipped); test `test_smart_extrude_drag.py` with `MX_GIZMO=PLANE`.
- [ ] **Inward gives an intersection instead of a subtraction. Not confirmed yet; reproduce
  first** (Seb's object: a wedge-shaped ridge, a polygon on its sloped top pushed in; the result
  is only the piece inside the cutter). `smart_extrude()` calls
  `mesh.intersect_boolean(operation='DIFFERENCE')` with the cutter solid selected, which is
  right. An intersection-shaped result means one of the two solids reads as inside-out:
  (a) the cutter's normals point inward after `recalc_face_normals(faces=solid)` (line 212)
  on a skewed, thin solid; or (b) Seb's mesh is open or has flipped normals, so the exact
  solver's inside test inverts. Check with Seb's mesh: cutter normals before the boolean, and
  whether the mesh is manifold.
- [x] **Found while reading the code, confirmed:** in the boolean path, `_cap_plane` uses the
  *move* direction as the cap's normal (line 137), so any move that isn't along the polygon
  normal (an arrow off the normal, a plane drag) finds no cap afterwards and leaves nothing
  selected. `_widening` also tests "along" against the move direction. Use the polygons' normal
  for the cap, and the move only for the sweep.
  **Done 2026-10-31:** Maximize 9de0a1e, `_cap_plane` uses the polygons' normal. `_widening` stays: its "along" test is about the move.
  **Not reproduced (2026-10-31):** wedge ridge, push along the normal, along Global Z, through the far side, on an open mesh: all subtract. Waiting for Seb's .blend or exact steps.

## Create: drag bug and parameters (Seb, 2026-10-31)

- [ ] **Bug, not confirmed yet; reproduce first:** *(Seb: "when creating a teapot there is a bug,
  maybe also with the other, when you click and drag, you can make it bigger, and smaller, but
  not bigger again. it gets stuck.")* While dragging the size, a Teapot can shrink after growing,
  but can't grow again. Check all drag-created objects (Teapot, Suzanne, Sphere, Box …), both
  keymaps. Reading `primitives.py` found no clamp in `_apply` (`RADIUS`: `d.length * scale`).
  Candidates to check: the input's soft or hard max in the node group, an `update_tag` /
  depsgraph lag, or the ray hit (`_hit`) jumping when the mouse passes over the new object.
  Confirm before changing code.
  **Not reproduced (2026-10-31):** every drag-created type (23) grows, shrinks and grows again by parameter and by evaluated size, in both keymaps, in all four quad views, shrunk to the center and dragged far out (`test_create_drag_grow.py`); the creation code is unchanged since 0.2.0. Need a screen recording or exact steps from Seb. Found on the way and fixed: Capsule showed nothing during its radius drag (height 0 clamps its caps); now a sphere, height never below the diameter.
- [x] *(Seb: "also i would like to see the parameters in the create panel")* **Parameters in the
  Create tab:** as in Max, after (and while) creating an object, the Create panel shows its
  parameters below the object-type grid: Name and Color, then Parameters (radius, segments,
  Teapot parts, …), and Creation Method / Keyboard Entry where Max has them. They are the same
  live inputs the Modify tab shows, for the just-created or selected object of that type. In Max
  they stay editable until you pick another tool or object.
  **Done 2026-10-31 (Maximize dfb74e2):** Create tab panels Keyboard Entry and Parameters (add-on, `ui.py`), below Name and Color, for the last created object until another object is active; they redraw during the drag. Not done: Creation Method (Max's Edge / Center, Cube / Box) needs new creation modes; ask Seb if he wants them.

## Slice Plane: big white disk (Seb, 2026-10-31, screenshot, "what is that white sphere?")

- [x] **Cause found in the code (`poly_tools.py`, `MAXIMIZE_GGT_slice_plane`):** the white disk
  is the Slice Plane's **move handle** (`GIZMO_GT_move_3d`, `FILL` + `ALIGN_VIEW`), with three
  faults:
  1. **Drawn at twice the plane's position:** `draw_prepare` sets
     `move.matrix_basis = Translation(co)`, and the gizmo also adds its target `offset`, which is
     the same `maximize_slice_location`. In the screenshot the disk sits as far above the plane as
     the plane sits above the ground (about 48 px each). Fix: identity `matrix_basis` (the offset
     carries the position), or no target and an operator drag.
  2. **No color set:** it draws in the default white, opaque. Use the plane's yellow with low
     alpha and a highlight, like the dials.
  3. **Too big:** no `scale_basis`, and `FILL` fills the whole circle. Use a small ring
     (`ALIGN_VIEW` without `FILL`, or a small `scale_basis`), as Max's Slice Plane has no big disk.
  - Also check that dragging the handle moves the plane 1:1 (not 2:1) after the fix.
  **Done 2026-10-31 (Maximize dfb74e2):** double position confirmed (`move3d_gizmo.cc` line 63 adds the target to the matrix); now identity matrix, yellow ring (scale 0.2, picked as a disk with FILL_SELECT). Found too: the second (green) dial never bound (`target_set_prop` index 1 is refused, `rna_wm_gizmo_api.cc` line 131), so `setup` failed half-way; both dials use get/set handlers, and a dial seen edge-on hides (it took the ring's clicks in the side views). Test `test_slice_plane_gizmo.py`: the plane follows the mouse 1:1.

## SwiftLoop does nothing (Seb, 2026-10-31: "swiftloop doesn't do anything yet?")

- [x] **Not confirmed; reproduce first.** The button is a name alias (`vocabulary.py` line 195:
  `swift_loop` → `mesh.loopcut_slide`, no options). From a panel button the alias runs it with a
  3D View override (`run()`, line 300). Likely cause: Loop Cut and Slide works on the edge under
  the mouse at invoke time, and the click happened in the Command Panel, so there is no edge under
  the cursor and it ends or waits without effect. Check what happens: cancelled, or a modal that
  never gets viewport events.
  **Done 2026-10-31 (Maximize dfb74e2):** confirmed (from the panel `mesh.loopcut_slide` returns CANCELLED at once, nothing under the mouse). New modal `maximize.swift_loop` (`poly_tools.py`): yellow preview of the ring cut under the mouse, click inserts (own ring cut at the mouse position), Shift flow (Set Flow on the new loop), Ctrl select loop, Ctrl+Shift remove, Alt+drag edge slide, one undo step per click, right-click / Esc ends, button pressed while on; also in Blender's Edge menu. Test `test_swift_loop.py` (both keymaps). Alt+drag slide is not covered by the test.
- **What it should be (Max's SwiftLoop):** a **mode**. Click the button, then in the viewport a
  loop preview follows the edge under the cursor; each click inserts a loop there, and you can
  insert as many as you like until right-click or Esc. Shift+click inserts a loop and keeps it
  flowing (Max: "Shift+click: flow loop"); Ctrl+click selects the loop; Ctrl+Shift+click
  removes it; Alt+drag slides. The button stays highlighted while the mode is on. Build it as a
  modal operator that calls `mesh.loopcut` at the mouse position per click (or our own ring cut)
  instead of one Loop Cut and Slide.

## Moritz manual on GitHub (Seb, 2026-10-31: "Let's host a manual on Github too")

- [ ] **A Moritz manual on GitHub Pages**, the target of Help > Manual and the splash's Manual
  link (both open Blender's manual today).
  - **Scope:** what Moritz does differently, not a copy of Blender's 2000-page manual:
    - Getting Started: Quick Setup, keymaps, name schemes, and what is Max-like vs Blender.
    - Command Panel: Create, Modify, Utilities.
    - Edit Poly and Editable Poly: levels, ribbon tools, Smart Extrude, SwiftLoop, Slice Plane,
      Freeform / Paint Deform.
    - The modifier list (Max and Blender names), Splines, the quad menu, the Scene Explorer
      features.
    - Importing from Max: the .max importer and the .mxscene exporter.
    - MCP and CLI.
    - "For Max users" and "For Blender users" pages.
    Every page links to the matching Blender manual page for everything Moritz leaves unchanged.
  - **How:** Sphinx with RST, like Blender's manual, so pages can link or borrow from it. Blender's
    manual is CC-BY-SA 4.0, so borrowed text needs credit and the same license. Source in
    `moritz/manual/` in the Moritz repo (or its own repo `cyberhirsch/moritz-manual`). A GitHub
    Actions workflow builds it on push to the docs and publishes to Pages. That one is small and
    free (the repo is public), but it is CI: ask Seb before enabling it.
  - **URL:** `https://cyberhirsch.github.io/moritz/manual/<version>/`, versioned like Blender's.
    `_url_from_manual` in `wm.py` points there. Screenshots are made with the Moritz CLI/MCP, so
    they can be redone for each release.
  - Ship the first version with 0.3.0.

## Updater (Seb, 2026-10-31: "build an update (with optional auto) into moritz")

- [x] **Moritz checks GitHub Releases for a newer version and installs it; auto is optional.**
  - **Source:** `https://api.github.com/repos/cyberhirsch/moritz/releases`. Compare with
    `bpy.app.moritz_version_string`. Pick the asset for the platform:
    - Windows: `.msi`
    - Linux: `.tar.xz`
    - macOS: `.dmg`
  - **Preferences > System > Updates:**
    - **Check for Updates on Startup** (on, at most once a day).
    - **Install Updates Automatically** (off by default).
    - **Include Pre-releases** (off).
    - **Check Now** button.
    - The last check time.
  - **Online access:** only when Blender's **Allow Online Access** is on (`bpy.app.online_access`).
    Off means no network at all, and Check Now explains why.
  - **Notice:** a quiet line in the status bar ("Moritz 0.3.1 is available") and an entry in
    Help > **Check for Updates…**. They open a dialog with the version, the release notes
    (`body` of the release) and **Install**, **Skip This Version** and **Later**.
  - **Install:**
    - Download in the background (progress in the status bar, never blocks the UI).
    - Check the file's **SHA-256** against `SHA256SUMS.txt`, which every release then also
      publishes (add it to `make_msi.py` / `make_unix_package.py` and the release workflow).
    - Hand over at quit:
      - Windows: `msiexec /i … /passive` for the per-user MSI, then Moritz restarts.
      - Linux: unpack next to the current folder and swap it in.
      - macOS: mount the dmg and copy `Moritz.app` over.
    - Ask to save unsaved work first. Auto mode installs at the next quit, never mid-session.
  - **Safety:**
    - Only HTTPS from github.com / objects.githubusercontent.com.
    - Only this repo, only signed-off checksums.
    - The portable zip is updated by telling the user, not by overwriting a folder it may not own.
  - **Where:** Python in Moritz's startup scripts (`bl_operators/moritz_update.py` plus the
    Preferences panel), so no new C code. It ships in the packages, with the next rebuild and
    0.3.0. Files are unaffected.
  - **Test:** a fake releases JSON and a local file server, covering:
    - a newer, older and same version
    - the pre-release filter
    - online access off
    - a bad checksum

  **Done 2026-10-31:** `scripts/startup/bl_operators/moritz_update.py` (Help > Check for Updates..., Preferences > System > Updates, status-bar line, dialog with the notes and Install / Skip This Version / Later; settings in `<config>/moritz_update.json`). Background check and download, SHA-256 against `SHA256SUMS.txt` (written by every packager via `record_checksum`, regenerated for all packages in the release job), hand-over through `atexit` (checked: it runs at quit) to a PowerShell / sh helper that waits for Moritz to exit. Test `moritz/tests/test_moritz_update.py` (25 checks, local server). **Not tested end to end:** a real MSI / tar.xz / dmg install (needs a published release with SHA256SUMS.txt; the first is 0.3.0, so the first real update is 0.3.0 → 0.3.x). Copies that aren't the per-user MSI (portable zip, dev builds) get the download page.
## Relax the quad caps (Seb, 2026-10-31: "can we relax the quad cap a little?")

- [x] **Quad caps get a relax.** Done 2026-10-31: Cap Relax (0-1, default 0.5) on Cylinder, Cone,
  ChamferCyl, Spindle, Gengon, Prism and the quad poles of Sphere, Capsule, OilTank (a repeat zone of
  one-step Blur Attribute on position, rim held, blended by Cap Relax; groups now version 6), and on
  Edit Poly Cap (quad and inset; a Laplacian relax in Python, border held). Test
  `tests/test_cap_relax.py`; comparison sheet `cap_relax_compare.png` (Sides 32/48, Cap Segs 1/3, Relax
  0 / 0.5 / 1).
  - **Where:**
    - the primitives' Quad Cap (Cylinder, Cone, ChamferCyl, Spindle, Gengon, Prism; the quad
      poles of Sphere, Capsule and OilTank too)
    - Edit Poly's Cap, quad and inset variants
  - **Today:** the inner grid is a square, so the cells near its corners squeeze and the rings
    toward the circle kink. **Seb's screenshot** (a Cylinder cap from the top): the inner grid is
    pushed out almost to the rim, leaving one thin ring of long, narrow quads around it, and the
    grid cells bulge toward the edge. The relax should even this out: the grid pulls in so the
    outer ring's quads are about as deep as the grid cells, and the cells near the rim get about
    the same size as those in the middle.
  - **The change:**
    - Smooth the cap's inner vertices a few iterations: in Geometry Nodes `Blur Attribute` on
      position, or a Laplacian relax.
    - Keep the outer border and the cap's plane fixed, so the cap stays flat and meets the side
      walls.
  - **Control:** a **Cap Relax** parameter, 0–1, default about 0.5, in the primitive's Parameters
    and Cap's redo panel / caddy. 0 gives today's grid.
  - **Check:** UVs stay clean, the cap stays planar, Sides that aren't a multiple of 4 (the one
    triangle) still look tidy.
  - *Add-on (`quad_caps.py`, `poly_tools.py` Cap). Files: one more Geometry Nodes input; Blender
    evaluates it.*

## mNPR renderer (Seb, 2026-10-31: "a new renderer based on eevee. call it mNPR", "Full copy of EEVEE")
- [x] **mNPR engine: a full copy of EEVEE.** `source/blender/draw/engines/mnpr`, made by
  `moritz/tools/make_mnpr_copy.py` (renames files, namespaces, shader and macro names). Engine id
  `MORITZ_MNPR`, listed as "mNPR". EEVEE's own code is unchanged.
  - Shared hooks: draw manager (view data, engine selection, registration), GPU shader lists,
    `GPU_MAT_MNPR` material type, shader tool rules for `mnpr_` files.
  - Create infos of mNPR's resource tables outside the `mnpr` namespace (`KernelGlobals`,
    `gbuffer::Reader`, ...) are filed under an `mnpr_` key, or they replace EEVEE's
    (`init_mnpr_infos` in `gpu_shader_create_info.cc`). EEVEE crashed before that fix.
  - Every UI and node check that accepts EEVEE accepts mNPR (`BKE_engine_id_is_eevee`;
    `moritz/tools/add_mnpr_to_ui.py` for the Python panels).
  - Test: `moritz/tests/test_mnpr_engine.py`. With strokes off mNPR matches EEVEE exactly.
- [x] **Painted strokes (first NPR feature).** A compute pass after the G-buffer
  (`mnpr_deferred_stroke_normal.bsl.hh`) splits surfaces into stretched 3D Voronoi cells and gives
  each cell one flat normal, read around the cell centre, so every stroke lights as one facet.
  Render > Painted Strokes: Size, Stretch, Strength. Stored as scene properties: files open in
  stock Blender, which ignores them.
- [ ] Strokes anchored on the object (rest position), not in world space: moving objects swim now.
- [ ] Colour jitter per stroke.
- [ ] Silhouette break-up: strokes eat into and spill past the outline (pass before motion blur
  and depth of field in `ShadingView::render_postfx`).
- [ ] Hand test in the viewport and on a real scene (Seb).
- *Files saved with mNPR selected store the engine "MORITZ_MNPR"; not yet checked what stock
  Blender does with that engine name.*

## Upstream maintenance (recurring)
- [ ] Merge each Blender release branch into `moritz/main` (recurring; last: 1 fix from `blender-v5.3-release`, 2026-10-30, merge d1c576d7acf; before that 4 fixes, merge ca65c5eef82; before that 115 fixes, 2026-10-29, merge a188bb1acd8, no conflicts, Windows libraries updated for the KTX / OpenImageIO fix; merge with `GIT_LFS_SKIP_SMUDGE=1`, a plain merge dies on LFS test images)
- [ ] Re-run the test suite and a smoke test of Maximize after each merge (recurring; last: 2026-10-31: all 68 test scripts pass; 2026-10-30 after the 1-fix merge: all 64 test scripts pass; before that, after the 4-fix merge: all 60 test scripts pass, 14 Moritz + 46 Maximize)
