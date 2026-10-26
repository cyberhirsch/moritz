# Performance: 10k-object scene

Measured 2026-10-25 with the Release build (`moritz.exe --factory-startup`), 1694×1147 window,
10 000 objects sharing the default cube mesh in one collection, Solid shading. Script: build
the objects, then time operators from a timer with the window open (`wm.redraw_timer` for
drawing). Average of 3–5 runs each.

| Action | Time |
|---|---|
| Create 10k linked objects (Python, data API) | 363 ms |
| Redraw the whole window | 66 ms |
| Outliner redraw (collapsed or expanded) | 22 ms |
| 3D viewport redraw | 23 ms |
| Select all / deselect all | 23 ms |
| Undo push | 19 ms |
| **Move one object, undo push, undo** | **757 ms** (85 ms after the fix below) |

## Findings

1. **Undo is the hotspot.** One undo step after moving a single object takes about 0.75 s.
   Memfile undo reuses unchanged IDs, but the depsgraph and the scene's object bases are
   rebuilt for every step, which grows with the object count. Max users undo constantly, so
   this is the one that will be felt. Look at `memfile_undosys_step_decode` →
   `BKE_memfile_undo_decode` → `DEG_relations_tag_update` / view layer resync.
2. **Whole-window redraw at 66 ms** (about 15 fps when everything redraws, e.g. while
   resizing areas). Each region alone is about 22 ms, so the cost is the sum of regions, not
   one slow editor.
3. Outliner, selection and the viewport are fine at this size.

## Undo fix (done)

Timing undo with `MORITZ_UNDO_TIMING=1` (prints each phase) and `--debug-depsgraph-time`
showed the undo step itself took about 100 ms; the rest was a full rebuild of the depsgraph
relations (0.5 s) plus a full evaluation, requested unconditionally in
`BKE_scene_undo_depsgraphs_restore`.

`memfile_undo.cc` now keeps the relations when the step provably changed none: same set of IDs,
every ID reused or re-read at its old address, and every re-read ID an object with the same
relation fingerprint (parent, data, instancing, force field, modifier types and the IDs they use;
objects with constraints, pose, particles, rigid body, soft body or animation data always
rebuild). Moving objects and undoing, in a 10k-object scene:

| | Before | After |
|---|---|---|
| Undo one move | 800 ms | 85 ms |
| Redo one move | 800 ms | 80 ms |

Steps that change relations (parent, modifiers, adding or deleting objects) still rebuild.
Tested by `moritz/tests/test_undo_relations.py`.

### Scene and collection fingerprints (2026-10-26)

A step that touches the scene datablock (the current frame, any scene setting) re-reads the
scene, and with many objects also the collection holding them; both used to force a full
rebuild. Scenes and collections now have fingerprints too:

- scene: camera, world, the master collection's flags, objects and children, every view layer's
  flag, layer collection tree (collections and their exclude / hide flags) and bases; scenes with
  a set scene, rigid body world, sequencer strips or animation data always rebuild;
- collection: flags, objects and children.

Re-reading a scene can re-allocate its master collection (embedded data), which the depsgraph
keys by address: `DEG_graph_id_replace_orig` re-keys that node (and the physics caches) to the
new pointer, and the master collection is tagged for a copy-on-evaluation update. In all tested
steps the master collection kept its address, so the re-key has not been exercised yet.

Undo / redo of a frame change, 10k objects:

| | Before | After |
|---|---|---|
| Undo or redo a frame change | 800 ms | 290 ms |

Hiding or excluding a collection, or linking an object to the scene collection, changes the
fingerprint and still rebuilds.

## Whole-window redraw (measured, no change)

Timed again per region with `wm.redraw_timer` (10 objects vs 10 000):

| | 10 objects | 10 000 objects |
|---|---|---|
| Whole window, with buffer swap | 6 ms | 40 ms |
| Outliner | 0.9 ms | 21 ms |
| 3D viewport | 1.1 ms | 13 ms |
| Properties, Timeline | 0.5 ms | 1.4 ms |

The Outliner's share is the tree rebuild (`outliner_build_tree` visits every object, also in
collapsed collections, because collapsed rows show their children's icons). `wm.redraw_timer`
forces that rebuild; in normal use the Outliner listener already redraws without rebuilding for
selection, active object, transform and frame changes, so a move or a selection click costs the
viewport plus a cheap Outliner draw. Only structural changes (add, delete, parent, rename)
rebuild. Not worth a core change.

## Next steps

- Repeat with 10k unique meshes and with instanced collections (the archviz case), and with
  Maximize enabled (its hover highlight and view tracking run on every redraw).
