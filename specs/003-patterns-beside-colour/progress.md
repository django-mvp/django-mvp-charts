# Progress — 003 Charts a reader can follow without telling colours apart

## 2026-09-26 · Forge · S3 PLAN

Did: branched `003-patterns-beside-colour` from origin/main 2f24b4a (the spec merge). Measured what
pyecharts 2.1.0 emits for `aria` and what ECharts 6.1.0 draws from it (research R1). Wrote plan.md,
research.md, tasks.md; appended D1–D3 to decisions.md.
Next: design review, then US1.
Watch: the README's Python block must stay byte-for-byte the demo builder's source.

## 2026-09-26T08:40 · Implementer US1 · T001

Did: `TestPatternsBesideColour` in tests/test_demo.py (written first; failed on the missing
`orders_by_channel` import), then `orders_by_channel()` in demo/views.py, added to
`ChartOptionsView`, and a fourth section on the Options page.
Verified: `uv run pytest tests/test_demo.py -q` → 34 passed; `uv run pre-commit run --all-files` → all passed.
Next: T002 probe page and browser tests.
Watch: the description text names which channel leads in which region; change it with the data.

## 2026-09-26T08:55 · Implementer US1 · T002

Did: `PatternsProbe` on `probe/patterns/` (tests/urls.py, tests/templates/probe/patterns.html) with the
patterned two-series bar `patterned-bar`; `TestDecalPatterns` in tests/test_components/test_chart_e2e.py.
Reads drawn elements only: each bar's overlay element (`_decalEl`, ECharts draws the pattern as a separate
element over the solid bar) and ZRender's display list for legend icons.
Verified: `uv run pytest tests/test_components/test_chart_e2e.py::TestDecalPatterns -q` → 4 passed.
The first run was red only because my read looked at the bar's own fill; the bar keeps a solid fill.
No production change was needed, so mutation checks against the probe (each restored afterwards):
- `"decal": {}` (drop `show`) → 3 failed: every-bar-carries-a-pattern, different-patterns, legend-icon.
- `"decal": {"show": True, "decals": {"symbol": "rect"}}` (single object) → 2 failed: different-patterns, legend-icon.
- drop `"label": {"enabled": False}` → 1 failed: keeps-the-tags-name-and-description.
Next: T003 README.
Watch: the bar overlay is `_decalEl`, an ECharts internal; a release that renames it fails these tests loudly.

## 2026-09-26T09:05 · Implementer US1 · T003

Did: `TestTheReadmeShowsThePatternedChart` in tests/test_demo.py (written first; 3 red: no block, no section,
no link), then README `## Patterns as well as colour` between "While the chart is still on its way" and
"Keeping its shape", carrying `orders_by_channel`'s source verbatim, and a link from the accessibility
paragraph in "Giving the chart a box". The block test anchors on `def orders_by_channel`.
Verified: `uv run pytest tests/test_demo.py -q` → 37 passed; pre-commit all passed.
Next: T004 CONTEXT.md and CHANGELOG.md.
Watch: US2 adds its statements to the same section; the section ends with the ECharts link, so US2's items go before it.

## 2026-09-26T09:12 · Implementer US1 · T004

Did: CONTEXT.md gains **Decal pattern** and **Generated description** in the file's entry shape;
CHANGELOG.md `[Unreleased]` gains one entry under `### Added` (the file has no documentation heading).
Verified: pre-commit all passed. Nothing under docs/ describes what this story touched (docs/ holds the
roadmap, ADRs and a brainstorm), so no page needed updating.
Next: full verify, report.

## 2026-09-26T10:10 · Implementer US2 · T005

Did: probe page gains `patterned-pie`, `patterned-line`, `patterned-area`, `patterned-scatter`, `described-by-echarts` and `coloured-patterns`, built in `PatternsProbe` (tests/urls.py) with the documented call; `COLOURED_PATTERNS` is the README's colour example.
Verified: `uv run pytest tests/test_components/test_chart_e2e.py::TestDecalPatterns -q` → 4 passed (US1 unchanged); pre-commit all passed.
Watch: `add_yaxis(areastyle_opts=None)` removes pyecharts' zero-opacity area, so the plain line only passes `areastyle_opts` when it is shaded.

## 2026-09-26T10:30 · Implementer US2 · T006

Did: `READ_MARKS`, `READ_TILE_COLOUR`, `READ_TILE_SHAPE` and eleven tests added to `TestDecalPatterns`. Pie slices and the line's area polygon (`view._polygon`) carry the pattern as an overlay (`_decalEl`); scatter symbols are read through their group's children; legend icons through the display list.
Verified: `uv run pytest tests/test_components/test_chart_e2e.py::TestDecalPatterns -q` → 15 passed.
Watch: pattern colour is read from the most opaque pixel of the tile (a circle's edge blends with transparency). The "tiles differ" test first compared data URLs, which differ by colour alone, and stayed green when entries lost their `symbol`; it now compares the shape of each tile (alpha above half), found in T008.

## 2026-09-26T10:45 · Implementer US2 · T007

Did: README section gains "Which marks carry a pattern", "Setting the pattern colour" (fragment identical to the probe's `aria_opts`) and "ECharts' generated description", before the ECharts link. `test_the_colour_example_is_the_call_the_browser_tests_measure` in tests/test_demo.py parses the fragment and compares it with the probe's.
Verified: `uv run pytest tests/test_demo.py -q` → 38 passed. Nothing under docs/ describes what this story touched.

## 2026-09-26T11:00 · Implementer US2 · T008

Mutations of tests/urls.py, each restored afterwards (`TestDecalPatterns` run each time):
- shade the plain line → red: plain-line-drawn-at-zero-opacity.
- unshade the shaded line → red: shaded-line-is-visible (the pattern test stays green: an unshaded area still carries one).
- no aria_opts on the pie → red: every-pie-slice-carries-a-pattern, slice-not-drawn-with-neighbours-pattern.
- no aria_opts on the scatter → red: scatter-legend-icons-do-carry-a-pattern.
- turn label off on described-by-echarts → red: surface-labelled-by-echarts-and-not-the-tag.
- colour-only `decals` entries → red: tiles-of-different-shape (the first version of this test stayed green; fixed in T006).
- an `itemStyle.decal` on scatter series: still green. ECharts computes a decal visual for the points but never draws it on the symbol, so a patterned scatter symbol cannot be produced from pyecharts; the legend test is the demonstration that the read works on this chart type.
