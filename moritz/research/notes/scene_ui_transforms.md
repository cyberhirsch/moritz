# Scene management, UI/navigation and transform-tool complaints from 3ds Max users switching to Blender

How the counts were made: ~14 web searches and fetches (BlenderArtists, Polycount, devtalk, projects.blender.org, Gumroad, Superhive, Blender release notes). The numbers are **distinct threads found by this search**, not how often the topic comes up across the internet. Reddit threads did not show up in any search (the search tool returned none for r/blender, r/3dsmax or r/archviz queries), and Polycount returned HTTP 403 to fetches. So the Reddit/Polycount side is under-sampled, and Polycount threads are known only from search snippets. Most threads found date from 2.7x/2.8x and are marked **[HISTORICAL]**. The current state (Blender 4.x/5.x) is confirmed only where a release note or manual page is cited.

## Q1. Which complaints are real, how often do they come up, and are they still valid?

### Takeaway
The complaints that recur most are: no **Align tool** (Alt+A), no Max-style **layer management / Freeze** (Blender went from 20 layers to Collections in 2.8), **quad menu / keymap** habits, **instances that don't share modifiers**, and **heavy-scene undo/Outliner slowness**. Most threads are from 2013–2020. Blender 4.0's **Snap Base** (press B) fixed the most-cited snapping gap. 4.2 made undo faster. Align, Freeze-as-display-state, modifier instancing and imperial fractions are still not native and are covered by add-ons such as BsMax and BMax Tools.

### Cited Findings

