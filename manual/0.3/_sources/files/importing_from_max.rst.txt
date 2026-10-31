##################
Importing from Max
##################

Without 3ds Max
===============

**File > Import > Autodesk MAX (.max)** reads .max files directly: meshes, UVs, materials and
their textures (also Physical materials). It is the bundled extension *Import Autodesk MAX* by
Sebastian Sille and others (GPL).

With 3ds Max
============

For more of the scene, export it from Max:

1. In 3ds Max: **Scripting > Run Script**, choose ``moritz_export.ms`` (it ships with Moritz). It
   saves a ``.mxscene`` file.
2. In Moritz: **File > Import > Max Scene (.mxscene)**.

V-Ray, Corona, Physical and Standard materials become Principled materials. What could not be
converted is listed in the material's ``max_unconverted`` property.

FBX
===

**File > Export / Import > FBX** has the presets "To 3ds Max" and "From 3ds Max".
