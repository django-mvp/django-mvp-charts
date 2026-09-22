# Progress — 002, a line chart drawn from values written in the template

A running log of what happened on this branch, newest entry last.

## 2026-09-22 — planning

Branch cut from `3efca44` on main, which already carries the specification (merged as #23) and the
constitution amendment that removed Article XV's colour claim (merged as #24). Baseline verified
green on that commit: lint, typecheck, 119 tests, build, conformance.

Plan, research and task list written. Thirteen tasks across the specification's three stories.
Three planning decisions recorded in `decisions.md`, none of which graduates to an architecture
decision record.

The sketch branch `sketch/chart-component-api` is prior art this plan draws on: its settled parts
(data as a Python value, empty defaults in `<c-vars>`, raw options merged last, `json_script` as
the carrier) are carried over, and the appearance defaults it wrote into every chart are not,
because the specification answers issue #17 by giving the package no appearance decisions at all.

## 2026-09-22T18:21:00Z · Implementer US1 · T001a

Did: wrote `tests/test_echarts/test_options.py`, mirroring the module T002 creates — `TestAttribute`
(empty reads as not given, `0`/`0.0` are values somebody wrote, a string is returned unparsed) and
`TestLine` (values with labels, without labels, and none at all, each compared whole).
Verified: `poetry run pytest tests/test_echarts/test_options.py -x` — collection failed with
`ModuleNotFoundError: No module named 'mvp_charts.echarts'`, the expected RED (module built in T002).
Next: T001 — the component's rendered-output contract.
Watch: nothing.

## 2026-09-22T18:23:00Z · Implementer US1 · T001

Did: wrote `tests/test_components/test_line.py`, compiling Cotton source directly as
`test_region.py` does — the options payload for values with labels, without labels, a value list
carrying `None`/a float/`0`, that every `<script>` in the output is the JSON payload (FR-001), and
that a missing id renders the region's own message with no options script (FR-006).
Verified: `poetry run pytest tests/test_components/test_line.py -v` — 6 failed with
`TemplateDoesNotExist: cotton/echarts/line.html`, the expected RED. This file will not turn green
until T004 wires the template together with T002's options builder and T003's tag; that is the
order `tasks.md` gives these tasks in and it is not re-sliced.
Next: T002 — implement the options builder T001a already covers.
Watch: this test file stays red through T002 and T003a/T003; expected until T004.

## 2026-09-22T18:24:00Z · Implementer US1 · T002

Did: `mvp_charts/echarts/options.py` — `Attribute` (one attribute's Python value; `""` reads as not
given, everything else including `0`, `0.0` and a string is returned untouched, per FR-002a) and
`Line` (the options object: `xAxis`/`yAxis`/`series` only, `xAxis.data` present only when labels are
given, values never reordered/dropped/combined/rounded/filled per FR-004).
Verified: `poetry run pytest tests/test_echarts/test_options.py -v` — 9 passed. `ruff check` and
`ruff format --check` on `mvp_charts/echarts/` and `tests/test_echarts/` — clean.
Next: T003a — tests for the template tag.
Watch: `tests/test_components/test_line.py` (T001) still red, as expected until T004.

## 2026-09-22T18:29:00Z · Implementer US1 · T003a

Did: wrote `tests/test_templatetags/test_mvp_charts.py`, mirroring the module T003 creates —
`TestEChartsChart` asserts the tag returns the id it was given, an options-script id derived from
it, a payload whose JSON parses back to what `Line` built, and that a call with no id returns no
payload.
Verified: `poetry run pytest tests/test_templatetags/test_mvp_charts.py -v` — collection failed with
`ModuleNotFoundError: No module named 'mvp_charts.templatetags'`, the expected RED.
Next: T003 — implement the tag.
Watch: `tests/test_components/test_line.py` (T001) still red, as expected until T004.

## 2026-09-22T18:31:00Z · Implementer US1 · T003

Did: `mvp_charts/templatetags/mvp_charts.py` — `{% echarts_chart %}`, registered on the package's
own library. Builds `Line(values, labels).options()`, wraps it in `EChartsChart` carrying the id,
an options-script id (`<id>-options`) and a `mark_safe`d JSON payload escaped the same way
`django.utils.html.json_script` escapes its own output (the three sequences that could end a
`<script>` early or smuggle a line/paragraph separator) — reproduced rather than called directly
because the payload needs its own tag carrying `data-mvp-echarts-options-for`, which `json_script`
has no way to add (D1). Returns `None` when no id was given.
Verified: `poetry run pytest tests/test_templatetags/test_mvp_charts.py -v` — 4 passed. `ruff check`,
`ruff format --check` and `mypy mvp_charts/templatetags/` — clean (one `S308` on the `mark_safe`
call, annotated and suppressed: the string it wraps is escaped for a script context immediately
above it, same as `json_script`'s own use).
Next: T004 — the component template.
Watch: `tests/test_components/test_line.py` (T001) still red, as expected until T004.

## 2026-09-22T18:34:00Z · Implementer US1 · T004

Did: `mvp_charts/templates/cotton/echarts/line.html` — declares `id`, `values`, `labels`, `name`,
`description` with empty defaults in `<c-vars>`, calls `{% echarts_chart %}`, renders
`<c-echarts.region>` with the id/name/description, and — only when the tag returned a chart — the
options script beside it carrying `data-mvp-echarts-options-for="{{ id }}"`. A missing id falls
through to the region's own missing-id message and the `{% if chart %}` guard drops the script
entirely (FR-006). Annotated to the gallery standard region.html uses, one `{# ... #}` per line.
`djlint --reformat` moved the payload onto its own line inside the script tag; `JSON.parse` and
`json.loads` both ignore the resulting leading/trailing whitespace.
Verified: `poetry run pytest tests/test_components/test_line.py tests/test_components/test_shipped_templates.py tests/test_components/test_region.py tests/test_app.py -q`
— 37 passed. This is where T001 (component-level) turns green. `ruff check`/`ruff format --check`
n/a (template file); `djlint --check` clean.
Next: T005 — the browser module.
Watch: nothing.

## 2026-09-22T18:38:00Z · Implementer US1 · T005

Did: `mvp_charts/static/mvp_charts/js/echarts-chart.js` — finds every
`[data-mvp-echarts-options-for]`, waits for its region's `mvp-chart-region:state` to reach `ready`
(with a fallback read of the region's current state for the case where it was already ready before
this script attached its listener), `echarts.init`s the drawing surface, `setOption`s the parsed
payload, and calls `chart.resize()` on `mvp-chart-region:resize`. No library poll, no height check
and no resize observer of its own (D2) — the region owns all three. Guarded against double
evaluation by a dataset flag per script and a `window.mvpEchartsChart` module guard; each chart
initialised inside its own try/catch so one failing leaves the others working, matching
chart-region.js.
Verified: no JS test runner in this repo — browser behaviour is exercised in T007. `node --check`
confirms the file parses. No lint config exists for standalone `.js` files (checked: no
eslint/prettier/package.json in the repo), matching chart-region.js's own lint-free status.
Next: T006 — the demo project.
Watch: this module is functionally unexercised until T006 wires a page that loads it and T007
measures it in a browser.

## 2026-09-22T18:44:00Z · Implementer US1 · T006

Did: `demo/views.py` (`LineChartView`), `demo/urls.py` (`line/`), `demo/menus.py` (the line chart as
the first — and so far only — entry in `CHART_TYPE_PAGES`, which brings the Charts group into the
sidebar), `demo/templates/demo/line.html` (two examples, following `chart_region.html`'s
`c-section`/`show_code`/`cotton:verbatim` convention: a single line chart, then a line chart beside
a bare `<c-echarts.region>` to show the two do not interact — US1 scenario 4, which T007 measures in
a browser), and `demo/templates/base.html` (loads `echarts-chart.js` beside `chart-region.js`).
`tests/test_demo.py`: extended the sidebar's expected href list with `/line/`; the "chart region is
top-level" assertion previously asserted no Charts group existed at all, which is no longer true
once a chart type does — rewrote it to assert the region precedes the group rather than sitting
inside it, and added one test that the line page is filed under Charts.
Verified: `poetry run pytest tests/test_demo.py -v` — 30 passed. Widened to
`poetry run pytest tests/ --ignore=tests/test_components/test_region_e2e.py --ignore=tests/test_components/test_delivery_e2e.py --ignore=tests/test_components/test_failures_e2e.py -q`
(the whole suite short of the pre-existing e2e files T007 has not written yet) — 82 passed. Manually
smoke-tested `/line/` via Django's test `Client`: 200, both examples' markup and options scripts
present. `ruff check`/`ruff format --check` on the changed Python files — clean.
Concern: `djlint --check` reports both `mvp_charts/templates/cotton/echarts/region.html` (pre-existing,
FS-001) and `demo/templates/demo/chart_region.html`/`overview.html` (pre-existing) as non-conformant
to its own reformat opinion, so it does not appear to be an enforced gate in this repo despite the
`[tool.djlint]` config in `pyproject.toml`. `demo/templates/demo/line.html` follows the existing
files' actual indentation convention rather than djlint's preference, for consistency with them.
Next: T007 — the browser test.
Watch: nothing.

## 2026-09-22T18:52:00Z · Implementer US1 · T007

Did: `tests/test_components/test_line_e2e.py`, following `test_region_e2e.py`'s shape — reads a live
ECharts instance back via `echarts.getInstanceByDom` and asserts the series data and category values
match what the demo page wrote, in order; asserts a line chart and the demo's bare region on the same
page both reach `ready` and only the chart has an instance (US1 scenario 4 — neither reads nor
changes the other's state); and asserts the chart's region still exactly fills its wrapper after a
window resize (FR-005, US1 scenario 5).
Verified: `poetry run pytest tests/test_components/test_line_e2e.py -v` — 8 passed on the first run,
against a real Chromium and the real ECharts CDN build (no stand-in). `ruff check`/`ruff format
--check` — clean.
Next: T008 — README and CHANGELOG.
Watch: nothing.

## 2026-09-22T18:58:00Z · Implementer US1 · T008

Did: README — replaced the pitch example at the top, which named attributes (`:data`, `x`, `y`,
`title`) the component never actually took; updated Status to say a chart type exists; added a
"Drawing a line" section between "Placing a chart region" and "Keeping its shape" showing the
complete markup including the sizing wrapper (character-for-character what the demo page renders,
checked by hand the way `TestDocumentedExample` checks the region example), and stating plainly that
`:values`/`:labels` take a Python value written with a colon, never text (FR-002a, FR-007); the
install section now shows three script lines — ECharts, `chart-region.js`, `echarts-chart.js` — with
the surrounding prose updated from "two"/"both" to "three"/"all three". CHANGELOG: an `[Unreleased]`
entry for the line chart, its browser module, the demo page and the README changes; the section's own
opening line no longer claims nothing draws.
Verified: `poetry run pytest tests/test_demo.py -q` — 30 passed (`TestDocumentedExample` still passes
against the untouched region example). Confirmed by hand that the new "Drawing a line" example's
normalized text is a substring of the rendered `demo/templates/demo/line.html`.
Next: full verify, then the completion report.
Watch: nothing.
