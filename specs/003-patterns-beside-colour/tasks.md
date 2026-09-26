# Tasks — charts a reader can follow without telling colours apart

Two stories, run in priority order. Each is independently testable and leaves the suite green.
Documentation ships in the story whose statements it makes.

**The stories are sequential, not parallel.** US2 extends the probe page, `TestDecalPatterns` and the
README section US1 creates, so it is dispatched only after US1 is accepted, on the same branch.

Test-first throughout (Article I): the assertions in each task are written and failing before the
change that satisfies them. Nothing under `mvp_charts/` changes in any task (FR-005).

## US1 — Turn patterns on without losing the chart's name (P1)

Delivers FR-001 … FR-006, SC-001, SC-002, SC-004. Issue #57.

- **T001** — `tests/test_demo.py`, new class `TestPatternsBesideColour`: the Options page lists
  `source_of(orders_by_channel)`; the chart's payload has `aria.enabled` true,
  `aria.label.enabled` false, `aria.decal.show` true and no `aria.decal.decals` key; it has two
  series; its placement carries a `name` and a `description`. Plus: every other chart on the demo
  pages arrives with `aria` equal to `{"enabled": false}` (AS1-5, SC-004). Then `demo/views.py`:
  `orders_by_channel()` — a `Bar` of North/South/East/West with "Online" and "In store" series, built
  with `init_opts=opts.InitOpts(aria_opts={"enabled": True, "label": {"enabled": False}, "decal":
  {"show": True}})` — added to `ChartOptionsView`'s context and `source`; and
  `demo/templates/demo/chart_options.html`: a fourth `<c-section>` "Patterns as well as colour"
  with a short `<c-text>`, the listing, and a `{% show_code %}{% cotton:verbatim %}` placement with
  `id="orders-by-channel"`, a height, `name` and `description`.
- **T002** — `tests/urls.py`: `PatternsProbe` on `probe/patterns/` and
  `tests/templates/probe/patterns.html`, following `RendererProbe`. For US1 it carries the
  two-series patterned bar (`id="patterned-bar"`, with `name` and `description`); T005 adds the
  rest. `tests/test_components/test_chart_e2e.py`, new class `TestDecalPatterns`, reading drawn
  elements (ZRender display list, `getItemGraphicEl`, data visuals — never `getOption()`): every bar
  of each series carries a pattern; the two series' patterns differ; each legend icon carries its
  series' pattern; the surface's `aria-label` equals the tag's `name` and `aria-describedby` still
  names the description element. No production change is expected: if a test passes on first run,
  mutate the probe (drop `decal.show`, add a single `decals` object, drop `label.enabled: false`)
  and confirm the matching assertion goes red, then restore — record that in progress.md.
- **T003** — `README.md`: new `## Patterns as well as colour` section after `## Placing the chart`
  and its subsections, carrying plan items 1, 2, 3 and 8 (what the patterns are and when they are
  worth it; the Python; why not `AriaDecalOpts`; the ECharts link). The paragraph in "Giving the
  chart a box" that mentions readers who "cannot tell its colours apart" links to the new section.
  The Python block is `orders_by_channel`'s source verbatim. `tests/test_demo.py`, extend
  `TestDocumentedExample`: the README's `python` block containing `def orders_by_channel` equals
  `source_of(orders_by_channel)` whitespace-normalised (AS1-3). Anchor on the `def` line, not on
  `aria_opts`: US2 adds a second `python` block in the same section that also contains `aria_opts`.
  Write that test first.
- **T004** — `CONTEXT.md`: **Decal pattern** (FR-006) and **Generated description** (spec Key Entities), in the file's
  existing shape (definition, _Avoid_ line where one helps). `CHANGELOG.md` `[Unreleased]`: one
  entry under the heading the file already uses for documentation, naming the new README section
  and the demo chart.

## US2 — Know where patterns show and where they don't (P2)

Delivers FR-007 … FR-011, SC-003. Issue #58.

- **T005** — Extend the probe page with charts built with the same documented call: a pie of three
  slices (`patterned-pie`), a two-series plain line (`patterned-line`), the same line with
  `areastyle_opts=opts.AreaStyleOpts(opacity=0.5)` on each series (`patterned-area`), a two-series
  scatter (`patterned-scatter`), and a bar with `aria_opts={"enabled": True, "decal": {"show":
  True}}` — generated description left on (`described-by-echarts`), and a two-series bar whose
  `decal` carries the README's colour example, a two-entry `decals` list giving each entry its own
  `symbol` and `color` (`coloured-patterns`), each with a `name`.
- **T006** — `TestDecalPatterns`, one test per README statement, each asserting presence and absence
  separately so it fails when the statement is made false: pie slices carry a pattern; a plain
  line's area element carries a pattern and is drawn at opacity 0; the shaded line's area carries a
  pattern at opacity above 0; no scatter symbol carries a pattern; the `described-by-echarts`
  surface's `aria-label` is not its tag's `name`; the `coloured-patterns` series each draw their
  pattern in the colour their entry names (read from the pattern tile's pixels, as research R1 did)
  and the two tiles differ.
- **T007** — `README.md`, the same section: plan items 4–7 (which marks carry a pattern; the cue on
  a plain line and on scatter points; the default colour and the `decals` list that sets it, with a
  short example that is a fragment (no `def` line) and is exactly the `coloured-patterns` probe's
  `aria_opts`, saying that a list replaces ECharts' built-in patterns so each entry needs its own
  `symbol` as well as its `color`; the generated description replacing the name, and the recommendation). Every
  mark statement it makes is one T006 asserts, and it says nothing T006 does not assert.
- **T008** — Mutation check of T006, as in T002: for each mark test, make the probe contradict the
  statement (shade the plain line, drop the area from the shaded one, turn the patterns off on the
  pie, leave the generated description off on `described-by-echarts`) and confirm the matching test
  goes red; restore. Record each in progress.md.
