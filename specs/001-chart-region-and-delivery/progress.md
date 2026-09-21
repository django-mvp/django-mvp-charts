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

## 2026-09-21T13:30Z · Implementer US1 · T004

**Did**: ran `makemessages -l en` and `compilemessages` to ship `mvp_charts/locale/en/LC_MESSAGES/`,
the base English catalog for the three guard messages (already wrapped in `{% trans %}` since T003)
and the app's `verbose_name`. Added `TestTranslatedMessages` in `test_region.py`, backed by a
test-only fixture catalog at `tests/locale/de/LC_MESSAGES/` — not shipped — translating one message,
activated via `override_settings(LOCALE_PATHS=...)` and `translation.override("de")`.

**Verified**: probed the mechanism before trusting the test (craft-tdd's rule for a criterion that
might already be satisfied) — rendering the same region under `translation.override("de")` with no
`LOCALE_PATHS` override shows the English source string, not the German one, confirming the test
exercises the catalog rather than passing regardless. `poetry run pytest
tests/test_components/test_region.py` — 16 passed. `poetry run pre-commit run --files
tests/test_components/test_region.py tests/locale/de/LC_MESSAGES/django.po
mvp_charts/locale/en/LC_MESSAGES/django.po` — all hooks passed.

**Next**: T005 — the demo shows a placed region and the Charts section appears.

**Watch**: nothing new.

## 2026-09-21T13:35Z · Orchestrator · T005

**Handover**: the run that started this feature was stopped mid-T005 at the owner's instruction and
picked up here from `c4222eb`. T001–T004 were committed and green; T005's tests were written and
red, which is where it resumed.

**Repaired first**: the in-flight edit had inserted `TestChartRegionPage` into the middle of
`TestDocumentationSurface`, leaving two classes of that name — the second shadows the first, so four
already-passing tests had silently stopped being collected. The new class moved to the end of the
file, the original class made whole, and its missing `reverse` import added.

**Did**: `demo/views.py` gained `ChartRegionView`, `demo/urls.py` its route, `demo/menus.py` its
first `CHART_PAGES` entry — which is what brings the Charts section into the sidebar — and
`demo/templates/demo/chart_region.html` shows one region in a 320px wrapper through
`{% show_code %}`, four more at four different heights, and a note on why the wrapper is not
optional. Removed `mvp_charts/templates/cotton/echarts/.gitkeep`: the directory holds a real
component now, and `test_app.py` asserts its existence either way.

**Two pre-existing tests were restated rather than weakened.** `test_that_is_the_only_entry` and
half of `test_no_section_is_drawn_with_nothing_under_it` asserted the sidebar's contents *while no
chart page existed* — their own docstrings said so. The enduring intent is that the sidebar holds
exactly the pages that exist and that no node is ever drawn with `href="None"`. The `href="None"`
guard is untouched and still the point of the second test; the first now asserts the navigation's
hrefs are exactly `/` and `/chart-region/`, which is the same claim at the new state and a stronger
assertion than counting `<li`.

**One defect this feature created, fixed here**: the `sidebar_navigation` fixture cut from the
navigation's label to the *first* `</ul>`. A section with pages under it nests a list, so that cut
now stopped at the first section and dropped the rest — an assertion about what the sidebar holds
would have passed without looking at most of it. It cuts to the matching close now.

**Verified**: `poetry run pytest` — 38 passed. Dev server restarted from this worktree;
`/chart-region/` serves 200 and carries five regions with five distinct ids.

**Next**: T006 — README section on placing a region, wrapper included, and the CHANGELOG entry.

**Watch**: nothing new.

## 2026-09-21T13:45Z · Orchestrator · T006

**Did**: README gained a *Placing a chart region* section — the example with its wrapper, why the
wrapper carries the height and the region has none, both required attributes and what each is for,
and the `id` attribute. Status line updated from "no components are written yet". CHANGELOG entry
for the region, the per-request numbering, the first locale catalog and the demo page.

**Went beyond the task**: the task called for no code test, on the grounds that rendering the
example in the demo page is what exercises it. That only holds while the two stay identical, and
nothing was keeping them identical. Added `TestDocumentedExample`, which extracts the README's
example and asserts it is the markup the demo template carries.

**Verified**: reinstated the defect before trusting the test — changing one attribute in the README
example fails it, restoring it passes. `poetry run pytest tests/test_demo.py` — 19 passed.

**Next**: T007 — measure in a real browser that the region's box is its wrapper's box.

**Watch**: the browser tests from T007 on need `install-playwright: true` on the `call-tests` job,
which is a workflow file and so the repository owner's to add. Until then they pass locally and
skip on CI.

## 2026-09-21T13:55Z · Orchestrator · T007

**Did**: `tests/test_components/test_region_e2e.py::TestRegionFillsItsWrapper` loads the chart
region page in chromium and measures every region against the element wrapping it. The comparison
is the region's `offsetWidth`/`offsetHeight` against the wrapper's `clientWidth`/`clientHeight` —
the region's own box against the box it was given. Comparing both elements' `getBoundingClientRect`
would differ by the wrapper's border width and prove nothing about the region.

Three assertions guard the measurement itself: that five regions were found at all, since every
other assertion is an `all()` over a list an empty page would satisfy; that the five wrappers are
genuinely five different heights, so the claim holds across sizes; and that no region measured zero,
since matching a wrapper that is itself nothing is not a pass.

`chromium_or_skip` in `tests/conftest.py` skips instead of failing where no browser is installed, so
CI reports these as skips until the workflow installs one.

