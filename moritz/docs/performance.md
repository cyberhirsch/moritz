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
| **Move one object, undo push, undo** | **757 ms** |

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

## Next steps

- Profile the undo step with a sampling profiler on a RelWithDebInfo build, and check whether
  the depsgraph can be updated instead of rebuilt when only transforms changed between steps.
- Repeat with 10k unique meshes and with instanced collections (the archviz case), and with
  Maximize enabled (its hover highlight and view tracking run on every redraw).
