#############
Smart Extrude
#############

Smart Extrude extrudes polygons and works out what that means for the mesh:

* **Out into free space:** a plain extrusion.
* **Into the mesh:** a cut, like a boolean subtraction: a pocket, a notch or, all the way through,
  a hole.
* **Out into other geometry:** the two are joined.

The result is one undo step, and only the cap stays selected, as in Max.

Using it
========

* **Smart Extrude** in Edit Polygons: drag along the normal (Ctrl for steps), or type a distance in
  the redo panel.
* **Shift+drag** selected polygons with the Move tool. Drag freely, or on the gizmo: an **arrow**
  extrudes along that axis in the current Transform Orientation, a **plane** handle in that
  plane, the center ring freely. Snapping works as in a move.

Transform Orientation
=====================

The gizmo follows the Transform Orientation menu in the viewport header: **Normal** aligns it to the
selected polygons, **Local** to the object, **Global** to the world.
