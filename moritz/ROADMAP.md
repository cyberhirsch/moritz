# Moritz Roadmap

Moritz is a fork of Blender that sits between 3ds Max and Blender: Blender's engine, data model and speed, with the modeling workflow, scene handling and vocabulary that Max users expect.

Base: Blender `blender-v5.3-release` @ `4768a6eac54` (5.3 beta, version 503; release due 2026-11-04), cloned 2026-10-22. Merge 5.4 after its release (alpha until 2027-02-03).
Evidence: [research/Max user complaints about Blender.md](research/Max%20user%20complaints%20about%20Blender.md).

## Principles

1. **Only change what works better in Max.** Where Blender already does the job well, keep Blender's way (at most a shortcut or quad-menu entry). Build only the gaps where Max is clearly better.
2. **Core changes only where an add-on can't do it.** The Max workflow ships as the add-on Maximize (its own repository); Moritz runs without it and keeps its own C++ changes small and easy to rebase.
3. **Stay rebasable on upstream.** Track Blender release branches. Core patches stay isolated and listed in [PATCHES.md](PATCHES.md), so each upstream release can be merged in days, not weeks.
4. **Blender files stay Blender files.** A `.blend` saved by Moritz opens in stock Blender. Moritz-only data degrades gracefully.
5. **Three keymaps, chosen at first start:** Blender, Max and Moritz (default). Stock Blender tutorials must stay usable.
6. **Legal:** GPL for the whole program, source published with every build, no Blender or Autodesk branding.

## Phases

Order: finish what makes Moritz usable every day, then the biggest unsolved gap (Edit Poly in the stack), then splines, then the core gaps no add-on can fill, then release.

### Phase 0 — Foundation — mostly done
Goal: Moritz builds, runs and is clearly its own app.
- Done: own repository with full history, Windows build, rebrand (name, `moritz.exe`, splash, icons, About, title, version 0.1 Alpha), own settings folders, tabbed docking.
- Left: CI build, a debug build for core work, a final sweep for Blender branding, hand test and polish of docking.

### Phase 1 — Feels like Max (Maximize + Moritz keymaps) — nearly done
Goal: a Max user can navigate, select, transform and model on day one.
Addresses: keymap and navigation (15/27 sources), terminology (3), editable primitives (4), Type-In and pivot (4), Align/Array/Clone (2), UVW Map (2).
- Done: Max and Moritz keymaps in Moritz (136 of 216 Max keys, 0 conflicts), chosen at first start; quad menu; Max vocabulary; Type-In, Align, Array, Spacing, Clone, Reset XForm, Select by Name, selection sets; editable primitives; UVW Map; sub-object levels with Border and Element.
- Left: the rest of the Moritz selection behavior, both shortcuts shown in menus and tooltips (keeps Blender tutorials usable), numpad views, hand test.

### Phase 2 — Edit Poly in the stack
Goal: Max's non-destructive modeling, the biggest unsolved gap (6/27 sources, never answered upstream).
- First as a prototype in Maximize: a Geometry Nodes "Edit Poly" that stores the edited mesh and applies edits as offsets while the topology below is unchanged (Max's own behavior), with Tab into it, Collapse To and Collapse All.
- Then in the core, once the workflow is right: editing directly on the evaluated mesh, speed on heavy meshes, Max's five sub-object select modes in the header (Border and Element as real modes).
- Kept from Blender: the modifier panel itself (no Max-style stack list) and the UV editor (no Unwrap UVW modifier).

### Phase 3 — Splines (only where Max is better)
Goal: Max-grade shape modeling (5/27 sources; a January 2026 archviz user left for Cinema 4D over it).
- Parametric shapes (Rectangle with corner radius, Circle, Arc, NGon, Star, Helix, Donut), a precise line tool (click for corner, drag for Bezier, with snapping), Fillet/Chamfer on vertices, Outline, Refine, Trim/Extend.
- Then 2D shape booleans (may need a C++ 2D clipper) and Loft.
- Kept from Blender: handle types, curve extrude and bevel, Screw for Lathe, text objects.

### Phase 4 — Core gaps no add-on can fill
Goal: the features that make Moritz more than "Blender plus an add-on", smallest first.
- Imperial units with fraction display and input (`3' 4 1/2"`).
- Freeze as a display state (greyed, unselectable) with a column in the Outliner.
- Smoothing groups as mesh data with Max-compatible FBX round trips.
- Instances that share their modifier stack; Make Unique.
- Gizmos for Bend, Taper, Twist and FFD as part of the modifier.
- Heavy-scene performance (10k+ objects: Outliner, undo, selection).

### Phase 5 — Pipeline and release
Goal: a Max studio can move a real project into Moritz.
- Bundle an existing `.max` importer and material converter instead of building one; "From/To 3ds Max" FBX presets.
- Installer, update path, "Moritz for Max users" docs and onboarding.
- Public 1.0.

## Out of scope
- **Rebuilding what Blender already does well** (principle 1): a Max-style stack list, an Unwrap UVW modifier, a separate Scene Explorer editor, Max names for curve handle types.
- **Corona:** its developers name the GPL as the obstacle, and that applies to a GPL fork too.
- **Clones of Forest Pack, RailClone and tyFlow:** Geometry Nodes and existing add-ons (Geo-Scatter) cover most of this; revisit after 1.0.
- **MAXScript interpreter:** low demand (0–1 sources); Python stays the scripting language.
- **Biped/CAT:** Max riggers themselves rate them poorly; Rigify plus a Max-named rig preset is enough.

## Competitors to watch
- **MAXStack** ($20, Superhive): Edit Mesh mid-stack, splines and UV Map as an add-on. Phase 2 has to beat it on robustness.
- **BsMax**: Max keymap, quad menu, Align and Array. Phase 1 has to beat it on polish and integration.
- **MaxStyle Modifier**: Extrude, Shell, Sweep and a real-world UVW Map.

## Risks
- **Upstream drift:** core patches in the modifier stack and the Outliner touch code that changes every release. Mitigation: small, isolated patches; merge every Blender release.
- **Keymap backlash:** a Max keymap makes stock Blender tutorials harder to follow. Mitigation: the keymap choice at first start, both shortcuts shown in menus and tooltips, and F3 aliases that work under every keymap.
- **Edit Poly topology tracking** is a research problem. Mitigation: a Maximize prototype first (Phase 2), with Max's own index-based behavior and a warning when the topology below changes.
- **File compatibility:** a new modifier type in DNA must not corrupt files opened in stock Blender.
