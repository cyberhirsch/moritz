#########
Modifiers
#########

**Add Modifier** in the Modify tab lists every modifier that fits the object. Search by Max's or
Blender's name: *bend* finds Bend, which is Blender's Simple Deform.

Where Blender already has the modifier, Moritz uses it under Max's name:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Max
     - In Moritz
   * - Bend, Twist, Taper, Stretch
     - Simple Deform, with a viewport gizmo for angle and factor
   * - TurboSmooth, Subdivide
     - Subdivision Surface
   * - Shell
     - Solidify
   * - Symmetry
     - Mirror (bisect)
   * - FFD 2x2x2 / 3x3x3 / 4x4x4 / (box)
     - Lattice, with a hidden lattice object
   * - Lathe
     - Screw
   * - Conform
     - Shrinkwrap
   * - Spherify
     - Cast
   * - Push
     - Displace along the normal
   * - Relax
     - Smooth Laplacian
   * - Skin Wrap
     - Surface Deform
   * - Path Deform
     - Curve
   * - ProOptimizer
     - Decimate
   * - Vertex Weld
     - Weld
   * - Wave, Ripple
     - Wave

Moritz adds its own where Blender has none: **Edit Poly**, **UVW Map**, **Freeform**, **Sculpt**,
**Quadify Mesh**, **Retopology**, **Mesh Cleaner**, **STL Check**, **VertexPaint** and more.

Name clashes
============

With the Max name scheme, four names mean Max's modifier: **Skin** (Blender's Armature),
**Smooth** (Smooth by Angle), **Lattice** (Wireframe with joints) and **Bevel** (the spline
modifier). Blender's modifiers of the same name keep their Blender names.

UVW Map
=======

Planar, Box, Cylindrical and Spherical mapping through a gizmo, with U / V tiling, real-world
size and the UV channel.

Files
=====

Modifiers Blender has are plain Blender modifiers. Moritz's own modifiers are kept by Blender
(disabled) and come back in Moritz.

.. seealso:: :blender:`Modifiers <modeling/modifiers/index.html>`
