# Max's mesh modifiers in Moritz: design notes

Seb, 2026-10-29: "ProOptimizer and Retopology: Max's algorithm is better, try to match it.
Quadify Mesh and Unwrap UVW: not later, plan them now (both native, rebuild)."

The native batch (`source/blender/modifiers/intern/MOD_max_mesh.cc`) has Cap Holes, Normal,
Mesh Clean, Quadify Mesh, ProOptimizer and VertexPaint. They are stored like Edit Poly: a plain
`ModifierData` with its settings in `system_properties` and an `mx_type`. Stock Blender keeps them
as a disabled "None" modifier and saves them back; Moritz revives them on load. **In stock Blender
the stack evaluates without them** (the mesh comes out uncapped, unoptimized, uncolored).

What below is fact about Max comes from its documentation; the rest is a plan. Points marked
*(check)* were not verified in a running Max.

## ProOptimizer

**Max:** a vertex-collapse optimizer. You set the result as Vertex % or Vertex Count, after a
**Calculate** step; after that, changing the percentage is instant. Options: Crunch / Protect /
Exclude Borders, Keep Material Boundaries, Keep UVs (with a tolerance), Keep Vertex Colors, Keep
Normals (with a threshold), Merge Vertices / Faces, Favor Compact Faces, Prevent Flips, Lock
Vertex Position, Symmetry X / Y / Z with a tolerance. The result is triangles.

**Phase 1 (done, native batch):** Blender's quadric collapse (`BM_mesh_decimate_collapse`) with
weight 0 on the vertices to protect: borders, material boundaries, UV seams, hard edges (Keep
Normals), plus a symmetry axis. This keeps boundaries exactly, but they cannot thin out at all.

**Phase 2 (the Max match):**
1. *Attribute-aware quadrics* (Garland and Heckbert 1998): the error of a collapse includes the UV
   and normal change, so UV and material boundaries stay where they are but still lose vertices
   along their length. This is Max's "Keep UVs" behaviour, rather than a frozen boundary.
2. *Favor Compact Faces:* add a triangle-quality term (the ratio of area to the squared edge
   lengths) to the cost.
3. *Prevent Flips:* reject a collapse that turns any adjacent face normal by more than 90°.
   Blender's collapse already checks for this; the option makes it visible.
4. *Calculate once:* record the full collapse sequence once (Hoppe's progressive mesh). The
   modifier keeps it in its runtime data, keyed by a hash of the input. The Vertex % slider then
   replays a prefix of the sequence, with no new optimization. This is what makes Max's slider
   instant.
5. *Vertex Count* as an alternative to the percentage; Keep Vertex Colors as another attribute in
   step 1.

Cost: one file, about 600 lines. It needs no BMesh changes: step 1 works on its own half-edge
arrays.

## Retopology

**Max (2021.2+):** the Retopology modifier, with the **ReForm** algorithm and later
**QuadriFlow** *(check which version added which)*. Options: Face Count; feature edges from an
angle (Auto Edge), smoothing groups, material IDs and UV seams; guide edges from an Edit Poly
selection; Symmetry X / Y / Z; pre-processing (Mesh Cleaner, a cleanup of non-manifold geometry);
post-processing (Conform to the original, then Relax). It runs in the background, and a status
line shows the progress.

**Plan:** a native `RETOPOLOGY` modifier.
1. **Pre-processing:** Mesh Clean (the native batch's), then a voxel cleanup on non-manifold
   input. QuadriFlow needs manifold input, and this is where Blender's Remesh > QuadriFlow most
   often fails. Max's cleaner is the reason Max seems better here.
2. **Feature edges:** sharp edges by angle, plus material, UV seam and hard-edge boundaries. They
   go to QuadriFlow's `preserve_sharp`, with the edges marked on the input.
3. **Symmetry:** bisect the input, retopologize one half, mirror it and weld the seam. This also
   halves the time.
4. **Face Count target** (Max's control), mapped to QuadriFlow's target face count.
5. **Post-processing:** a shrinkwrap projection onto the original (Conform), then a few Laplacian
   relax passes that keep the projection.
6. **Runs in a job** (`wm_jobs`), like Blender's Remesh operator, with the result cached in the
   modifier's runtime data. The stack shows "Calculating…" until the result is ready. Changing a
   setting restarts the job. Saving stores the result in a hidden mesh, like Edit Poly's Topology
   mode, so reopening the file does not run it again.

**Unknown:** ReForm is Autodesk's own algorithm and is not published. Matching it means matching
its results (edge flow along curvature, quad density following detail), not its code. The
practical comparison: run the same five test meshes through Max and Moritz, then compare the quad
ratio, the valence-4 ratio and the distance to the original.

## Quadify Mesh (done in the native batch)

**Max:** converts the mesh to quads, with Quad Size as a percentage of the object's size.

**Moritz:** QuadriFlow, with a target face count computed from the surface area divided by
(bounding-box diagonal × Quad Size %)², and attributes reprojected onto the result. It inherits
the manifold requirement. Pre-processing step 1 of Retopology will also go here, since both use
QuadriFlow.

## Unwrap UVW

This changes the 2026-10-25 rule ("Blender's UV editor stays, no Unwrap UVW modifier"). Blender's
**UV editor stays the editing tool**. What is new is that the **result lives in the stack**, as
in Max.

**Max:** a stack modifier that holds the UVs of one map channel for the mesh below it. Edit UVWs
is the editing window, with Peel, Pelt, Flatten Mapping, Quick Planar, Stitch, Relax, Pack and
seam editing. The UVs follow the stack below until its topology changes.

**Plan:** a native `UNWRAP_UVW` modifier, built like VertexPaint.
1. **Storage:** one float2 per face corner of the modifier's input, plus a target UV map name
   (Max's map channel). Corners are matched by the `mx_orig` mapping, as in Edit Poly, so the UVs
   survive a vertex count change below as long as the faces stay the same. Otherwise the modifier
   shows a warning: "The mesh below changed: unwrap again".
2. **Editing session:** like Edit Poly's stand-in. Edit Mode on the stack's result up to the
   modifier, with the UV Editor opened beside the 3D view. Leaving stores the UVs. Max's tools map
   to Blender's:
   - Peel = Unwrap (Angle Based / Minimum Stretch);
   - Pelt = Unwrap with seams;
   - Flatten Mapping = Smart UV Project;
   - Quick Planar = Project from View;
   - Stitch = Stitch;
   - Relax = Minimize Stretch;
   - Pack = Pack Islands;
   - Edit Seams = Mark Seam.

   Maximize labels them with Max's names in the Max scheme.
3. **Evaluation:** write the stored UVs into the target map (creating it if needed) and make it
   active for rendering.
4. **Several Unwrap UVW modifiers** in one stack each write their own channel, or override the
   same one, as in Max.

Stock Blender: the modifier is kept but not evaluated, so the mesh renders with its own UVs only.
To hand a file to stock Blender, apply the modifier first (Apply works: the UVs then become mesh
data).

## Order of work

1. Build and test the native batch (now).
2. ProOptimizer phase 2: no new DNA, so no file risk.
3. Retopology: a new native type, `mx_type` "RETOPOLOGY", the next value after VertexPaint.
4. Unwrap UVW: a new native type, `mx_type` "UNWRAP_UVW", plus the Maximize session.
