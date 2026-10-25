# Splines and shapes as Max builds them (measured, 2026-10-25)

Source: 3ds Max 2026, measured headless (`3dsmaxbatch`). Each shape was created with known
parameters, converted to Editable Spline, and every knot dumped (position, in/out vector, knot
type, segment type). The scripts and raw data stay outside the repo. A static look at
`stdplugs/prim.dlo` (REA/Ghidra, no PDB) confirmed one fact only: the circle handle constant
below is a hard-coded float, read from 11 places in the shape code. The arc, helix and star rules
below were fitted to the measurements. No Autodesk code was copied
or is needed. Everything here is observed behaviour, which Moritz re-implements.

Feeds Phase 3b in [TASK.md](../TASK.md).

## Defaults (all shape classes, Line included)

Interpolation: Steps 6, Optimize on, Adaptive off. Helix has no Steps/Optimize: its knots are
already dense (see below).

## Handle length

- **Circle-type quarter arcs** (Circle, Ellipse, Donut, Arc and Ngon-circular 90° pieces):
  handle = **0.5517861843 × r**, not the textbook 4/3·tan(22.5°) = 0.55228. Ellipse uses the
  same factor per semi-axis (20 × 10 ellipse: 5.5179 along x, 2.7589 along y).
- **Arcs of other angles**: the arc is always **4 knots / 3 equal segments**, whatever the
  angle (10°…359° measured). Handle per segment of angle φ, as a fraction of r:

  | φ | 3.33° | 10° | 20° | 30° | 40° | 60° | 90° | 119.67° |
  |---|---|---|---|---|---|---|---|---|
  | Max | 0.019398 | 0.058216 | 0.116652 | 0.175535 | 0.235095 | 0.357204 | 0.551786 | 0.764937 |
  | 4/3·tan(φ/4) | 0.019394 | 0.058215 | 0.116652 | 0.175537 | 0.235103 | 0.357266 | 0.552285 | 0.767217 |

  Max equals 4/3·tan(φ/4) up to about 30° and then falls slightly below it (−0.09 % at 90°,
  −0.3 % at 120°). **Rule that reproduces the whole table to 1e-6:** the handle length at which
  the mean distance from the centre of the 10 samples at t = 0, 0.1, …, 0.9 equals the radius
  (found by bisection). At 90° that gives exactly 0.5517861843, the circle constant.
  `maximize/shapes.py` `arc_handle()`.
- **Fillets** (Rectangle corner radius, Ngon corner radius, Star fillets): handle =
  **0.5517861843 × tangent distance**, where tangent distance = fillet radius × tan(turn/2).
  Rectangle r = 2 → 1.1036. Ngon (6 sides, 60° turn) r = 2 → distance 1.1547 → handle 0.6371.
- **Straight segments** (Rectangle and Ngon sides): handles at **1/3 of the segment**, so the
  segment is an exact straight line that stays a Bezier curve.

## Per shape

