########
Freeform
########

Max's Freeform tools, for retopology and painting on surfaces.

Freeform modifier
=================

**Add Modifier > Freeform** keeps the mesh on a **Draw On** surface (Surface object, Offset,
Conform strength). Its panel holds Max's PolyDraw:

* **Drag**, **Step Build**, **Extend**, **Optimize**
* **Conform** brushes: Conform, Conform Move, Conform Rotate, Conform Scale, Conform Relax. The
  direction dropdown sets how vertices reach the surface: **Target** (the surface normal under the
  brush), **Active Object** (the mesh's own normals), **Nearest** (closest point) or **View**.
* **Strips**, **Surface**, **Shapes**, **Topology**, **Branches**, **Splines**
* **Draw On:** Grid, Surface or Selection

Conform brushes also start from Object Mode; they enter Edit Mode for the stroke.

Brushes never block the interface: buttons work while a brush runs, right-click ends it.

Paint Deform
============

In Edit Poly, the **Paint Deform** rollout paints the mesh directly: Shift, Shift Rotate, Shift
Scale, Push/Pull, Relax/Soften, Flatten, Pinch/Spread, Smudge, Noise, Exaggerate, Revert.
Right-click or Enter commits, Esc cancels, Ctrl inverts. **Pick** locks the brushes to one object,
**Mirror** X / Y / Z paints both sides, and presets (Fine, Medium, Broad) store brush settings.

.. seealso:: :blender:`Retopology <modeling/meshes/retopology.html>`
