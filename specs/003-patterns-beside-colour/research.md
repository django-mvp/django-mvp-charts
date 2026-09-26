# Research — 003 Charts a reader can follow without telling colours apart

## R1 — What pyecharts emits for `aria`, and what ECharts draws from it

Measured 2026-09-26: pyecharts 2.1.0, ECharts 6.1.0 from the demo's CDN, chromium via Playwright.
Each chart built in Python, its `dump_options()` passed to `setOption`, then read back from the
instance's data visuals (`getData().getVisual('style').decal`, `getItemVisual(0, 'style')`) and
from ZRender's display list (elements whose fill is a pattern).

**pyecharts' default.** A chart built with no aria option dumps `"aria": {"enabled": false}`. The
key is always present, which is why SC-004 is checkable on the rendered payload.

**Where the option goes.** `aria_opts` is an `InitOpts` argument, not a `set_global_opts` one:
`set_global_opts(aria_opts=...)` raises `TypeError`. `Base.__init__` copies `ariaOpts` into
`options["aria"]` as given, so a plain dictionary passes through untouched.

**`AriaDecalOpts` gives every series the same pattern.** `AriaDecalOpts(is_show=True)` writes
`"decal": {"show": true, "decals": {<one object>}}`. ECharts applies a single `decals` object to
every series: on a two-series bar both series' decal visuals were identical (10×10 tile, rotation
0). With `"decal": {"show": true}` and no `decals`, the two series drew different patterns (1×7
tile at 30° rotation, and a 16×12 tile), from ECharts' built-in set.

**Which marks carry a pattern** (pattern-filled elements in the display list, two series unless
noted):

| Chart | Pattern-filled elements | Reading |
|---|---|---|
| Bar, 4 categories | 10 | 8 bars + 2 legend icons |
| Pie, 3 slices | 6 | 3 slices + 3 legend icons |
| Line, plain | 4 | 2 area polygons at `areaStyle.opacity` 0 + 2 legend icons |
| Line, `areastyle_opts(opacity=0.5)` | 4 | the same elements, now visible |
| Scatter | 2 | legend icons only; no symbol is patterned |

**The generated description.** With `aria.enabled` true and `label.enabled` false, the surface's
`aria-label` stayed as written. ECharts' own default for `label.enabled` under `aria.enabled` is
true, so leaving `label` out turns the generated description on.

**Default colour.** pyecharts' `AriaDecalOpts` default and ECharts' built-in patterns are both
`rgba(0, 0, 0, 0.2)`: dark and translucent.
