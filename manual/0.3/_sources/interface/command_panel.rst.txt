#############
Command Panel
#############

Moritz's Properties editor is the Command Panel. Its first three tabs, in teal, are Max's:

Create
   New objects, by category (see :doc:`/modeling/create`).

Modify
   The modifier stack of the selected object, and the selected modifier's settings.

Utilities
   Align, Array, Spacing Tool and Object Paint (see :doc:`/scene/transform_tools`).

Blender's tabs follow in their usual order (Tool, Render, Output, View Layer, Scene, World,
Collection, Object, Particles, Physics, Constraints, Data, Material).

Modify tab
==========

The stack
   The modifiers top first, the base object at the bottom, as in Max. Click a row to show only
   that modifier's settings below. Move Up / Down (or Ctrl+Up / Down) reorders.

Right-click a row
   Copy, Paste, Paste Instanced, Make Unique, Collapse To, Collapse All, Off in Renderer.
   Instanced modifiers show a link icon.

Under the stack
   Show End Result (Alt+`), Make Unique, Remove Modifier.

Add Modifier
   One list of every modifier that fits the object (also Ctrl+A). Type to filter; Max and Blender
   names both find it (see :doc:`/modeling/modifiers`).

For an editable mesh the Modify tab shows the Edit Poly rollouts (see :doc:`/modeling/edit_poly`).

Files
=====

The open tab is stored in the file. Blender does not know Create, Modify and Utilities and shows
its Object tab instead; nothing else changes.

.. seealso:: :blender:`Properties editor <editors/properties_editor.html>`
