# Reddit survey: 3ds Max users' complaints about Blender

## Could Reddit be reached through the built-in browser?

### Takeaway
No. The built-in browser pane refuses reddit.com, so no threads were read. Per the assignment, research stopped here. Sample: 0 threads.

### Cited Findings
- On 2026-10-22, `mcp__Claude_Browser__navigate` to https://old.reddit.com/r/blender/search?q=3ds+max+switch&restrict_sr=on&sort=relevance&t=all returned "https://old.reddit.com is not allowed due to safety restrictions".
- `mcp__Claude_Browser__navigate` to https://www.reddit.com/r/blender/search/?q=3ds+max+switch returned "https://reddit.com is not allowed due to safety restrictions and cannot be opened in the Browser pane".
- Earlier research found that WebSearch and WebFetch also refuse reddit.com (per the coordinator's brief).

### Inferences
- The block covers the whole domain (old. and www.), not one URL, so trying other subreddits or search strings would not help.

### Gaps
- No thread URLs, dates, vote or comment counts, complaints, or category tallies could be collected for r/blender, r/3dsmax, r/archviz, r/gamedev or r/vfx.
- Ways to fill the gap (each needs the user's say-so): (a) the Claude in Chrome extension (mcp__claude-in-chrome__*), which runs in the user's own Chrome and may not have this domain restriction; (b) the user pastes thread URLs or exports the page text; (c) use non-Reddit forums instead (Blender Artists, CGSociety/Polycount, Autodesk forums, BlenderNation comments).
