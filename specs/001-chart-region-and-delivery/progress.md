# Progress — 001, a chart region and the library that draws into it

## 2026-09-21T12:50Z · Plan · S3

**Did**: branched `001-chart-region-and-delivery` from `origin/main` at 74c1f30 (the commit the
specification merged on), installed the environment, wrote `plan.md`, `research.md` and `tasks.md`,
and created this ledger with the spec gate recorded from the merged specification pull request.

**Verified**: `poetry run pytest` — 15 passed, on 74c1f30, before anything was written. The demo
project serves on its own port from this worktree.

**Next**: design review, then US1.

**Watch**: the browser tests cannot run on CI until one line is added to this repository's test
workflow, and automation does not push workflow files. Recorded in `plan.md`, filed as an issue, and
stated in the pull request rather than left implicit.

## 2026-09-21T13:05Z · Implementer US1 · T001

**Did**: wrote `mvp_charts/templates/cotton/echarts/region.html` per plan.md *The region's markup* —
a `figure` carrying `data-mvp-chart-region`, sized `relative h-full w-full`, a `role="img"` drawing
surface carrying the author's `name` as its accessible name, and a `figcaption` carrying `description`
as reachable text. The id is a fixed literal for this task; T002 replaces it with the per-request
generator. Declared `tests/test_components/` in `[tool.forge.conformance] non-mirror-paths`.

**Verified**: `poetry run pytest tests/test_components/test_region.py::TestChartRegion` — 5 passed.
`poetry run pre-commit run --files mvp_charts/templates/cotton/echarts/region.html
tests/test_components/__init__.py tests/test_components/test_region.py pyproject.toml` — all hooks
passed.

**Next**: T002 — per-request ids so several regions on one page stay independently identifiable.

**Watch**: nothing new.

## 2026-09-21T13:15Z · Implementer US1 · T002

**Did**: added `mvp_charts/templatetags/mvp_charts.py` with `ChartRegionAssets`, holding the
per-request region counter, and the `chart_region_id` tag wrapping it. `region.html` now takes `id`
as an optional author-supplied prop and calls the tag only when it is omitted.

**Verified**: `poetry run pytest tests/test_templatetags/ tests/test_components/test_region.py` — 11
passed. `poetry run mypy mvp_charts/templatetags/mvp_charts.py` — clean. `poetry run pre-commit run
--files mvp_charts/templates/cotton/echarts/region.html mvp_charts/templatetags/__init__.py
mvp_charts/templatetags/mvp_charts.py tests/test_templatetags/__init__.py
tests/test_templatetags/test_mvp_charts.py tests/test_components/test_region.py` — all hooks passed.

**Next**: T003 — a region with no name or no text alternative reports which is missing.

**Watch**: nothing new.

## 2026-09-21T13:22Z · Implementer US1 · T003

**Did**: `region.html` now guards on `name`/`description`: when either is missing or an empty
string, it renders a `role="alert"` message naming which one, translated with `{% trans %}`, and
renders no region at all — no `figure`, no id generated. Empty string and omission both trip the
guard, per D5.

**Verified**: `poetry run pytest tests/test_components/test_region.py` — 14 passed (full file, not
just the new class, since the guard sits in front of every other path through the same template).
`poetry run pre-commit run --files mvp_charts/templates/cotton/echarts/region.html
tests/test_components/test_region.py` — all hooks passed.

**Next**: T004 — ship the base English catalog and prove the wrapped strings translate.

**Watch**: nothing new.
