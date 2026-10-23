# Frequency survey: what 3ds Max users complain about when switching to Blender

Sample: 27 distinct sources (forum threads, one blog post, one article, Steam threads). Each source counts once per complaint, however many posters raised it.

**Sample caveats (read first):**
- **Reddit could not be accessed.** The search tool refuses reddit.com, so r/blender, r/3dsmax and r/archviz are **absent** from the sample. This is the largest gap.
- **Polycount returned HTTP 403**, and so did the archive.org mirror. Four Polycount threads (S19–S22) are included **from search-result snippets only**. Their complaint lists may be incomplete.
- **I found no YouTube video or CGArchitect/CGSociety forum thread with a usable complaint list.** The only CGArchitect item is a 2024 article (S14).
- **The sample skews old.** 12 sources are from before Blender 2.8 (2013 to early 2019), 7 from the 2.8x–2.9x era (2019–2021), and only 8 from 2022–2026 (Blender 3.x–5.x). Each source is tagged by era below so stale complaints can be discounted.
- Some threads are single-feature requests (S11, S12, S24, S27), not full switching narratives. They are kept because they come from Max users mid-switch, but they inflate the "Edit Poly mid-stack" count relative to broad threads.

## Q1. Which sources describe Max users switching to Blender (or trying it and abandoning it), with their complaints?

### Takeaway
I catalogued 27 sources from 2013–2026. Complaints cluster around (a) keymap, navigation and shortcut reliance, (b) the loss of Max's non-destructive and parametric modelling (Edit Poly mid-stack, editable primitives, splines), and (c) interface discoverability. Archviz pipeline complaints (V-Ray/Corona, asset-library conversion, plugins) dominate the few 2025–2026 sources.

### Cited Findings — per-source catalogue

Era tags: **[pre-2.8]** = Blender ≤2.79; **[2.8–2.9]** = 2019–2021; **[3.x–5.x]** = 2022–2026.

