# Moritz for 3ds Max users

Where the things you know from 3ds Max are in Moritz. Keys are for the **Moritz** keymap, the
default. Max's own keymap and Blender's are one click away in **Quick Setup** (first start) or
**Preferences > Keymap**. Features marked *Maximize* come from the Maximize add-on, which Moritz
enables on first start.

## Getting around

| Max | Moritz |
|---|---|
| Pan, orbit, zoom | MMB, Alt+MMB, Ctrl+Alt+MMB (or wheel). Preferences > Keymap > Maya Navigation for Alt+LMB/MMB/RMB |
| Top / Front / Left / Perspective / Camera | T / F / L / P / C, or the numpad as in Blender (Num 7 / 1 / 3 / 5 / 0) |
| Zoom Extents Selected / All | Z / Ctrl+Shift+Z |
| Maximize Viewport | Alt+W, on the viewport under the mouse |
| Undo / Redo Viewport | Shift+Z / Shift+Y |
| Quad menu | Right-click in Object Mode and Edit Poly *(Maximize)* |
| Global Search | X (Blender's F3 search) |

## Selecting

| Max | Moritz |
|---|---|
| Click, Ctrl+click adds, Alt+click removes | The same; Ctrl+click on a selected object removes it |
| Window / Crossing | Drag left to right: window (fully inside). Right to left: crossing (touching) |
| Rectangle / Circle / Lasso region | Q, pressed again, cycles the shape |
| Selection preview (hover highlight) | On by default *(Maximize, preference "Hover Highlight")* |
| Select by Name | H |
| Named Selection Sets | Sidebar (N) > Max > Selection, also for sub-objects *(Maximize)* |
| Select Children / Ancestor | Double-click; PgDn / PgUp |
| Freeze Selection / Unfreeze All | Quad menu > Display; frozen objects draw gray and can't be selected (Blender's "Disable Selection") |
| Hide / Unhide | Alt+H, Alt+I (hide unselected), Alt+U |
| Isolate Selection | Alt+Q |

## Transforming and cloning

| Max | Moritz |
|---|---|
| Move / Rotate / Scale | W / E / R; F5 / F6 / F7 lock X / Y / Z while transforming, F8 the plane (Blender's X/Y/Z and typed numbers work too) |
| Transform Type-In | F12 *(Maximize)* |
| Affect Pivot Only, Center to Object, Reset XForm | Insert; sidebar > Max > Pivot *(Maximize)* |
| Align | Alt+A, then pick the target *(Maximize)* |
| Clone (Copy / Instance / Reference) | Ctrl+V, or Shift+drag (also on the gizmo) *(Maximize)*. Instances and references share the mesh and the original's whole modifier stack |
| Make Unique | Quad menu / F3 "Make Unique" |
| Array, Spacing Tool | Quad menu > Tools *(Maximize)* |
| Snaps, Angle Snap | S, A |

## Modeling

| Max | Moritz |
|---|---|
| Standard Primitives with parameters | Add > Standard Primitives; drag to create; parameters in the sidebar > Max > Modify *(Maximize)* |
| Convert to Editable Poly | Press 1–5, or quad menu |
| Sub-object levels 1–5, 6 back | The same; the header shows Vertex, Edge, Border, Polygon, Element |
| Edit Poly modifier | Quad menu > Tools > Edit Poly Modifier: edit with 1–5 while the modifiers below stay live; Collapse To / Collapse All in the sidebar *(Maximize, prototype)* |
| Show End Result | Alt+` |
| Extrude, Chamfer, Bevel, Connect, Cut, Swift Loop, Weld, Target Weld, Collapse, Bridge, Cap, Detach | Max names in the quad menu and F3 search, Max keys (Shift+E, Ctrl+Shift+C, Ctrl+Shift+B, Ctrl+Shift+E, Alt+C, Alt+1...) |
| Smoothing groups | Sidebar > Max > Polygon: Smoothing Groups (32 buttons, Auto Smooth, Select By SG) at polygon level |
| Soft Selection | Shift+B (Blender's Proportional Editing) |
| TurboSmooth, Shell, Symmetry | Blender's Subdivision Surface, Solidify, Mirror (Max names in F3 search) |
| Bend / Twist / Taper / Stretch | Blender's Simple Deform; a viewport gizmo drags its angle or factor *(Maximize)* |
| FFD | Blender's Lattice modifier |
| UVW Map | Quad menu > UVW Map *(Maximize)*; Unwrap UVW is Blender's UV Editor |

## Shapes and splines

| Max | Moritz |
|---|---|
| Line | Add > Shapes > Line: click for corners, drag for curves, click the first point to close *(Maximize)* |
| Rectangle, Circle, Ellipse, Arc, NGon, Star, Helix, Donut | Add > Shapes; drag to create, parameters stay editable, "Thickness" renders them *(Maximize)* |
| Convert to Editable Spline | Press 1 on a shape |
| Fillet, Chamfer, Outline, Break, Trim, Extend | Curve Edit Mode > Max Spline Tools *(Maximize)* |
| Connect | Max Spline Tools > Connect (Blender's Make Segment, F) |
| Refine | The Pen tool |
| Boolean (Union, Subtraction, Intersection) | Object > Max Spline Tools, with the two shapes selected *(Maximize)* |
| Loft | Object > Max Spline Tools > Loft: active = path, selected = shape *(Maximize)* |
| Extrude, Lathe, Renderable Spline | Blender's curve Extrude/Bevel, Screw modifier, curve Bevel Depth |

## Scene, units and files

| Max | Moritz |
|---|---|
| Scene Explorer | Outliner (F2 renames) |
| Units Setup, feet and fractional inches | Scene Properties > Units > Imperial > Fractional Inches (3' 4 1/2") |
| Material Editor | M |
| Render Setup / Render | F10 / Shift+Q or F9 |
| Track View, Dope Sheet | Graph Editor, Dope Sheet (K sets a key, Ctrl+Alt+Z frames) |
| Auto Key / Set Key | N / K |
| FBX to / from Max | File > Export / Import > FBX, operator presets "To 3ds Max" / "From 3ds Max" |

## Following Blender tutorials

Menus and tooltips show Blender's own shortcut next to Moritz's when they differ, and the numpad,
F3 search and the menus work as in Blender. To follow a tutorial key for key, switch the keymap to
Blender in the Max sidebar tab or Preferences > Keymap.