| Shape | Knots | Knot type | Notes |
|---|---|---|---|
| Circle r | 4 at 0/90/180/270°, first at +X | Bezier | CCW |
| Ellipse | 4, first at +X | Bezier | Width = X, Length = Y |
| Donut | 2 splines × 4 | Bezier | outer first |
| Arc | 4 (3 segments), open | Bezier | first knot's in-vector and last knot's out-vector = 0. Pie: closed, 5 knots (+centre) |
| Rectangle, no radius | 4, first at (+w/2, +l/2) | Bezier Corner | 1/3 handles, CCW |
| Rectangle, radius | 8 | Bezier Corner | fillet rule above |
| Ngon N | N, first at +X | Bezier Corner | Inscribed (`scribe` 0, the default): the radius circle touches the sides, so the corners are at r / cos(180°/N). Circumscribed (1): the corners are at r |
| Ngon, corner radius | 2N | Bezier | fillet rule |
| Ngon, Circular | N | Bezier | arc handles for 360°/N |
| Star N points | 2N, first on Radius 2 at +X | Bezier, **zero-length handles** | alternates Radius 2 / Radius 1 (Max's points are Radius 1) |
| Star, fillets | 4N | Bezier | tangent distance = the fillet radius itself; Distortion turns the Radius 2 points |
| Helix | ceil(40 × Turns) segments, open | Corner, 1/3 handles | effectively a polyline. Direction 0 = CW. The radius is linear along the helix. Bias b: z = 1 − (1 − u)^(1 + 9b) for b > 0, u^(1 + 9|b|) for b < 0 |

**Star quirk:** with Distortion and fillets, Max does not fillet the corners it draws. A Radius 2
point's fillet vertices go towards the previous Radius 1 point unturned and the next one turned
by **2 ×** Distortion. A Radius 1 point's fillet vertices go towards the unturned Radius 2
points. So the filleted sides of a distorted star are slightly curved. Moritz reproduces this
(all 24 knots to 1e-5); without fillets, or without Distortion, it is plain geometry.
| Egg | 11, × 2 with Outline | Bezier | circular arcs, in units of half the width w: bottom radius w around (0, −0.3w) in 2 segments; sides radius 3w around (∓2w, −0.3w) up to 36.87° in 3; top radius w/2 around (0, 1.2w) in 3. The outline is the same arcs Thickness further out. Length is tied to the width (1.5 w). |

The default first-knot rotation and the CCW direction are what make Max's Loft, Sweep, Path
Deform and "Make First" results line up. Moritz has to match them.

## Knot types to Blender handles

| Max | Blender |
|---|---|
| Corner | Vector |
| Smooth | Auto |
| Bezier | Aligned |
| Bezier Corner | Free |

Zero-length Bezier handles, as on the plain Star, are Free handles on the knot itself. Blender
points the outer handle of an open spline's end vertex outward, while Max leaves it on the
vertex, so those two vertices are Free.

## Status in Moritz (2026-10-25)

`maximize/shapes.py` builds every shape above as Bezier splines. `tests/test_shapes_max.py`
compares them with the Max 2026 dump (`tests/data/max2026_shapes.json`): all match to 1e-5.
Steps map to the curve resolution (Steps + 1), and Thickness maps to a round bevel.
**Not done:** Optimize and Adaptive (no Blender setting; needs a curve tessellation change),
Egg is built since 2026-10-25 and matches to 1e-4.

## Modifier stack (how Max structures it, from the public SDK docs)

These facts come from the public SDK documentation, not from REA.

- Every object is evaluated as **base object → object-space modifiers bottom-up → world-space
  modifiers**. Blender's stack has the same order, so no change is needed.
- **Channels**: each modifier declares which channels it changes (geometry, topology, texture,
  selection, …) and which it needs. Only those channels are re-evaluated, and the others pass
  through cached. Blender's closest equivalent is the per-modifier depsgraph flags. Moritz already
  caches below Edit Poly through the session (stage 3).
- **Sub-object selection travels up the stack**: Edit Spline / Edit Poly / Mesh Select pass
  their selection to the next modifier. A modifier above acts on that selection only. The
  Maximize Edit Poly already follows this rule; Edit Spline must follow it too.
- **Shape modifiers** (Edit Spline, Normalize Spline, Fillet/Chamfer, Renderable Spline, Sweep,
  Extrude, Lathe) take a shape in. Extrude, Lathe and Sweep give out a mesh or poly. Blender's
  curve modifier stack does not support this split, so Moritz implements shape modifiers in
  Geometry Nodes on the curve. Extrude, Lathe and Sweep already work that way in Maximize.

## Files

A Curve object with Bezier splines and Blender handle types is plain Blender data. Stock
Blender shows the converted shape and loses only parameter editing. That edit stays in the
add-on, so a rebuild is not needed.

## Max scene import of shapes

The exporter writes each shape's knots in node space, with Max's knot and segment types and every
shape parameter. Known classes come back parametric. Others come back as exact Bezier splines:
- Max's Smooth and Bezier knots become Aligned, unless a handle has zero length; then they are Free.
- Corner and Bezier Corner knots become Free.

Max's own handle positions are kept, because Blender's Auto handles differ from Max's Smooth ones.
On Max line segments the handles are ignored, so Moritz puts them on the line.
`Maximize/tests/test_max_shapes_import.py` checks a Max 2026 export to 1e-5.

## Edit Spline modifier

**Stage 0 (add-on, done 2026-10-25, `maximize/edit_spline.py`):** a Geometry Nodes modifier,
"MX Edit Spline", with two hidden helper curve objects, as the Edit Poly prototype:
- **Base** is the input at the last edit; **Edited** is the edited splines.
- Each edited knot keeps its base knot index in its **tilt**: legacy curves have no custom point
  attributes. Subdivided knots get an in-between tilt and count as new.
- While the input knot count equals Base's, every edited knot and its handles move by
  input[orig] − base[orig]. Shape parameters below therefore carry the edits along.
- Otherwise the edit is frozen and the panel warns. Editing again re-bases: each edited knot then
  follows the nearest new input knot.
- 1, 2 and 3 edit at the modifier, on the Edited stand-in, with every Editable Spline tool; 6 or
  the level key returns to the object.

*Files:* a Geometry Nodes modifier plus helper objects; stock Blender evaluates them unchanged.
Test: `Maximize/tests/test_edit_spline.py`.

**Core stages (planned, same path as Edit Poly):**

| Stage | Content |
|---|---|
| 1 | Native `EDIT_SPLINE` modifier (type 201, plain `ModifierData`, data in `system_properties` like Edit Poly, so it is file-safe in stock). `modify_geometry_set` on the curves: per-knot offsets when the knot count and topology hash hold, else the stored result curves. RNA `store(input, edited)`. |
| 2 | Edit session on the object itself: Edit Mode builds the edit-nurbs from the stored result (`ED_curve_editnurb_make` from the result instead of `cu->nurb`), and the load writes back into the modifier. The stand-in object and the tilt trick go away. |
| 3 | The add-on drives the native modifier when present; it migrates the stage-0 setups. |

The stand-in swap is the weak point of stage 0: the Outliner and selection briefly see another
object. Stage 2 removes it, as Edit Poly's stage 3 did.
