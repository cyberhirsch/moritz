################
Creating Objects
################

The **Create** tab holds every object type by category, as in Max: **Geometry, Shapes, Lights,
Cameras, Helpers, Space Warps, Systems**. The category buttons sit in a column on the left, the
object types in a grid on the right. The same objects are in the 3D Viewport's **Add** menu.

Click a type, then drag in a viewport:

* Box-like objects: drag the base, move for the height, click.
* Round objects: drag the radius, then move for a height or a second radius, click.
* Creation goes on until right-click or Esc, so you can make several in a row.

Objects get Max's names: Box001, Teapot001, TorusKnot001.

Geometry
========

Standard Primitives
   Box, Cone, Sphere, GeoSphere, Cylinder, Tube, Torus, Pyramid, Teapot, Suzanne, Plane, TextPlus.

Extended Primitives
   Hedra, Torus Knot, ChamferBox, ChamferCyl, OilTank, Capsule, Spindle, L-Ext, Gengon, C-Ext,
   RingWave, Hose, Prism.

Shapes
======

Line, Rectangle, Circle, Ellipse, Arc, Donut, NGon, Star, Text, Helix, Egg, Section, Freehand,
and the extended ones: WRectangle, Channel, Angle, Tee, Wide Flange. See
:doc:`splines`.

Parameters
==========

The objects stay parametric: their size, segments and options are in the **Modify** tab until
you collapse them (convert to Editable Poly, or press 1–5).

Primitives come with quads: round caps get a quad grid (**Quad Cap**) and spheres quad poles,
unlike Max's triangle fans. Turn it off per object for Max's caps.

Files
=====

Parametric objects are Geometry Nodes modifiers, so Blender opens and evaluates them unchanged.

.. seealso:: :blender:`Adding objects <scene_layout/object/editing/add.html>`
