# Modeling, modifier-stack and UV complaints from 3ds Max users switching to Blender

Method note: ~19 search/fetch calls (Oct 22, 2026). Counts below are "distinct threads/posts found in this session", not internet volume. Reddit was NOT reachable through the search tool (site:reddit.com queries returned no Reddit hits; Polycount thread fetch returned 403), so Reddit counts are absent and true volume is certainly higher. Items marked [model knowledge] come from my prior knowledge and were not verified by a fetched source in this session.

## Q1. Modifier stack not editable like Max (no Edit Poly mid-stack, Apply is destructive); does Geometry Nodes change this?

### Takeaway
The most consistently raised complaint (5+ threads found, 2012–2026). Still applies in Blender 5.x: there is no native "Edit Mesh" modifier; Geometry Nodes adds procedural modifiers but not hand-editing mid-stack. Paid add-on MAXStack (kleinARt) now ships an Edit Mesh modifier with Tab-to-edit at any stack position.

### Cited Findings
- 2012 bf-committers mailing list thread asking for a "3DsMax editable poly like toolset" — [archive.blender.org](https://archive.blender.org/lists/bf-committers/2012-April/036277.html)
- BlenderArtists "Edit mesh modifier like 3ds Max" thread: there is no equivalent of the Edit Poly modifier — [BlenderArtists](https://blenderartists.org/t/edit-mesh-modifier-like-3ds-max/622132)
- Polycount "blender 2.8 vs 3ds max .. critical two issue" (2019): user couldn't find an "edit poly" modifier equivalent; another says curves can't be turned back once converted to mesh (historical, 2.8 era) — [Polycount](https://polycount.com/discussion/212519/blender-2-8-vs-3ds-max-critical-two-issue)
- BlenderArtists (Apr 2019, 3ds Max user/architecture teacher "mienda"): missing Edit Poly modifier for rollback-able non-destructive modeling; reply (zeauro) said Blender was moving to node-based modifiers (historical, 2.80) — [BlenderArtists](https://blenderartists.org/t/thoughts-about-blender-2-8-from-a-3dsmax-user-and-a-blender-teacher-in-architectural-school/1153944)
- Steam forum: asks for Max-like edit mesh modifier; suggested workaround is shape keys, which cannot record edge/vertex splits — [Steam](https://steamcommunity.com/app/365670/discussions/0/1743394388072521840)
- Blender task T83928 proposed "Dynamic edit" + "Node History" Geometry Nodes nodes explicitly modelled on Max's Edit Poly "buffer in the modifier stack" — [developer.blender.org T83928](https://developer.blender.org/T83928)
- Blender 5.0 added six GN-based modifiers (new Array, Scatter on Surface, Instance on Elements, Randomize Instances, Curve to Tube, Geometry Input) — none is a manual edit modifier — [Blender 5.0 modeling release notes](https://developer.blender.org/docs/release_notes/5.0/modeling/)
- Add-on: MAXStack ("Max Stack – Max Modifiers and Stack", kleinARt/Valentin Klein, Superhive): 39 modifiers incl. Edit Mesh modifier (Tab-edit at any point in stack, Delta/Replace modes), Shell, Slice, Weld, FFD; $20; listed for Blender 4.2–5.2 (description says 4.3+); v1.3 Oct 2026 — [Superhive](https://superhivemarket.com/products/max-stack-3dsmax-modifiers)

### Inferences
- GN makes a Max-like *procedural* stack possible (add-ons above are built on it) but does not by itself provide sub-object editing on a modifier; mid-stack topology edits remain an add-on feature.
- [model knowledge] Native partial mitigations: Weld modifier (2.90) answers the old "Merge modifier" request (cf. [devtalk Merge modifier thread](https://devtalk.blender.org/t/hurdles-to-implementing-merge-modifier/9718/20)); "On Cage"/"Edit Mode" modifier toggles let you edit the base mesh while seeing the stack result, but edits always go to the base, not mid-stack.

### Gaps
- No Reddit counts; no current (2025–26) devtalk proposal for a native Edit Mesh modifier found.
- MAXStack quality/reviews not checked.

## Q2. Edit Poly tool gaps (Swift Loop, Connect with slide/pinch, Cap, Extrude Along Spline, Shell, Graphite, Chamfer/Quad Chamfer vs Bevel)

### Takeaway
Raised in roughly 6 threads found, mostly older Polycount/BlenderArtists posts. Most tools have Blender analogues; perceived gaps are Swift Loop ergonomics, Max Chamfer/Quad Chamfer quality and smoothing-group-driven chamfer, and a true Shell modifier (Solidify differs). Nothing in 4.x/5.x release notes specifically targets these.

### Cited Findings
- Polycount: user misses SwiftLoop speed/edge-flow; Blender Loop Cut and Slide "always starts from the centre of the edge"; another user praises mousewheel loop count with preview — [Polycount](https://polycount.com/discussion/comment/1119556)
- Polycount: replicating Max Inset in Blender via scale on individual origins + zero extrude (old thread; Blender has had an Inset tool since 2.6x [model knowledge]) — [Polycount](https://polycount.com/discussion/comment/1078237)
- BlenderArtists "Blender's Bevel like the 3ds max's chamfer": bevel "doesn't quite achieve the same results as chamfering" — [BlenderArtists](https://blenderartists.org/t/blenders-bevel-like-the-3ds-maxs-chamfer-question/659606)
- Polycount: Max Chamfer/Quad Chamfer modifiers can pick edges by smoothing groups (fast low-to-high workflow); Blender Bevel modifier closest but "does not handle it as good as max bevel in some cases"; others prefer Blender bevel weights — [Polycount](https://polycount.com/discussion/comment/2726437); [Polycount](https://polycount.com/discussion/220526/src)
- Mienda (2019): bevel/chamfer "not parametric enough"; reply: Bevel modifier improved for 2.80 (historical) — [BlenderArtists](https://blenderartists.org/t/thoughts-about-blender-2-8-from-a-3dsmax-user-and-a-blender-teacher-in-architectural-school/1153944)
- Blender 5.0: Bevel and Symmetrize now support Auto Merge (minor) — [5.0 notes](https://developer.blender.org/docs/release_notes/5.0/modeling/)
- Shell: no 1:1 Shell modifier; Solidify is the usual substitute. Add-ons: MaxStyle Modifier (free, Booth, Blender 5.2+, GN-based: Extrude, Shell with separate inner/outer, Sweep, UVW Map) — [Booth](https://booth.pm/en/items/8671900); MAXStack Shell — [Superhive](https://superhivemarket.com/products/max-stack-3dsmax-modifiers)
- Old Max-vs-Blender equivalence table (Blender 2.6x era) maps Edit Poly → Edit Mesh, Extrude → curve->geometry, FFD → Lattice — [assettocorsamods](https://assettocorsamods.net/threads/max-vs-blender-equivalence-table.1032)

### Inferences
- [model knowledge] Blender equivalents: Swift Loop ≈ Loop Cut and Slide (Ctrl+R) / Knife; Connect ≈ Subdivide/Connect Vertex Path (J) — no built-in slide/pinch params; Cap ≈ Fill (F)/Grid Fill; Extrude Along Spline ≈ Curve modifier on extruded faces, or GN; Graphite "Ribbon" has no counterpart except add-ons and pie menus. Quad Chamfer topology ≈ Bevel with Miter/"Harden Normals" options but not identical.
- [model knowledge] Common add-ons cited by switchers: LoopTools (bundled extension), MACHIN3tools/MESHmachine (chamfer/fillet editing), Edge Flow/Set Flow, Fast Loop. Not verified in this session.

### Gaps
- No source found for Connect slide/pinch or Extrude Along Spline complaints specifically; volume unknown.
- Did not find Blender add-on pages dedicated to Max Swift Loop / Graphite clones.

## Q3. Weak spline/shape modeling (Editable Spline, fillet/chamfer/outline, shape booleans, Loft, Sweep, Lathe, renderable splines)

### Takeaway
Very common and still current: found in ~6 threads 2019–2026, including a January 2026 archviz thread calling Blender spline drawing "very very hacky". Blender 3.x–5.x improved curves via Geometry Nodes (Fillet Curve, Curve to Mesh, 5.0 Curve to Tube modifier, 5.3 NURBS input nodes/miter scale), but there is no Editable-Spline-grade toolset (outline, 2D booleans, trim/extend) natively.

### Cited Findings
- Chaos forum "Replacing 3dsMax with Blender for archviz" (Jan 29–30, 2026): spline drawing "very very hacky and not well supported"; meshes from splines at varying elevation fail; CAD import hard; recommended add-ons z-Curve-Sweeper (free), Loft Curves (~$20 Superhive), BlenderGIS, ND Primitives — [Chaos forum](https://forums.chaos.com/t/replacing-3dsmax-with-blender-for-archviz/124304)
- Mienda (2019): missing Edit Spline modifier and Sweep modifier; curve bevel "very poor in parameterization"; replies: Polysweeper, Extra Objects profiles, Sverchok (historical) — [BlenderArtists](https://blenderartists.org/t/thoughts-about-blender-2-8-from-a-3dsmax-user-and-a-blender-teacher-in-architectural-school/1153944)
- Polycount (2019): Blender curve tools "don't come anywhere close to Max's Spline tools"; user models with loose verts/edges + subdivision instead; misses real-world UV on Max splines — [Polycount](https://polycount.com/discussion/212519/blender-2-8-vs-3ds-max-critical-two-issue)
- Blender 5.0: Curve to Tube modifier (round caps, UVs); Curve Data edit-mode panel — [5.0 notes](https://developer.blender.org/docs/release_notes/5.0/modeling/); 5.3 (alpha) GN notes add NURBS input nodes and Curve to Mesh "Miter Scale" — [5.3 GN notes](https://developer.blender.org/docs/release_notes/5.3/geometry_nodes/)
- Add-ons: MAXStack spline modifiers Lathe, Sweep (10 sections), Bevel, Extrude, Renderable Spline, Normalize Spline — [Superhive](https://superhivemarket.com/products/max-stack-3dsmax-modifiers); MaxStyle Modifier Extrude/Sweep (free, 5.2+) — [Booth](https://booth.pm/en/items/8671900); BlendSplines (Gumroad, atelierbump) — [Gumroad](https://atelierbump.gumroad.com/l/blendsplines)

### Inferences
- [model knowledge] Blender 3.3 added the Curve Pen tool and 3.x the Fillet Curve GN node; Screw modifier ≈ Lathe; curve Bevel/Extrude ≈ renderable spline. Outline (offset) and 2D shape booleans are still missing natively.

### Gaps
- Could not verify the exact release of Fillet Curve node / Curve Pen in this session.
- No Reddit count.

## Q4. Smoothing groups vs sharp edges / Auto Smooth (4.1 modifier change), FBX round trip

### Takeaway
Persistent pain point (~8 threads/issues found, 2006–2024): Blender has no smoothing groups, FBX round-trip to Max loses or mangles them, and the 4.1 removal of mesh Auto Smooth (replaced by "Smooth by Angle" GN modifier) drew a "workflow regression" report. Partly eased in 4.2 (Shade Auto Smooth returns as menu op adding the modifier). Smoothing groups themselves remain unsupported.

### Cited Findings
- Right-Click Select "Smoothing groups (+ Edit Poly) workflow" (4 Jul 2020): Open, 13 up/5 down, 11 comments; a game dev stays in Max because of it; 2022 comment: FBX no longer preserves groups into Max; 2023 counter-view: auto smooth 180° + sharp edges equivalent, Blender SG export buggy — [RCS](https://blender.community/c/rightclickselect/CQfbbc/)
- FBX export emulates SGs by splitting sharp edges; Max import produced only 2 smoothing groups — [Blender issue #104434](https://projects.blender.org/blender/blender-addons/issues/104434); custom normals lost Blender→Max (2.79/2.8) — [#57673](https://projects.blender.org/blender/blender/issues/57673)
- Forum workaround: shade smooth, mark sharp, Auto Smooth 180°, export Smoothing=Edge, enable SG on Max import — [BlenderArtists](https://blenderartists.org/t/blender-to-3ds-max-smoothing-groups-dont-work-as-expected/637244); further threads: [Polycount 226094](https://polycount.com/discussion/226094/blender-to-3ds-max-smoothing-groups-problem), [BlenderArtists 1109396](https://blenderartists.org/t/smoothing-groups-problem/1109396), [Polycount 206615 (baking)](https://polycount.com/discussion/206615/blender-smoothing-groups-fro-baking)
- 4.1: Auto Smooth became modifier-only; linked-object workflow complaint — [BlenderArtists](https://blenderartists.org/t/blender-4-1-auto-smooth-is-now-a-modifier-only/1488922); "Workflow Regression: Autosmooth 4.1" — [#116922](https://projects.blender.org/blender/blender/issues/116922); 4.1 files shade fully smooth in 4.0 — [#118118](https://projects.blender.org/blender/blender/issues/118118)
- 4.2: "Shade Auto Smooth" back in context menu, adds Smooth by Angle modifier (user report) — [CG Cookie](https://cgcookie.com/community/18932-auto-smooth-is-back-in-blender-4-2)

### Inferences
- Smoothing groups as data remain unsupported in 5.x; issue is now mostly FBX interop for game/Max pipelines.

### Gaps
- Did not verify whether Blender's newer C++ FBX importer (4.5+) changed SG handling.

## Q5. Modifier gizmos (Bend, Taper, FFD) vs Blender empties

### Takeaway
Raised in ~4 threads; still applies partially. Simple Deform needs an empty for axis/origin, no in-viewport gizmo; Lattice is a separate object. 5.0 added "Lattice Deform Selected" (auto-fit lattice) and gizmos for the new Array modifier.

### Cited Findings
- 2019: Simple Deform's Bend works non-destructively "though without a 3ds Max-style gizmo" — [BlenderArtists](https://blenderartists.org/t/thoughts-about-blender-2-8-from-a-3dsmax-user-and-a-blender-teacher-in-architectural-school/1153944)
- Equivalence table: FFD → Lattice; many add-ons make it behave like Max FFD — [assettocorsamods](https://assettocorsamods.net/threads/max-vs-blender-equivalence-table.1032)
- 5.0 "Lattice Deform Selected" operator fits lattice to selection — [5.0 notes](https://developer.blender.org/docs/release_notes/5.0/modeling/); 5.0 Array modifier with interactive gizmos — [CG Channel](https://www.cgchannel.com/2025/11/blender-5-0-is-out-check-out-its-5-key-features)
- Add-ons: Bend Modifier (Mark Kingsnorth, Gumroad, "inspired by 3ds Max") — [Gumroad](https://mark-kingsnorth.gumroad.com/l/bend-modifier); MAXStack Bend/Twist/Taper/FFD — [Superhive](https://superhivemarket.com/products/max-stack-3dsmax-modifiers)

### Gaps
- Whether MAXStack/Bend add-on use true gizmos vs empties not verified.

## Q6. No UVW Map modifier with box/cylinder gizmo and real-world size (archviz)

### Takeaway
Strong, current archviz complaint (~4 threads 2011–2026). No native equivalent in 5.x (UV Project modifier needs projector objects; cube projection is destructive). Add-ons: XYZ Mapper, MAXStack UV Map, MaxStyle Modifier UVW Map (with real-world map size).

### Cited Findings
- Jan 2026: "there is no regular UVW box map?"; Blender cube/cylindrical mapping lacks controls and is destructive; XYZ Mapper (Superhive, paid) closest — [Chaos forum](https://forums.chaos.com/t/replacing-3dsmax-with-blender-for-archviz/124304)
- 2011 BlenderArtists "Simple Box UVW map modifier" request incl. world-dimension sizing — [BlenderArtists](https://blenderartists.org/t/simple-box-uvw-map-modifier/524479)
- 2019: UVW Map modifier missing; workarounds Texture Space, Image Texture box projection — [BlenderArtists](https://blenderartists.org/t/thoughts-about-blender-2-8-from-a-3dsmax-user-and-a-blender-teacher-in-architectural-school/1153944)
- MaxStyle Modifier UVW Map: Planar/Box/Cylinder/Spherical, Fit/Center, "Real-World Map Size" — [Booth](https://booth.pm/en/items/8671900); MAXStack UV Map with viewport gizmo — [Superhive](https://superhivemarket.com/products/max-stack-3dsmax-modifiers)

### Gaps
- XYZ Mapper product page not fetched.

## Q7. Unwrap UVW not in the stack; map channels; further complaints

### Takeaway
Sparse evidence in this session (~2 posts). Blender UV editing is always destructive on base mesh UV maps; 5.0 improved the UV editor (sync select, pack to region, arrange islands) but not stack-based unwrap. Additional complaints found: object scale vs dimensions (Ctrl+A), lack of parametric primitives, Boolean/Slice reliability.

### Cited Findings
- 5.0 UV changes: sync-selection per-UV, shared selection across UV maps, Pack to custom region, Arrange/align islands — [5.0 notes](https://developer.blender.org/docs/release_notes/5.0/modeling/)
- Max Unwrap UVW is applied from the modifier list (reference) — [Scribd FATE tutorial](https://www.scribd.com/document/6796507/FATEtutorial3dsmax-v1); Steam thread recommends TexTools for UV — [Steam](https://steamcommunity.com/app/365670/discussions/0/1743394388072521840)
- Extra: scaling objects changes scale not dimensions, distorting modifiers (2019); missing Slice/bisect modifier and Boolean artifacts (2019) — [BlenderArtists](https://blenderartists.org/t/thoughts-about-blender-2-8-from-a-3dsmax-user-and-a-blender-teacher-in-architectural-school/1153944); lack of procedural primitives (2026; ND Primitives suggested) — [Chaos forum](https://forums.chaos.com/t/replacing-3dsmax-with-blender-for-archviz/124304)
- Boolean "Fast" solver renamed "Float" in 5.0 — [5.0 notes](https://developer.blender.org/docs/release_notes/5.0/modeling/)

### Inferences
- [model knowledge] Blender's multiple UV Maps are the map-channel equivalent; UV Warp / UV Project modifiers are the only in-stack UV ops. Boolean Exact solver (2.91) and Bisect remained; Slice as modifier is add-on (MAXStack).

### Gaps
- No dedicated threads found on "Unwrap UVW in stack" or map channels; Reddit not searchable.