- **S1 — "My thought so far after switching from 3ds max"** (BlenderArtists), Sep 2018 – Jul 2019, **[pre-2.8 → 2.80]** (2.79/2.80).
  - **Complaints:**
    - Missing Max tools and splines.
    - Imported splines lost their Bézier handles.
    - Weak sculpting and auto-retopo.
    - Slowdowns on heavy meshes; 2.80 edit-mode viewport performance was "very poor".
    - No geometry-to-plane displacement baking in 2.80.
    - Add-ons tied to specific Blender versions.
    - Metin_Seven missed some Max modifiers early on.
  - **Prefers:**
    - Stability: Max crashed and had erratic selection and a corrupted UI.
    - Boolean add-on, Cycles, small download, community.
    - Bmax/BsMax (parametric primitives, quad menu, pivot editing).
    - MiraTools noise deform, which he found better than Max's Noise.
  - **Outcome:** stayed with Blender (bought 3D-Coat for sculpting).
  - Sources: [p1](https://blenderartists.org/t/my-thought-so-far-after-switching-from-3ds-max/1127006); [p7](https://blenderartists.org/t/my-thought-so-far-after-switching-from-3ds-max/1127006?page=7)
- **S2 — "Moving to Blender from 3ds max"** (BlenderArtists), Mar 2018, **[pre-2.8]**.
  - **Complaints:**
    - Losing the "visual intuitiveness" of Max's transform gizmo.
    - Gizmo-free manipulation "takes some getting used to".
    - Full-screen modelling with custom menus and macros is impossible natively without Python.
  - **Prefers:**
    - Ctrl+RMB path select and extruding bare vertices or edges.
    - Built-in sculpting and unfiltered viewport textures.
    - Add-ons: Pie Menu Editor, Hard Ops, TexTools.
  - **Outcome:** stayed (as of the thread).
  - [Source](https://blenderartists.org/t/moving-to-blender-from-3ds-max/1100657)
- **S3 — "3DS Max -> Blender"** (BlenderArtists), OP Apr 2017 **[pre-2.8]**, with Max-user replies in 2022 **[3.x]**.
  - **OP complaints:**
    - Cluttered UI with too many small buttons.
    - Left-click placement and the 3D cursor/pivot behaviour.
    - Hotkeys don't match Max.
    - Inflexible quad view.
    - No clear equivalent to smoothing groups.
    - Camera and lights get in the way when modelling.
    - Unclear how to save a workspace.
    - The Max input preset didn't apply.
  - **2022 replies:**
    - Terminology differs ("merge" vs "weld").
    - Vertex snapping to other objects is hard to find.
  - **Prefers:**
    - Max preset, free price, node materials.
    - UV and weight editing integrated into Edit Mode (Max's equivalents are topology-dependent modifiers).
    - F3 search.
  - **Outcome:** stayed (tentative).
  - [Source](https://blenderartists.org/t/3ds-max-blender/688049)
- **S4 — "Hi New Blender User here… Coming from a 3ds Max Background"** (BlenderArtists), Apr 2024, **[3.x–5.x]** (~4.1).
  - **Complaints:**
    - Interface "like I hit a wall".
    - Total reliance on shortcuts, which also clash with Premiere and After Effects.
    - Node setups are incomprehensible.
    - Tutorials just watch someone use hotkeys. Several Max-user repliers agree; one calls the transition "a bit a nightmare".
  - **Prefers:** F3 search, menus showing their shortcuts, Quick Favorites, the default keymap, BsMax (only its Align was seen as useful).
  - **Outcome:** unknown (the OP will "give it a try").
  - [Source](https://blenderartists.org/t/hi-new-blender-user-here-coming-from-a-3ds-max-background-small-question-regarding-interface/1527510)
- **S5 — "Replacing 3dsMax with (?) Blender (?) for archviz"** (Chaos forum), Jan 28–30, 2026, **[3.x–5.x]**.
  - **Complaints:**
    - Spline modelling is "very very hacky".
    - No standard UVW box map, so no equivalent to Max's UVW Map modifier; cube mapping is destructive.
    - Can't build terrain from elevation splines without add-ons.
    - Procedural primitives are lacking.
    - Blender is "not procedural / destructive" compared with C4D.
    - Heavier hotkey reliance.
    - Converting the asset library is the main obstacle.
    - V-Ray for Blender's readiness is doubted.
  - **Prefers:** geometry nodes, BlenderGIS, a non-destructive terrain test "just as fast".
  - **Outcome:** mixed.
    - OP (Vizioen) **abandoned Blender, moving toward Cinema 4D**.
    - Mokiki is hybrid: still renders in Max with Forest Pack and V-Ray.
    - bardo is moving but keeps a token Max licence for old projects.
  - [Source](https://forums.chaos.com/t/replacing-3dsmax-with-blender-for-archviz/124304)
- **S6 — "Blender newbie questions from someone coming from 3ds Max"** (BlenderArtists), Jun 2021, **[2.8–2.9]**.
  - **Complaints:**
    - No always-on map preview like Slate.
    - No Photoshop-style map layering; no Blend-material equivalent.
    - No typed soft-selection falloff, pinch or bubble.
    - Missing Max viewport controls and shortcuts.
    - No World transform mode.
    - Backface elements can only be selected in wireframe.
    - Paid add-ons needed.
    - Particles called "complete and utter trash" by a former Max user.
  - **Prefers:** EEVEE, node groups acting as instances, Node Wrangler, BsMax.
  - **Outcome:** **hybrid**. Max stays the modelling tool ("I can work way faster… with Max"); Blender is used for simulation, animation and rendering.
  - [Source](https://blenderartists.org/t/blender-newbie-questions-from-someone-coming-from-3ds-max/1310339)
- **S7 — "Yet another 3ds max user struggling to blend in"** (BlenderArtists), Oct 2016, **[pre-2.8]**. The OP had 17 years of Max.
  - **Complaints:**
    - Nowhere to click "to get my hands free".
    - Sticky modal transforms.
    - Gizmos follow the view, not the world.
    - Screen-space transforms add steps.
    - Keyboard-heavy and hard to discover.
    - MMB orbit/Alt pan is the opposite of Max.
    - Drag-select setup failed.
    - Ctrl+Tab for sub-object modes; wants 1/2/3 as in Max.
  - **Prefers:** flexible areas, light and robust, selection conversion, inline help.
  - **Outcome:** likely stayed (still working in it at the end).
  - [Source](https://blenderartists.org/t/yet-another-3ds-max-user-struggling-to-blend-in/677494)
- **S8 — "Blender in Production (3DS Max User Perspective)"** (BlenderArtists), Aug 2014, **[pre-2.8]** (2.71).
  - **Complaints:**
    - Modelling tools non-intuitive.
    - Lag at around 1M triangles.
    - 3D cursor behaviour.
    - Scattered UI with small buttons.
    - Weak retopology.
    - Rigging: wants a port of Epic's A.R.T. rig toolkit.
    - Navigation: wants WASD.
    - Destruction and simulation tools.
    - Repliers: motion capture and file linking are production gaps; the tool panel is easy to miss.
  - **Prefers (repliers):** faster modelling, hotkeys, history.
  - **Outcome:** unknown.
  - [Source](https://blenderartists.org/t/blender-in-production-3ds-max-user-perspective/618120)
- **S9 — "Thoughts about blender 2.8 from a 3dsmax user and a blender teacher in architectural school"** (BlenderArtists), Apr 2019, **[2.80 beta]**.
  - **Complaints:**
    - Missing non-destructive modifiers: Edit Poly, Edit Spline, Sweep, Slice, Bend, Chamfer, UVW Map.
    - Bisect isn't a modifier.
    - Booleans produce artifacts and crash.
    - Curve bevel is weaker than Sweep.
    - Resizing a cube changes its scale to 2,2,2, needing Ctrl+A.
    - Students find it complex.
    - Archipack is hard to customise.
  - **Replier bassig:** Max's stack "may still be more powerful".
  - **Prefers:** speed and fun once learned, cheap add-ons, Sverchok.
  - **Outcome:** stayed (teaches Blender and refuses to teach Autodesk).
  - [Source](https://blenderartists.org/t/thoughts-about-blender-2-8-from-a-3dsmax-user-and-a-blender-teacher-in-architectural-school/1153944)
- **S10 — "Transitioning From 3dsmax to Blender"** (blog), Dec 28, 2014, **[pre-2.8]**.
  - **Complaints:**
    - The Max preset is partial; reaching vertex mode takes Tab then 1.
    - No Element or Border sub-object.
    - Right-click sets the cursor instead of opening a menu.
    - Primitives are created at the cursor, not dragged out.
    - Primitive parameters are "a one way street".
    - One active camera.
    - Smooth shading is not the default.
    - No Ctrl+Backspace edge collapse.
    - Renamed tools: Chamfer, Connect, Cut, Attach, Meshsmooth, Shell, Symmetry.
    - FFD vs separate Lattice object.
    - The pivot can't be dragged.
    - Groups ≠ Max groups.
    - No one-button Reset XForm.
  - **Prefers:** nothing explicit.
  - **Outcome:** unclear (kept learning).
  - [Source](https://blenderden.wordpress.com/2014/12/28/transitioning-from-3dsmax-to-blender/)
- **S11 — "3DS Max Like Edit Poly Modifier"** (devtalk), Apr 2022, **[3.x]**.
  - **Complaints:** wants Edit Poly above Solidify so generated faces can be edited (e.g. given materials) without applying it. A second user: "one of the few things I miss from Max too."
  - **Outcome:** n/a. No developer answer; redirected to Right-Click Select.
  - [Source](https://devtalk.blender.org/t/3ds-max-like-edit-poly-modifier/23989)
- **S12 — "…Stack design from 3ds max is the Mr. Right to Modifier Stack"** (devtalk), Jun 2020, **[2.8–2.9]**.
  - **Complaints:** the new modifier panel compresses everything into subpanels, so it takes lots of clicking to tweak.
  - **Outcome:** n/a.
  - [Source](https://devtalk.blender.org/t/not-being-offensive-but-stack-design-from-3ds-max-is-the-mr-right-to-modifier-stack-for-now/13878)
- **S13 — "Unity ArchViz: From 3dsmax to blender?"** (Unity forum), ~2020, **[2.8–2.9]**.
  - **Complaints:** few Max-specific ones. Community-only support; some animation tools (pole targets) awkward.
  - **Prefers:** EEVEE for fast archviz iteration; the studio's "artists actually prefer blender 2.8 to max and maya now"; cost.
  - **Outcome:** **hybrid** (the studio does about 60% of its work in Blender and that share is growing).
  - [Source](https://discussions.unity.com/threads/unity-archviz-from-3dsmax-to-blender.839323/)
- **S14 — "Blender or 3DS max: Which is the Best for Archviz in 2025?"** (CGArchitect/CGconnect article summarising a video by Oliver Higgins), Nov 19, 2024, **[3.x–5.x]**.
  - **Complaints:** steep learning curve; shortcut-heavy interface; struggles with large, complex scenes.
  - **Prefers:** free, plugins, community, good for small or medium projects.
  - **Outcome:** n/a.
  - [Source](https://cgconnect.chaos.com/features/articles/c685e73c-blender-or-3ds-max-which-is-the-best-for-archviz-in-2025?from=cgarchitect)
- **S15 — Steam Blender discussion** (shortcuts for Max users), Sep–Nov 2017, **[pre-2.8]**.
  - **Complaints:**
    - Shortcuts are confusing.
    - Tutorials assume Blender keys.
    - "Not just 'jump' to another software" (a Max user since 2003).
    - The Max preset misses Extrude and Hide.
  - **Outcome:** continuing ("working better everyday with blender").
  - [Source](https://steamcommunity.com/app/365670/discussions/0/1520386297686927961)
- **S16 — "15 years 3ds max veteran switching to Blender!"** (BlenderArtists), Mar 2013, **[pre-2.8]**.
  - **Complaints:**
    - No Align tool.
    - No Shift-drag clone with an Instance/Reference choice and a count.
    - No bevel along normal.
    - Two-axis constraint while extruding behaves oddly.
    - No warning on shortcut conflicts.
    - Interface drove him away on earlier attempts.
  - **Prefers:** "twice as fast" once shortcuts are learned, F2, retopology, linked duplicates, no licence fees.
  - **Outcome:** stayed (building a render farm).
  - [Source](https://blenderartists.org/t/15-years-3ds-max-veteran-switching-to-blender/570088)
- **S17 — "Long term Max user moving to Blender"** (BlenderArtists), Aug–Sep 2013, **[pre-2.8]**.
  - **Complaints:**
    - Shortcuts and menu layout are strange.
    - Can't drag-create objects.
    - No AutoGrid equivalent for cut-outs.
    - Unclear how to build floor plans.
    - A 10-year Max user called the UI "the most annoying piece of garbage ever" before coming round.
  - **Prefers:** spline tools (one replier), knife, Shift-D.
  - **Outcome:** stayed, "still struggling".
  - [Source](https://blenderartists.org/t/long-term-max-user-moving-to-blender/585249)
- **S18 — "3dsMax user, trying to switch to Blender"** (BlenderArtists), Sep 2015, **[pre-2.8]**.
  - **Complaints:** the N-panel shows offsets, not absolute coordinates (Transform Type-In habit); couldn't find the N panel.
  - **Prefers:** the interface after tweaks; free.
  - **Outcome:** undecided, also evaluating Modo and Maya.
  - [Source](https://blenderartists.org/t/3dsmax-user-trying-to-switch-to-blender/652421)
- **S19 — "[RANT] What I really REALLY hate about Blender as a 3ds Max user"** (Polycount), May 2020, **[2.8–2.9]**. *Snippet-based.*
  - **Complaints:**
    - Primitives' radius, height and segments can't be edited after creation.
    - Modifiers don't use the object's axis, so empties are needed (e.g. Mirror); a replier agrees.
    - UV tools are "the worst part": auto-unwrap angles, packing, no quick UV view on the model, no Preserve UVs, relax only via brush.
    - Curve handle types and adding points are awkward compared with Max splines; a replier says Max is "king" for splines.
  - **Prefers:** repliers cite shrinkwrap and UV projection; the OP likes Blender for basic modelling.
  - **Outcome:** **stayed** ("don't want to go back to max any time soon").
  - [Source](https://polycount.com/discussion/219632/rant-what-i-really-really-hate-about-blender-as-a-3ds-max-user)
- **S20 — "Moving to blender worth it?"** (Polycount), ~Aug 2023, **[3.x]**. *Snippet-based.*
  - **Complaints:**
    - A Max user since 2011 took "at least 2 years" to get comfortable.
    - Spline modelling is "still a lot better in Max".
    - Scripting.
    - Export and pipeline friction in game work.
  - **Prefers:** "few clicks less than in Max"; less hand strain (tap-to-transform); simpler viewport shading and shader editor; bmax add-on.
  - **Outcome:** stayed (no regrets), though studio pipelines still need Max or Maya.
  - [Source](https://polycount.com/discussion/233800/moving-to-blender-worth-it)
- **S21 — "Helping a large group transition from 3DS Max to Blender?"** (Polycount), 2019, **[2.80]**. *Snippet-based.*
  - **Complaints:** deploying a Max-like keymap to a team; premade keymaps hide what they changed; a Max preset makes tutorials harder to follow.
  - **Prefers:** BsMax, Machin3Tools, Keyhydra; mostly default keys.
  - **Outcome:** unknown.
  - [Source](https://polycount.com/discussion/212304/helping-a-large-group-transition-from-3ds-max-to-blender)
- **S22 — "Blender generic questions from a previous 3ds max user"** (Polycount), 2022, **[3.x]**. *Snippet-based.*
  - **Complaints:** no visual constraint gizmo during extrusion (the gizmo disappears); each segment needs extra steps.
  - **Outcome:** the OP remapped axis/plane keys and kept going.
  - [Source](https://polycount.com/discussion/231733/blender-generic-questions-from-a-previous-3ds-max-user)
- **S23 — "Any way to make blender control more like 3ds Max?"** (Steam), Sep 2020, **[2.90]**. *Borderline: the OP was learning Max, not a veteran.*
  - **Complaints:** MMB pans and Alt orbits in Max, but Blender differs; Max zooms toward the cursor and Blender doesn't ("very jarring").
  - **Outcome:** reluctantly accepted the Industry Compatible keymap advice.
  - [Source](https://steamcommunity.com/app/365670/discussions/0/4462460605170407592)
- **S24 — "Something like nondestructable 'edit mesh' modifier?"** (BlenderArtists), Jun 2023 – Feb 2025, **[3.x–4.x]**.
  - **Complaints:** can't edit vertices generated by Subdivision without applying it (Max Edit Mesh/Edit Poly style).
  - **Responses:**
    - Technical reasons it is hard.
    - A Dec 2024 "Modifier List [Fork]" add-on with an Edit Mesh modifier.
    - Note that Max's version can corrupt results when lower stack entries are edited.
  - [Source](https://blenderartists.org/t/something-like-nondestructable-edit-mesh-modifier/1470643)
- **S25 — "Importing 3ds max models to blender with textures"** (BlenderArtists), Feb–Aug 2026, **[3.x–5.x]** (Max 2024 / Blender 4.5). The OP has 15 years of Max.
  - **Complaints:**
    - Textures lost on OBJ, FBX, GLB, USD, .max and BMAX import.
    - Blender renames maps, so Find Missing Files fails.
    - BMAX "works only rarely".
    - The V-Ray/Corona asset library is unusable.
  - **Outcome:** **hybrid**. Max remains the source of the library; workaround is a MaxScript plus the BMAX Connector.
  - [Source](https://blenderartists.org/t/importing-3ds-max-models-to-blender-with-textures/1630285)
- **S26 — "BMax Tools or how I left 3ds Max"** (BlenderArtists add-on thread), Sep 2013, **[pre-2.8]**.
  - **What the author rebuilt (i.e. what he missed):**
    - Align dialog.
    - Clone Options (clone/array hybrid).
    - Mirror dialog.
    - Max-style per-mode context (quad-like) menus.
    - Select by Type.
    - Hide/unhide and freeze/unfreeze that preserve selection.
    - Target Weld, Make Planar.
  - **Complaints:** terminology and multi-step actions versus Max's one-click tools; select by type "a chore"; repliers want a Max-style array with cumulative or random transforms.
  - **Outcome:** stayed.
  - [Source](https://blenderartists.org/t/bmax-tools-or-how-i-left-3ds-max/586373)
- **S27 — "Edit Poly - Modificator"** (devtalk), Jul–Aug 2021, **[2.9x]**.
  - **Complaints:** a Max user must apply Subdivision before further edits, which forces many backup copies; wants Edit Poly in the stack.
  - **Outcome:** n/a.
  - [Source](https://devtalk.blender.org/t/edit-poly-modificator/19504)

### Inferences
- These threads are mostly about the first weeks of switching: keymap, navigation and finding things. Deep production complaints (Xrefs, render elements, Biped/CAT, MAXScript, Forest Pack/RailClone) are rare in switching threads. This is either because those users never get far enough to hit them, or because those complaints appear in feature-specific threads rather than switching threads.

### Gaps
- No Reddit data (blocked). Reddit is probably where most 2022–2026 switching threads live, so recent-era counts are likely undersampled.
- No YouTube transcripts were found or fetched.
- Polycount thread bodies were not readable; S19–S22 rely on search summaries.
- I found no CGSociety or CGArchitect forum switching threads.

## Q2. How often does each complaint appear (ranked by number of sources)?

### Takeaway
Out of 27 sources, by a wide margin the most frequent complaint is **keymap, navigation, shortcut reliance and the missing quad menu (15/27)**. Next, at about a fifth of sources each:
- **UI clutter and discoverability** (6)
- **The destructive modifier stack and the missing Edit Poly mid-stack** (6; 4 specifically about Edit Poly mid-stack)
- **Spline modelling** (5)
- **Learning curve and hotkey-centric tutorials** (5)

In the 2022–2026 subset (8 sources), keymap/shortcuts (3), .max/asset-library import (3) and learning curve (3) lead. Edit Poly mid-stack (2), spline modelling (2) and V-Ray/Corona (2) follow.

### Cited Findings — tally (distinct sources; source IDs refer to Q1)

| Rank | Complaint category | # sources (of 27) | Sources | # in 2022–26 subset (of 8) |
|---|---|---|---|---|
| 1 | Keymap / navigation / shortcut reliance / quad menu | 15 | S2, S3, S4, S5, S6, S7, S8, S10, S14, S15, S16, S17, S21, S23, S26 | 3 (S4, S5, S14) |
| 2 | *(new)* UI clutter / discoverability / hidden panels | 6 | S3, S4, S7, S8, S17, S18 | 1 (S4) |
| 2 | Modifier stack: destructive workflow / Edit Poly mid-stack / stack UI | 6 (Edit Poly mid-stack specifically: 4: S9, S11, S24, S27) | S5, S9, S11, S12, S24, S27 | 3 (S5, S11, S24) |
| 4 | Spline modelling (Edit Spline, Sweep, Bézier handles, spline terrain) | 5 | S1, S5, S9, S19, S20 | 2 (S5, S20) |
| 4 | *(new)* Learning curve / tutorials assume Blender hotkeys | 5 | S4, S9, S14, S15, S20 | 3 (S4, S14, S20) |
| 6 | *(new)* Parametric primitives (can't edit after creation; no drag-create) | 4 | S5, S10, S17, S19 | 1 (S5) |
| 6 | *(new)* Transform gizmo / modal sticky transforms / constraints while extruding | 4 | S2, S7, S16, S22 | 1 (S22) |
| 6 | Transform Type-In / snapping / reference coord systems / AutoGrid | 4 | S3, S6, S17, S18 | 0 (S3's 2022 reply aside) |
| 9 | Edit Poly tools (Element/Border, collapse, bevel along normal, Target Weld) | 3 | S10, S16, S26 | 0 |
| 9 | Pivot handling / 3D cursor | 3 | S3, S8, S10 | 0 |
| 9 | Heavy-scene performance | 3 | S1, S8, S14 | 1 (S14) |
| 9 | .max / CAD / asset-library import and export pipeline | 3 | S5, S20, S25 | 3 (S5, S20, S25) |
| 9 | *(new)* Terminology differences (weld/merge, chamfer/bevel…) | 3 | S3, S10, S26 | 0 (S3's 2022 reply aside) |
| 9 | *(new)* Add-on dependence / add-on fragility or cost | 3 | S1, S6, S25 | 1 (S25) |
| 15 | Slate / Multi-Sub / node materials (preview, layering, Blend mtl, "node spaghetti") | 2 | S4, S6 | 1 (S4) |
| 15 | UVW Map modifier / real-world box mapping | 2 | S5, S9 | 1 (S5) |
| 15 | V-Ray / Corona | 2 | S5, S25 | 2 |
| 15 | Align / Array / Spacing / Clone options | 2 | S16, S26 | 0 |
| 15 | Layers / Scene Explorer / Freeze / selection sets / groups / select-by-type | 2 | S10, S26 | 0 |
| 15 | Modifier gizmos / modifier axis (empties needed; FFD vs Lattice) | 2 | S10, S19 | 0 |
| 15 | *(new)* Object scale vs dimensions / Reset XForm | 2 | S9, S10 | 0 |
| 15 | *(new)* Sculpting / retopology weak (old-era) | 2 | S1, S8 | 0 |
| 15 | *(new)* Particles / destruction / simulation | 2 | S6, S8 | 0 |
| 24 | Smoothing groups | 1 (2 if S10's "smooth shading not default" is counted) | S3 | 0 |
| 24 | Instances vs references | 1 | S16 | 0 |
| 24 | Unwrap UVW / UV editing tools | 1 | S19 | 0 |
| 24 | Plugins (Forest Pack etc.) | 1 | S5 (keeps Max for Forest Pack + V-Ray) | 1 |
| 24 | Xrefs / file linking | 1 (weak) | S8 | 0 |
| 24 | Biped / CAT / rigging | 1 | S8 | 0 |
| 24 | MAXScript / scripting | 1 | S20 | 1 |
| 24 | *(new)* Soft-selection parameters | 1 | S6 | 0 |
| 24 | *(new)* Baking (displacement) | 1 | S1 | 0 |
| — | Render elements / camera correction | 0 | — | 0 |

Supporting evidence for selected rows:
- **Keymap complaint versus fix.** The common fix offered is the Industry Compatible or Max keymap. Several Max users still report it as partial ("some shortcuts, such as Extrude and Hide, did not match") — [S15](https://steamcommunity.com/app/365670/discussions/0/1520386297686927961); also [S10](https://blenderden.wordpress.com/2014/12/28/transitioning-from-3dsmax-to-blender/).
- **Edit Poly mid-stack is the most specific recurring modelling request.** It appears across 2019–2025 and was never answered by developers. Requesters are pointed to Right-Click Select or to geometry nodes — [S11](https://devtalk.blender.org/t/3ds-max-like-edit-poly-modifier/23989), [S27](https://devtalk.blender.org/t/edit-poly-modificator/19504), [S24](https://blenderartists.org/t/something-like-nondestructable-edit-mesh-modifier/1470643).
- **Archviz-specific complaints concentrate in 2026 sources:** splines, UVW Map, asset library, V-Ray/Corona — [S5](https://forums.chaos.com/t/replacing-3dsmax-with-blender-for-archviz/124304), [S25](https://blenderartists.org/t/importing-3ds-max-models-to-blender-with-textures/1630285).

### Inferences
- The categories proposed in the brief that rarely or never appeared are:
  - Xrefs/containers
  - Render elements/camera correction
  - Biped/CAT
  - Forest Pack/RailClone/tyFlow/Phoenix
  - MAXScript
  - Units/precision
  - Smoothing groups

  They are probably real but **under-represented by this method** because they surface in feature-specific threads (see sibling research) or on Reddit/CGArchitect, which I could not survey. Treat their low counts as "not prominent in switching narratives", not "not a problem".
- Several old-era complaints are likely stale for Blender 4.x/5.x:
  - Sculpting and retopology weakness (2013–2018).
  - Heavy-mesh lag in 2.71 and 2.80.
  - "Autosave missing" (which was wrong even then).
  - Gizmo absence: Blender 2.80+ has transform gizmos ([S22](https://polycount.com/discussion/231733/blender-generic-questions-from-a-previous-3ds-max-user) notes the gizmo exists but disappears during extrude).
- Complaints that recur across all eras are the most robust signals:
  - Keymap/navigation
  - Splines
  - Parametric primitives
  - The destructive stack / Edit Poly mid-stack

### Gaps
- Counts are small. One source more or less changes ranks from #4 downward, so ranks below #2 are not statistically meaningful.
- Snippet-based sources (S19–S22) may under-count complaints.

## Q3. What do Max users prefer in Blender, and did they stay or go back?

### Takeaway
Of 27 sources:
- **10 report the user stayed** with Blender (some tentatively).
- **4 are hybrid** (Max kept for modelling, the asset library, or Forest Pack/V-Ray rendering).
- **1 includes a clear abandonment** (S5's OP, moving to Cinema 4D over splines and procedural modelling).
- The rest are unknown or not applicable.

The most-cited preferences are:
- Speed once shortcuts are learned.
- Stability compared with Max crashes.
- Built-in sculpting and EEVEE.
- Edit-mode integration of UVs and weights.
- F3 search.
- Cost.

Bridging add-ons (BsMax/Bmax) are recommended in about 8 sources, but are also criticised as incomplete.

### Cited Findings
- **Outcome tally:**
  - **Stayed:** S1, S2, S3 (tentative), S7 (likely), S9, S16, S17, S19, S20, S26 = 10.
  - **Hybrid:** S6 (Max for modelling), S13 (studio ~60% Blender), S25 (Max as library source), plus S5's Mokiki and bardo (Max kept for Forest Pack/V-Ray, or a token licence for old projects) = 4 sources.
  - **Abandoned:** S5's OP Vizioen, "I guess Blender is out of the picture" = 1.
  - **Unknown/n.a.:** S4, S8, S10, S11, S12, S14, S15, S18, S21, S22, S23, S24, S27.
  - Sources: [S5](https://forums.chaos.com/t/replacing-3dsmax-with-blender-for-archviz/124304), [S6](https://blenderartists.org/t/blender-newbie-questions-from-someone-coming-from-3ds-max/1310339), [S13](https://discussions.unity.com/threads/unity-archviz-from-3dsmax-to-blender.839323/), [S25](https://blenderartists.org/t/importing-3ds-max-models-to-blender-with-textures/1630285)
- **Speed and fewer clicks once learned:**
  - "twice as fast" — [S16](https://blenderartists.org/t/15-years-3ds-max-veteran-switching-to-blender/570088)
  - "few clicks less than in Max" — [S20](https://polycount.com/discussion/233800/moving-to-blender-worth-it)
  - faster, more fun — [S9](https://blenderartists.org/t/thoughts-about-blender-2-8-from-a-3dsmax-user-and-a-blender-teacher-in-architectural-school/1153944)
- **Stability versus Max crashes** — [S1](https://blenderartists.org/t/my-thought-so-far-after-switching-from-3ds-max/1127006); also a 2022 replier calling Max's stacked character modifiers crash-prone — [S3](https://blenderartists.org/t/3ds-max-blender/688049)
- **Built-in sculpting and unfiltered viewport textures** — [S2](https://blenderartists.org/t/moving-to-blender-from-3ds-max/1100657)
- **EEVEE for fast iteration** — [S6](https://blenderartists.org/t/blender-newbie-questions-from-someone-coming-from-3ds-max/1310339), [S13](https://discussions.unity.com/threads/unity-archviz-from-3dsmax-to-blender.839323/)
- **UV, weight and mesh editing integrated in Edit Mode** (rather than topology-dependent modifiers) — [S3](https://blenderartists.org/t/3ds-max-blender/688049)
- **Selection tools:**
  - Path select and vertex/edge extrude — [S2](https://blenderartists.org/t/moving-to-blender-from-3ds-max/1100657)
  - Selection conversion — [S7](https://blenderartists.org/t/yet-another-3ds-max-user-struggling-to-blend-in/677494)
- **Ergonomics** (tap-to-transform, less hand strain) — [S20](https://polycount.com/discussion/233800/moving-to-blender-worth-it)
- **F3 search, menus showing shortcuts, Quick Favorites** — [S4](https://blenderartists.org/t/hi-new-blender-user-here-coming-from-a-3ds-max-background-small-question-regarding-interface/1527510)
- **Cost and no licence fees** — [S16](https://blenderartists.org/t/15-years-3ds-max-veteran-switching-to-blender/570088), [S13](https://discussions.unity.com/threads/unity-archviz-from-3dsmax-to-blender.839323/)
- **Bridging add-ons:**
  - BsMax/Bmax recommended in S1, S3, S4, S6, S20, S21 and S26 (author-built).
  - Criticised as incomplete or unhelpful in S4 ("little value beyond Align Object") and S25 ("works only rarely").

### Inferences
- The pattern resembles survivorship: users who post update threads tend to have stayed, and those who quit rarely post. The low abandonment count (1) is therefore likely an undercount.
- Hybrid outcomes cluster in archviz and asset-library contexts (S5, S13, S25). Lock-in by asset library and plugins, not modelling UX, seems to be what keeps Max in the pipeline.
- Modelling-UX complaints are what make some users keep Max for modelling (S6) or leave Blender (S5).

### Gaps
- No data on long-term retention, i.e. whether "stayed" users were still using Blender years later.
- No Reddit "I went back to Max" threads could be checked.
