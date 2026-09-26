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
