##########################
Compatibility with Blender
##########################

Moritz saves ordinary ``.blend`` files. They open in Blender 5.3, and Blender's files open in
Moritz.

What Blender sees of Moritz's features:

* **Parametric objects** are Geometry Nodes modifiers: Blender shows and renders them.
* **Edit Poly** and Moritz's own modifiers stay in the file, disabled; saving in Blender keeps
  them, and Moritz brings them back.
* **The Command Panel tabs** fall back to the Object tab.
* **Smoothing groups, named selection sets, freeze** are ordinary attributes and properties.

Add-ons and Python scripts written for Blender work in Moritz.
