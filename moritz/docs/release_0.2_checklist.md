# Moritz 0.2: hand tests and release

Everything automated is done: 58 test scripts pass on the merged build (2026-10-30), and both
packages are built and smoke-tested. What is left needs Seb's hands and decisions. Each test below
takes a few minutes; tick it in `TASK.md` when it passes, or note what went wrong.

**Release candidate** (built 2026-10-30 from `5db869f5794`, not published):
- `G:\Code\Moritz\dist\rc-0.2\moritz-5.3-windows-x64.zip`: portable, with Maximize bundled
  (off until you enable it)
- `G:\Code\Moritz\dist\rc-0.2\moritz-5.3-windows-x64.msi`: per-user installer

## 1. Docking with a real mouse and two monitors (TASK.md, Phase 1)

Simulated events already pass. What simulation can't cover is real mouse timing and a second monitor.
1. Drag an editor's empty header space onto another area's center: it stacks as a tab.
2. Drag it to an edge: it splits. Drag it outside the window: a new window opens.
3. Drag that new window to the second monitor, then drag a tab back into the main window.
4. Drag a tab button itself, close a tab with its ×, and use Duplicate as Tab in the header's
   context menu.
5. At a different DPI scale on the second monitor (if it has one): do the tab strip and the
   corner grip still line up?

## 2. The whole add-on with a real mouse (TASK.md, Phase 1)

Enable Maximize (Preferences > Add-ons), Keymap: Max, Names: Max.
1. Navigation: MMB pan, Alt+MMB orbit, Ctrl+Alt+MMB zoom, Alt+W maximize, Z zoom extents.
2. Right-click quad menu in Object Mode and in Edit Mode: the text faces the cursor, the titles
   form a band through the middle, the current level is framed, and Convert To opens a submenu.
3. Create tab: Box, then Modify tab: change the Length. Press 1–5 for the levels.
4. Add Modifier > Search: type "bend", "cap", "retopo", "vertexpaint".
5. Utilities tab: Align, Array, Spacing Tool, Object Paint.
6. VertexPaint modifier: Paint, a few strokes, Done; then Cancel and Clear Colors.
7. Paint Deform, Freeform and Sculpt: one stroke each. Do the new icons read clearly?

## 3. The Edit Poly workflow (TASK.md, Phase 2)

1. A box with a Bend modifier, then Edit Poly on top of it; move a few vertices.
2. Change the Bend angle: the edits follow.
3. Extrude a polygon in Edit Poly, then change a modifier below that changes the topology: you
   get the warning, and Re-base keeps the edit.
4. Mid-stack Sculpt: one stroke, leave, change the Bend: the sculpt follows.
5. Save, then open the file in stock Blender 5.3: the stack is kept, Edit Poly is disabled, and
   saving there and reopening in Moritz brings it back.

## 4. The release (Seb decides when)

1. **Version:** the splash still says `0.1 Alpha` (`BKE_moritz_version.h`,
   `MORITZ_VERSION_STRING`). Set `0.2` (or `0.2 Beta`); this needs a rebuild, and the package
   names should then say 0.2 instead of 5.3.
2. Rebuild, run the test suite, and rebuild both packages with `moritz/tools/make_portable_zip.py`
   and `moritz/tools/make_msi.py`.
3. Release notes: the native modifiers (Edit Poly, Edit Spline, Cap Holes, Normal, Mesh Clean,
   Quadify Mesh, ProOptimizer, VertexPaint, Retopology), the Command Panel with Create, Modify
   and Utilities, tabbed docking, name schemes and the Max icons. Note the file rule as well:
   files from stock Blender open unchanged; native Moritz modifiers survive in stock Blender only
   as disabled "None" modifiers, and stock Blender evaluates the stack without them.
4. Tag `moritz-0.2` and publish the release. The repos are private: decide whether the release
   is private too, or for testers only (GPL: anyone who gets the binary gets the source; the
   readme in each package links to it).