**General "switching from Max" threads (context; ~6 threads found)**
- A BlenderArtists thread (Sept 2018, 2.79/2.8 alpha) has a switcher "missing a few tools" from Max. The fix offered is the BMax add-on for the "align tool" and "layers management". Others in the thread miss Max splines and 2D spline Booleans. Heavy sculpt meshes "slow down to a crawl". The same switcher praises Blender selection as more reliable than Max. [HISTORICAL] — [BlenderArtists: My thought so far after switching from 3ds max](https://blenderartists.org/t/my-thought-so-far-after-switching-from-3ds-max/1127006)
- Polycount "[RANT] What I really REALLY hate about Blender as a 3ds Max user": a long-time Max user calls Blender the least intuitive software they have used, where simple Max actions turn into "finicky workarounds" (from search snippet only; fetch blocked by 403) — [Polycount rant](https://polycount.com/discussion/219632/rant-what-i-really-really-hate-about-blender-as-a-3ds-max-user)
- Polycount "Moving to blender worth it?": a switcher says they still miss **Max's transform gizmo** after learning the shortcuts. Another says it took ~2 years to get "really" comfortable. An experienced user warns the Industry Compatible keymap "will never be exactly the way you want it" (snippet only, 403 on fetch) — [Polycount: Moving to blender worth it?](https://polycount.com/discussion/233800/moving-to-blender-worth-it)
- Other switcher threads: [BlenderArtists: Moving to Blender from 3ds max](https://blenderartists.org/t/moving-to-blender-from-3ds-max/1100657); [Renderosity: 3dsmax user learning Blender](https://www.renderosity.com/forums/threads/2888028) (struggled to select sub-elements; pie menus in 2.73 helped) [HISTORICAL]

**1. Layers / Layer Explorer / Freeze / Display as Box / See-Through / Named Selection Sets (~4 threads)**
- How Max works: frozen objects stay visible but can't be selected or edited. Objects on a frozen layer can't be unfrozen one by one — [Autodesk: Freezing and Unfreezing](https://help.autodesk.com/cloudhelp/2017/ENU/3DSMax/files/GUID-B6650710-B62B-4BAD-8178-81A12DFB2432.htm); [Autodesk Layer Explorer](https://help.autodesk.com/cloudhelp/2015/ENU/3DSMax/files/GUID-DD5876EA-F333-4185-AF51-EDE339B1EBF3.htm)
- This is an old request. A 2004 bf-funboard thread asks for a third state between visible and hidden, and the answer was "not possible" (use linked scenes) [HISTORICAL] — [bf-funboard 2004](https://lists.blender.org/pipermail/bf-funboard/2004-August/002023.html)
- BMax Tools had Max-style layer tools (freeze/render toggles). Its author says they were **dropped in BMax Tools 3.0 because Collections replaced layers** — [BlenderArtists: BMax Tools](https://blenderartists.org/t/bmax-tools-or-how-i-left-3ds-max/586373/82)
- Status 4.x/5.x: Collections have an Outliner selectability toggle (the closest match to Freeze, but objects are not greyed out). Display As: Bounds and In Front / X-ray are per-object properties. Not sourced in this pass, so see Gaps.

**2. Instances vs References / Make Unique — modifiers not shared (~3 threads)**
- How Max works: an instance shares the master object **and modifiers** — [Autodesk: Copies, Instances, References](https://download.autodesk.com/us/3DSmax/2012help/files/GUID-13325749-3C9C-49BF-8601-304FA084699-312.htm)
- A Max user asks how to instance a modifier across objects. Answer: "no way to really instantiate a modifier". Workarounds are Ctrl+L Copy Modifiers and the Copy Attributes add-on [HISTORICAL thread, issue still current] — [BlenderArtists: instance a modifier](https://blenderartists.org/t/is-there-a-way-to-instance-a-modifier-across-multiple-objects/568912)
- Blender linked duplicates (Alt+D) share mesh data, but modifiers stay per-object — [CG Cookie: Duplicate Link](https://cgcookie.com/community/20677-snow-globe-duplicate-link)
- Add-on: **ModiTo / Modifier To Instances** (Superhive). It converts Array/Mirror modifiers into linked-duplicate instances and adds Shift+L to select linked objects — [Superhive: Modito](https://superhivemarket.com/products/-modito)

**3. Xrefs / Containers vs library linking & overrides (~1 thread found; under-sampled)**
- Blender's closest equivalent is Link plus **Library Overrides**: several independent overrides of the same asset, adding modifiers/constraints on top, chained overrides. Limits: overrides can only be edited on selected items, creating them from the Properties ID widget has limited support, and the resync on every file load is costly — [Blender Manual 4.4: Library Overrides](https://docs.blender.org/manual/uk/4.4/files/linked_libraries/library_overrides.html)
- No thread found that compares Max Xref/Containers with Blender directly.

**4. Heavy-scene performance: undo, Outliner, many objects (~6 threads/reports)**
- "Undo Performance Must Be Addressed" (devtalk, 2.8x era): one tester with 1,536 objects / ~75M triangles reported **7 s to undo a single translate**, where Maya was instant [HISTORICAL] — [devtalk: Undo performance must be addressed](https://devtalk.blender.org/t/undo-performance-must-be-addressed/8838); also [devtalk: Undo Performance Feedback](https://devtalk.blender.org/t/undo-performance-feedback/2554)
- An open Outliner showing the scene made Blender unresponsive with many objects (T51861). Blend File display mode hurt viewport performance (T92159) — [T51861](https://developer.blender.org/T51861); [T92159](https://developer.blender.org/T92159)
- Tracked issue: editing with many datablocks (add/delete/duplicate, undo pushes, depsgraph rebuilds) scales with object count — [projects.blender.org #68938](https://projects.blender.org/blender/blender/issues/68938)
- Fixes: 2.83 brought the large undo speedup for Object mode (see Gaps for the source). **4.2: "Faster undo due to implicit sharing"** — [Blender 4.2 Core release notes](https://wiki.blender.org/release_notes/4.2/core/). The 4.2 Outliner changes are usability only (Ctrl-F filtering, "Unused Data" mode) — [4.2 UI notes](https://developer.blender.org/docs/release_notes/4.2/user_interface/). No 4.3/4.4 Outliner speed item found; the 4.4 summary is "Winter of Quality" stability work — [Blender 4.4 release](https://www.blender.org/press/blender-4-4-release)

**5. Keymap, navigation, quad menu, Zoom Extents, Isolate, quad view (~6 threads)**
- The built-in "Industry Compatible" keymap (2.8+) is recommended in many threads. Ctrl+Alt+Q toggles quad view like Max — [BlenderArtists: Blender UI for 3ds Max?](https://blenderartists.org/t/are-there-any-blender-ui-for-3ds-max/1164931); Steam threads also suggest it — [Steam discussion](https://steamcommunity.com/app/365670/discussions/0/1520386297686927961)
- Feature request: "Is it possible to implement context menus like 3ds max?" — [devtalk quad menu](https://devtalk.blender.org/t/is-it-possible-to-implement-context-menus-like-3ds-max/13439)
- **BsMax** (3ds Max UI simulator): Max keymap, quad menu, Align, Array, Rename. Its Align tool can also be reached from Object > Transform > Align Objects (BsMax) — [devtalk: BsMax](https://devtalk.blender.org/t/bsmax-for-blender-2-80-3dsmax-ui-simulator/5790); [BlenderArtists: Need help with BsMax](https://blenderartists.org/t/need-help-with-the-bsmax-addon/1265931). A Polycount user notes the quad menu is of limited use without gizmo cycling (snippet) — [Polycount comment](https://polycount.com/discussion/comment/2690439)
- Isolate: Blender's Local View (numpad /) is the equivalent. Extension "Local View Manager" exists on the Extensions platform — [extensions.blender.org: Local View Manager](https://extensions.blender.org/add-ons/local-view-manager/versions/)

**6. Pivot handling: Affect Pivot Only / Working Pivot / Reset XForm (~3 threads)**
- How Max works: Reset XForm puts the transforms into an XForm modifier gizmo and resets the node. Affect Pivot Only + Align to World — [Autodesk MAXScript: Align Pivot & Reset Transform](https://help.autodesk.com/cloudhelp/2025/ENU/MAXScript-Help/files/3ds-Max-Objects-and-Interfaces/Node-MAXWrapper/Node-Common-Properties-Operators/GUID-CE525795-1A44-4DB3-BA90-DACA69430115.html); [Polycount pivot thread](https://polycount.com/discussion/comment/965922)
- Blender equivalents (Options > Affect Only: Origins; Ctrl+A Apply Transforms; Set Origin): not confirmed by a fetched source in this pass. See Gaps.

**7. Transform Type-In (F12) and snapping (~3 threads + release notes)**
- **Fixed in 4.0**: **Snap Base**. Press B during a transform to pick the base point (vertex-to-vertex snapping), Alt to navigate during the transform, new snap symbols (vertex/midpoint/perpendicular), and a reworked Snapping popover ("Snap With" moved first) — [Blender 4.0 modeling notes](https://developer.blender.org/docs/release_notes/4.0/modeling/); [Blender 4.0 release page](https://www.blender.org/download/releases/4-0/) (listed as a headline feature at blender.org/release-notes/blender-4-0)
- Max-style axis constraint / slide add-on: "Align & Slide" (Gumroad) — [Align & Slide](https://raydex.gumroad.com/l/alignslide)
- No thread specific to 2.5D snap or an F12 dialog was found. See Gaps.

**8. Align (Alt+A), Array dialog, Spacing Tool, Clone options, Mirror, Snapshot (~5 threads; Align is the most-cited single tool)**
- Max Align picks which part of the source aligns to which part of the target. The old built-in "Align Tools" add-on only used pivots — [BlenderArtists: align on axis to other objects](https://blenderartists.org/t/align-mesh-objects-on-1-or-more-axis-to-other-objects/509950) [HISTORICAL]
- Many paid/free add-ons fill the gap: **Pro Align Tools**, **Simple Align Tools**, **AATB3D** (align/distribute grid, linear, radial), **Mesh Align Plus** (free, GitHub), **Align Between Two** — [Pro Align Tools](https://yainvieyra.gumroad.com/l/pro-align-tools); [Simple Align Tools](https://douripo.gumroad.com/l/pUqdF); [AATB3D](https://aig3d.gumroad.com/l/AATB3D); [Mesh Align Plus](https://github.com/egtwobits/mesh_mesh_align_plus/releases/tag/v0.5.0); [Align Between Two](https://github.com/Mainman002/Blender-Align-Between-Two/releases)
- BsMax bundles Align, an Array dialog and Rename — [devtalk: BsMax](https://devtalk.blender.org/t/bsmax-for-blender-2-80-3dsmax-ui-simulator/5790)
- Max-modifier-style add-on: "Max Stack — Max Modifiers And Stack" (Superhive) — [Superhive: Max Stack](https://superhivemarket.com/products/max-stack-3dsmax-modifiers/ratings)

**9. Units, imperial input, precision (~5 threads)**
- Imperial unit system with typed suffixes (' ", mil, yd, mi). Needs advanced numeric input to give correct results — [KatsBits: Metric & Imperial units](https://www.katsbits.com/site/?p=1672)
- **Fractions of an inch cannot be displayed** — [BlenderArtists: fractions of an inch](https://blenderartists.org/t/how-can-i-adjust-the-imperial-units-to-show-fractions-of-an-inch/567066); [BlenderArtists: feet & inches](https://blenderartists.org/t/how-do-you-work-in-imperial-units-feet-inches-in-blender/1122156)
- Bug #49960: extruding by a typed value with inches gives the wrong amount — [#49960](https://projects.blender.org/blender/blender/issues/49960); 2012 bf-committers thread on imperial units for architecture [HISTORICAL] — [bf-committers 2012](https://lists.blender.org/pipermail/bf-committers/2012-March/035802.html)

**10. Selection: Select by Name, filters, backfacing (~1 thread)**
- The only direct mention found is a 2018 switcher who said Blender selection worked better than Max's buggy one — [BlenderArtists 2018](https://blenderartists.org/t/my-thought-so-far-after-switching-from-3ds-max/1127006). No threads found on a Select-by-Name dialog or selection filters.

**Further complaints found in this area**
- **The Max transform gizmo** itself is missed (Polycount, snippet) — [Polycount](https://polycount.com/discussion/233800/moving-to-blender-worth-it)
- **Splines / 2D spline Booleans** (strongly tied to archviz) — [BlenderArtists 2018](https://blenderartists.org/t/my-thought-so-far-after-switching-from-3ds-max/1127006)
- **Pipeline / bridge tools** are in demand: 1-Click Sync (Max–Blender bridge), 3Ds Max Bridge, MaxToBlender, Max hierarchy transfer, and the official io-scene-max importer extension (4.2+) — [1 Click Sync](https://superhivemarket.com/products/1-click-sync/docs); [3Ds Max Bridge](https://superhivemarket.com/products/3ds-max-bridge/docs); [MaxToBlender](https://3dtoall.gumroad.com/l/maxtoblender3); [Max hierarchy transfer](https://andrejscripts.gumroad.com/l/blender_max_hierarchy_transfer); [BlenderNation: import .max add-on](https://www.blendernation.com/2024/08/08/import-3ds-max-files-to-blender-with-a-free-add-on/)

### Inferences
- Rough ranking by threads found: Align tool ≈ keymap/quad menu ≈ heavy-scene undo/Outliner > layers/freeze > modifier instancing ≈ imperial units > pivot/Reset XForm > snapping (mostly fixed in 4.0) > Xrefs > selection.
- How much add-ons exist (more than 7 align add-ons, BsMax, BMax Tools, bridge tools) is a stronger signal that a complaint is still live than the dated thread counts.
- Many complaints are about learning curve and muscle memory, not missing features (Industry Compatible keymap, Local View = Isolate, Collections selectability ≈ Freeze).
- Snapping is the clearest "fixed" case (4.0 Snap Base). Undo speed improved (4.2), but no source shows 10k+ object Outliner/selection performance as solved.

### Gaps
- **No Reddit threads were returned** by the search tool, and Polycount fetches were blocked (403). Counts are therefore biased toward BlenderArtists/devtalk and likely under-count the 2021–2026 discussion.
- Not verified with a fetched source: the exact version of the large Object-mode undo speedup (believed to be 2.83), and current Outliner performance with 10k+ objects in 4.x/5.x.
- No Blender 5.x release-note items found on Outliner, undo, Freeze or Align. Nothing in this pass says whether 5.0/5.1 changed any of these complaints.
- Blender-side equivalents to check against the manual: Options > "Affect Only: Origins" (≈ Affect Pivot Only), Ctrl+A Apply Transforms (≈ Reset XForm), Outliner selectability toggle (≈ Freeze), Display As Bounds / In Front (≈ Display as Box / See-Through), Local View (≈ Isolate), View All / Frame Selected (≈ Zoom Extents).
- No threads were found on: Named Selection Sets (the "Selection Sets" add-on is believed to exist but was not verified), Spacing Tool, Clone options dialog, Snapshot, Transform Type-In (F12), 2.5D snap, Select-by-Name dialog, ignore-backfacing, or large-coordinate float precision.
- BsMax's current compatibility with 4.2+/5.x (whether it is on the Extensions platform) could not be confirmed.
- Xref/Container comparison is under-sourced: only the Blender manual was found, with no Max-switcher threads.
