# Moritz Roadmap

Moritz is a fork of Blender that sits between 3ds Max and Blender: Blender's engine, data model and speed, with the modeling workflow, scene handling and vocabulary that Max users expect.

Base: Blender `blender-v5.3-release` @ `4768a6eac54` (5.3 beta, version 503; release due 2026-11-04), cloned 2026-10-22 into `blender/`. Merge 5.4 after its release (alpha until 2027-02-03).
Evidence: [reports/Max user complaints about Blender.md](reports/Max%20user%20complaints%20about%20Blender.md).

## Principles

1. **Core changes only where an add-on can't do it.** Everything else ships as an add-on (`maximize`, its own repository; Moritz runs without it), which keeps the fork's own C++ changes small and easy to rebase.
2. **Stay rebasable on upstream.** Track Blender release branches. Core patches stay isolated and documented, so each upstream release can be merged in days, not weeks.
3. **Blender files stay Blender files.** A `.blend` saved by Moritz must open in stock Blender. Moritz-only data degrades gracefully, for example an Edit Poly modifier collapses to its evaluated mesh.
4. **Max habits are the default, Blender habits are one switch away.** Tutorials for stock Blender must stay usable.
5. **Legal:** GPL v3 for the whole program, source published with every build, no Blender or Autodesk branding.

## Phases

### Phase 0 — Foundation
Goal: Moritz builds, runs and is clearly its own app.
- Own repository and branching model; upstream remote; full history (unshallow).
- Windows build (`make.bat`) with the precompiled libraries; CI build.
- Rebrand: name, splash, icons, window title, and a separate config directory (`%APPDATA%\Moritz`) so Moritz never touches a user's Blender settings.
- GPL compliance: license notices, a source offer, and a "based on Blender" credit.

### Phase 1 — Feels like Max (add-on `maximize`) — done
Goal: a Max user can open Moritz and navigate, select, transform and model on day one.
Top complaints addressed: keymap and navigation (15/27 sources), UI discoverability (6), learning curve (5), editable primitives (4), transform gizmo and Type-In (4).
- Max keymap and quad menu (default), with a one-click switch back to the Blender keymap.
- Max vocabulary: labels, tooltips and F3 search aliases (Weld, Chamfer, Attach, Collapse, Swift Loop…) through a "Max English" translation.
- Startup file: quad view, Max-like viewport navigation, scene units, Max-style command panel layout.
- Transform Type-In (F12), Reset XForm, Affect Pivot Only, Align (Alt+A), Array dialog, Spacing tool, Isolate (Alt+Q), Select by Name (H).
- Editable (parametric) primitives that collapse to a mesh on demand.
- UVW Map modifier with Box/Cylinder/Planar projection and real-world size.
- Named selection sets.

### Phase 2 — The stack (core)
Goal: Max's non-destructive modeling, the biggest unfixed gap (6/27 sources, never answered upstream).
- **Edit Poly modifier:** a real C++ modifier that holds manual edits anywhere in the stack, with sub-object editing (Tab into it) and robust topology tracking when the modifiers below it change.
- **Collapse To / Collapse All** on the stack.
- Unwrap UVW as a stack modifier (built on the Edit Poly machinery).
- Modifier gizmos for Bend, Taper, Twist and FFD as sub-objects of the modifier, not empties.

### Phase 3 — Splines
Goal: Max-grade shape modeling (5/27 sources; a January 2026 archviz user left for Cinema 4D over it).
- Editable Spline tools: fillet, chamfer, outline, trim/extend, weld, refine, 2D shape booleans.
- Shape modifiers: Extrude, Lathe, Sweep, Loft, Renderable Spline.
- Spline drawing with snapping, AutoGrid and Max-style vertex types (Corner, Smooth, Bezier, Bezier Corner).

### Phase 4 — Scene and data (core)
Goal: archviz-scale scenes and Max's scene management.
- Scene Explorer as its own editor: layers, Freeze, Display as Box, See-Through, sortable columns.
- Freeze as a true display state (greyed, unselectable) in every shading mode.
- Instance vs Reference: instances that share their modifier stack; Make Unique.
- Smoothing groups as mesh data, with Max-compatible FBX round trips.
- Imperial units with fraction display and input (`3' 4 1/2"`).
- Heavy-scene performance: 10k+ objects in the Outliner/Scene Explorer, undo and selection.

### Phase 5 — Pipeline and release
Goal: a Max studio can move a real project into Moritz.
- Bundle and extend the `.max` importer; V-Ray/Corona material conversion.
- Max-compatible FBX defaults (units, axes, smoothing).
- Installer, auto-update, "Moritz for Max users" docs, and video onboarding.
- Public 1.0.

## Out of scope
- **Corona:** its developers name the GPL as the obstacle, and that applies to a GPL fork too.
- **Clones of Forest Pack, RailClone and tyFlow:** Geometry Nodes and existing add-ons (Geo-Scatter) cover most of this; revisit after 1.0.
- **MAXScript interpreter:** low demand (0–1 sources); Python stays the scripting language.
- **Biped/CAT:** Max riggers themselves rate them poorly; Rigify plus a Max-named rig preset is enough.

## Competitors to watch
- **MAXStack** ($20, Superhive, Oct 2026): Edit Mesh mid-stack, splines and UV Map as an add-on. Phase 2 has to beat it on robustness.
- ****: Max keymap, quad menuBsMax, Align and Array. Phase 1 has to beat it on polish and integration.
- **MaxStyle Modifier**: Extrude, Shell, Sweep and a real-world UVW Map.

## Risks
- **Upstream drift:** core patches in the modifier stack and the Outliner touch code that changes every release. Mitigation: small, isolated patches; merge every Blender release.
- **Keymap backlash:** a Max keymap makes stock Blender tutorials harder to follow. Mitigation: a visible keymap switch, and F3 aliases that work under both keymaps.
- **Edit Poly topology tracking** is a research problem. Mitigation: build a prototype first (Phase 2, first task), and set a fallback that rebases edits by position when topology tracking fails.
- **File compatibility:** a new modifier type in DNA must not corrupt files opened in stock Blender.