**One thing this needed that the plan did not foresee**: the browser fixtures run a test inside a
greenlet with an event loop under it, and Django refuses synchronous database work from an async
context, so building the test database for `live_server` raised before any page loaded. Scoping the
allowance to the browser tests does not work — pytest-django builds the database from an autouse
fixture, which runs before any fixture a test can ask for. It is set once in `pyproject.toml`
instead, with the reasoning beside it: this package has no models, no views and no ORM calls, so the
only database work in the suite is the harness building its own test database, and the check has
nothing here to protect.

**Verified**: reinstated the defect before trusting the measurement — dropping `h-full` from the
region collapses it to zero height and fails two of the four tests; restoring it passes all four.
`poetry run pytest` — 43 passed. `poetry run pre-commit run --all-files` — all hooks passed.

**US1 is complete.** T001–T007 all committed and green.

**Next**: T008 — the development delivery, as one pinned integrity-checked tag the project places.

**Watch**: the browser tests need `install-playwright: true` on the `call-tests` job before CI runs
them rather than skipping them. That is a workflow file, so it is the repository owner's to add.

## 2026-09-21T14:15Z · Orchestrator · T008–T012

**Did**: `<c-echarts.cdn />` renders one pinned, integrity-checked script tag that a project places
in its own base template. `mvp_charts/versions.py` holds the URL, the pinned version, the hash and
the range the namespace claims, so the three values that have to agree cannot drift apart in markup.
`{% chart_region_assets %}` emits the package's own module the first time a region on a request asks
for it and nothing afterwards, so five regions load it once and a page with none loads nothing.
`chart-region.js` gained its library resolution: it reads `window.echarts`, and a region that finds
nothing keeps looking rather than judging at its first instant.

**The integrity hash is real.** Fetched `echarts@6.1.0` from the CDN, confirmed the file reports
`version:"6.1.0"`, and computed the sha384 from those bytes. A hash written from memory would be a
hash the browser silently refuses, which looks exactly like a network fault.

**Split T010 across two stories, deliberately.** As written it asserts a region "reports nothing"
under either delivery, but the reporting is US3's work and the plan has the module land as a stub
here. The half that belongs to this story — a region resolves the library by either route, with no
setting either way — is implemented and tested now through an observable `waiting` → `ready` state
on the element. US3 adds the states for the two ways a region cannot draw, on the same attribute.

**Probe pages rather than demo pages.** `tests/templates/probe/` and three routes in `tests/urls.py`
put a region in exactly the situation each browser test needs: the library arriving as a separate
file, arriving inline, arriving late, and a page with no region at all. Contorting a page a reader
visits into those shapes would have made the demo worse to read for the sake of the suite.

**Not tested, deliberately**: whether the public CDN is reachable. The delivery component's tag
being pinned and integrity-checked is this package's whole contribution to that route, and it is
asserted from rendered output. Fetching the file during a test run would make the suite fail for
reasons that say nothing about this package. The browser tests serve a stand-in.

**One pre-existing test restated**: `test_no_javascript_is_rendered` asserted no script tag at all,
which was the same claim while the region had no module. It now asserts what it was always about —
the author writes none, the package inlines none, and whatever a region needs arrives as one
external module. The `x-data` half is untouched: the plan rejected a per-region framework component
and that rejection still holds.

**Verified**: reinstated the defect before trusting the no-region assertions — putting a region on
the probe page that should have none fails them, removing it passes. `poetry run pytest` — 70
passed. `poetry run pre-commit run --all-files` — all hooks passed.

**Next**: T013 — a missing library reported in the page, after the wait.

**Watch**: nothing new.

## 2026-09-21T14:45Z · Orchestrator · T013–T018

**Did**: both messages now travel with the region as data attributes rendered through the package's
catalog, so their wording and their translation are asserted without a browser and the module holds
no English. The module reports a missing library only after the page has fired `load` and a further
three seconds, judges height at a region's first visibility through an `IntersectionObserver`, never
judges a region twice, and sets a readable minimum height only where the alternative is an invisible
failure. Each region is initialised in its own `try`/`catch`. A second demo page shows all three
states deliberately, suppressing the inherited delivery with an empty `extra_js` block.

**Two defects found by measuring rather than by reading.** The browser insisted a region would not
fill its wrapper, and both causes were mine from this session:

1. The explanatory comment added to `region.html` used `{# … #}` across several lines. Django's
   comment tag is single-line, so everything after the first line was served to the reader as page
   text — an explanation of the component printed into the page, and an element sized by a paragraph
   that should not exist. Nothing raises. Now `{% comment %}`, and
   `tests/test_components/test_shipped_templates.py` fails on any shipped template that opens a
   comment it does not close on the same line. Confirmed by reinstating it.
2. The probe pages loaded no stylesheet. The package ships none by design and its markup uses
   classes django-mvp's prebuilt one emits, so `h-full` never applied and `sr-only` never hid the
   caption — the test was measuring a line of caption text and reading it as a sizing defect in the
   component. The probe pages link the stylesheet now.

**One assertion was wrong rather than the page**: the failures page test asserted the CDN host was
absent, and django-mvp serves its icon font from the same host. Narrowed to ECharts by name.

**Also added**: a check that every user-facing string in a shipped template is wrapped for
translation, since the same file was already walking the templates.

**Verified**: `poetry run pytest` — 100 passed. Both new guards were confirmed against the defects
they exist for.

**Next**: T019–T023 — the resize contract.

**Watch**: the missing-library browser tests wait out the grace window, so the browser suite now
takes around 35 seconds. Acceptable; worth revisiting only if it grows.
