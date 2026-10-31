#########
Edit Poly
#########

Sub-object levels
=================

Press **1–5** for Vertex, Edge, Border, Polygon, Element; **6** (or Tab) goes back to the object.
The 3D Viewport header shows the five levels. Pressing a level on a parametric object or another
mesh converts it to an editable mesh.

The Modify tab
==============

At a level the Modify tab shows Max's rollouts:

* **Selection:** the levels, Grow / Shrink, Loop / Ring, Dot Loop / Dot Ring, Similar, Fill,
  Outline, Ignore Backfacing, By Angle, and Select By (NonQuads, Open, Random, Symmetry).
* **Soft Selection:** Blender's proportional editing in Max's words.
* **Edit Geometry:** Repeat Last, Attach, Detach, Collapse, Cut, QuickSlice, Slice Plane, Make
  Planar X / Y / Z, Relax, Hide / Unhide, Named Selections Copy / Paste, Preserve UVs, Show Cage,
  To View / To Grid, Geometry (All), Subdivision.
* **Edit Vertices / Edges / Borders / Polygons / Elements:** the level's tools: Extrude, Chamfer,
  Weld, Target Weld, Connect, Remove, Break, Split, Bridge, Cap, Inset, Bevel, Outline, Hinge From
  Edge, Extrude Along Spline, Insert Vertex, Create Shape, Turn and more.
* **Loops** (Edge level): Insert / Remove Loop, Set Flow, Build End / Corner, Distribute, Center,
  Straighten, Circle, Curve.
* **Material IDs** and **Smoothing Groups** (Polygon and Element level).
* **Paint Deform:** Shift, Push/Pull, Relax, Flatten, Pinch, Smudge, Noise, Exaggerate brushes.

The **+** next to a rollout's title runs the last tool again (Apply and Continue).

Cap
---

Cap fills a border with a quad grid. Ctrl+click makes one n-gon (Max's cap), Shift+click an inset
ring with a quad grid inside.

Caddy
-----

**Preferences > Interface > Editors > Tool Settings** chooses where a tool's values appear: Blender's
Adjust Last Operation panel (the default) or Max's caddy at the selection, with OK, Apply and
Continue and Cancel.

Editable Poly and the Edit Poly modifier
========================================

An **Editable Poly** is the mesh itself. The **Edit Poly modifier** keeps your edits in the stack:
the modifiers below stay live, and the edit follows them while their topology doesn't change
(Moritz warns when it does). Collapse To / Collapse All bakes the stack.

On instances, Edit Poly is shared as in Max: editing it on one instance edits all.

Files
=====

Blender keeps the Edit Poly modifier in the file (disabled) and saves it back; Moritz revives it.

.. seealso:: :blender:`Mesh editing <modeling/meshes/editing/index.html>`
