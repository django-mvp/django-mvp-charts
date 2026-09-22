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
