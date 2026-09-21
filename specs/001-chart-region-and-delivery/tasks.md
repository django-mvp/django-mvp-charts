# Tasks — 001, a chart region and the library that draws into it

23 tasks in four stories, in priority order. Each task names the test that fails first and the
requirement or criterion it closes. Tests before implementation, one commit per task.

Paths are repository-relative. `verify` means `poetry run pytest` plus
`poetry run pre-commit run --all-files`; per-task runs are the narrowest scope that covers the
change, and the full verify runs once per story before its report.

---

## US1 — Put a chart region on a page (P1, issue #7)

### T001 — the region renders, fills its wrapper, and carries its name and text alternative

*Test first*: `tests/test_components/test_region.py::TestChartRegion` — render
`<c-echarts.region name="…" description="…" />` inside a wrapper and assert against the rendered
output: one `figure` carrying `data-mvp-chart-region`, a drawing surface with `role="img"` and the
author's name as its accessible name, a `figcaption` carrying the description as text, and the
sizing classes that make the region exactly its wrapper. No class-presence assertion stands alone —
each one is asserted as part of the element contract it belongs to.

*Implement*: `mvp_charts/templates/cotton/echarts/region.html` per plan.md *The region's markup*. Add
`"tests/test_components/"` to `[tool.forge.conformance] non-mirror-paths` in `pyproject.toml` beside
the two entries already there — this directory's subject is a template, so there is no module to
mirror, and Article X requires the declaration rather than inferring it.

Closes FR-001, FR-002, FR-003, FR-005. Serves SC-001, SC-006.

### T002 — several regions on a page are separately identifiable

*Test first*: `tests/test_templatetags/test_mvp_charts.py` — `{% chart_region_id %}` returns
`mvp-chart-region-1`, then `-2`, within one request, and restarts for a new request;
`tests/test_components/test_region.py` — two regions rendered in one template have different ids and
each `aria-describedby` points at its own `figcaption`.

*Implement*: `mvp_charts/templatetags/mvp_charts.py` with `ChartRegionAssets` holding the per-request
counter, and an `id` attribute on the component that an author may supply instead.

Closes FR-004. Serves SC-002.

### T003 — a region with no name or no text alternative says which is missing

*Test first*: `tests/test_components/test_region.py::TestMissingAttributes` — omit the name, omit the
description, pass each as an empty string, and assert the rendered output carries a `role="alert"`
message naming the missing attribute and contains no chart region at all.

*Implement*: the guard in `region.html`.

Closes FR-006. Serves SC-006.

### T004 — the package's messages are translatable

*Test first*: a test asserting every message the region can render is wrapped for translation — the
rendered page under a second active language shows the translated string from a test-only catalog
entry rather than the English one.

*Implement*: `{% trans %}` / `{% blocktrans %}` throughout the templates, `mvp_charts/locale/` with a
base English catalog, `makemessages` clean over the package.

Closes Article VIII for this feature's strings.

### T005 — the demo shows a placed region, and the Charts section appears

*Test first*: `tests/test_demo.py` — the new page renders, contains one chart region inside a wrapper
whose height is visible in the markup, contains five regions with five distinct ids, and the sidebar
now carries a Charts section with an entry for the page.

*Implement*: `demo/views.py`, `demo/urls.py`, `demo/templates/demo/chart_region.html` (examples
wrapped in `{% show_code %}{% cotton:verbatim %}`), and the first entry in `CHART_PAGES`.

Closes FR-007. Serves SC-001, SC-002.

### T006 — README documents placing a region, wrapper included

*Test first*: not a code test — the README example is run against the branch by rendering it in the
demo page from T005, which is the same markup.

*Implement*: README section on placing a region, stating that the wrapper supplies the height and
that the region has none of its own, plus the CHANGELOG entry.

Closes Article VI for US1.

### T007 — in a real browser, the region's box is its wrapper's box

*Test first*: `tests/test_components/test_region_e2e.py::TestRegionFillsItsWrapper` — load the demo
page, measure the wrapper and the region with `getBoundingClientRect`, assert they match on both
axes, and assert the same for all five regions on differently sized wrappers.

*Implement*: nothing new if T001 is right. A failure here is a sizing defect in the markup.

Closes SC-001, SC-002 as measured rather than asserted.

---

## US2 — The charting library reaches the browser (P2, issue #8)

### T008 — the development delivery is one pinned, integrity-checked tag the project places

*Test first*: `tests/test_components/test_cdn.py` — `<c-echarts.cdn />` renders exactly one script
tag, at a pinned version, carrying an integrity hash and `crossorigin="anonymous"`; and no template
shipped in `mvp_charts/` other than that component references a remote origin at all.

*Implement*: `mvp_charts/templates/cotton/echarts/cdn.html`; add the line to the demo's
`base.html` in `{% block extra_js %}`.

Closes FR-008, FR-010. Serves SC-003.

### T009 — the module loads once per page, and only when a region is on it

*Test first*: `tests/test_templatetags/test_mvp_charts.py` — `{% chart_region_assets %}` returns the
script tag on its first call in a request and the empty string afterwards;
`tests/test_components/test_region.py` — a page with five regions carries exactly one
`chart-region.js` tag, and a page with none carries no reference to the package's static files at
all.

*Implement*: the `chart_region_assets` tag, called from `region.html`; the module itself lands as a
stub whose behaviour arrives in US3 and US4.

Closes FR-010 for the package's own asset. Serves SC-008.

### T010 — a region uses whatever supplies `window.echarts`, with no setting either way

*Test first*: `tests/test_components/test_delivery_e2e.py` — two pages, identical settings: one where
the CDN component supplies the library, one where a local script assigns `window.echarts` the way a
project's bundle does. In both, the region reports nothing and the library is reachable from the
page.

*Implement*: the module's library lookup; the demo's second delivery example.

Closes FR-009. Serves SC-004.

### T011 — the namespace states the ECharts range it renders against

*Test first*: `tests/test_components/test_cdn.py` — the version the delivery component pins falls
inside the range the package declares, and the declared range is a valid specifier.

*Implement*: `mvp_charts/versions.py`, quoted in README beside both delivery routes; `deptry` stays
clean because nothing was added to the dependency list.

Closes FR-011, FR-012.

### T012 — a project that places no region loads nothing new

*Test first*: `tests/test_components/test_region_e2e.py` — load a demo page carrying no region and
assert no request was made for `chart-region.js` and no third-party origin was contacted beyond what
the page already loads without this package.

*Implement*: nothing new if T009 is right.

Closes SC-008.

---

## US3 — A region that cannot draw says why (P3, issue #9)

### T013 — a missing library is reported in the page, after the wait

*Test first, without a browser*: `tests/test_components/test_region.py::TestFailureMessages` — render a
region and assert both messages are already in the page as `data-` attributes, with the wording the
reader will see and translated under a second active language. The message text is server-rendered,
so it is asserted on every pull request whatever CI does about browsers, and only the timing is left
to the browser test.

*Then in a browser*: `tests/test_components/test_region_e2e.py::TestMissingLibrary` — load the failures
page with no library available, wait past the grace window, and assert the region's own area now shows
the message naming ECharts and both ways to supply it, in the page rather than only in the console.

*Implement*: the module's wait-then-report path; the messages passed in as `data-` attributes through
`{% trans %}`.

Closes FR-013, FR-016. Serves SC-005.

### T014 — a library that arrives late is never reported missing

*Test first*: the same file — a page that assigns `window.echarts` after a delay, asserting no message
ever appears and that the region resolves once it arrives.

*Implement*: resolve-on-appearance polling, cleared as soon as it resolves.

Closes FR-018.

### T015 — a wrapper with no resolved height is reported, readably

*Test first*: the same file — a region in a wrapper with a percentage height inside a content-sized
ancestor. Assert the message is in the region, and that the region's measured height is enough for
the message to be read.

*Implement*: the first-visibility measurement and the inline readable height.

Closes FR-014. Serves SC-005.

### T016 — a region that loses its height later reports nothing

*Test first*: the same file — a region that renders correctly in an open panel, then the panel
collapses. Assert no message appears, and that reopening the panel restores the region's size.

*Implement*: the measured-once rule.

Closes FR-015.

### T017 — one failing region leaves the others working

*Test first*: the same file — a page with a failing region beside working ones; assert the failing one
carries its message and every other region still fills its wrapper and still dispatches its resize
event.

*Implement*: per-region isolation in the module.

Closes FR-017.

### T018 — the demo shows both failure states deliberately

*Test first*: `tests/test_demo.py` — the failures page renders, carries a region with no library, a
region with no resolved height, a region missing its text alternative, and one working region; the
sidebar carries its entry.

*Implement*: `demo/templates/demo/chart_region_failures.html`, its view, route and menu entry, and the
README section naming both messages and what each one means. The page overrides
`{% block extra_js %}` with an empty block — no `{{ block.super }}` — so it does not inherit the
development delivery line from the demo's `base.html`. Without that override the library loads and the
missing-library state cannot occur on the one page whose subject it is.

Closes FR-019. Serves SC-005.

---

## US4 — The region holds its shape as the page changes (P4, issue #10)

### T019 — a window resize leaves the region filling its wrapper

*Test first*: `tests/test_components/test_region_e2e.py::TestHoldsItsShape` — render, resize the
viewport, assert the region's box still equals its wrapper's with no clipped or leftover area.

*Implement*: nothing new if the sizing is CSS; the assertion is what proves it.

Closes FR-020. Serves SC-007.

### T020 — a wrapper resized without the window changing is followed

*Test first*: the same class — change the wrapper's height by script, assert the region follows and
that a resize event carrying the new box was dispatched.

*Implement*: the `ResizeObserver` and the `mvp-chart-region:resize` event.

Closes FR-021. Serves SC-007.

### T021 — a region revealed after load fills its wrapper then

*Test first*: the same class — a region inside a container that is hidden at load; reveal it and
assert it fills the container and reports no height failure.

*Implement*: the `IntersectionObserver` path shared with T015.

Closes FR-022. Serves SC-007.

### T022 — a burst of size changes settles once, at the final size

*Test first*: the same class — count `mvp-chart-region:resize` events while changing the wrapper's
size many times within a few frames; assert the final measurement is the final size and that the
count is far below the number of changes.

*Implement*: `requestAnimationFrame` coalescing.

Closes FR-023.

### T023 — the resize contract is documented

*Test first*: not a code test — the documented event name and payload are the ones the T020 test
subscribes to.

*Implement*: README section on the event a chart type subscribes to, what it carries and when it
fires; CHANGELOG entry completed for the feature.

Closes Article VI for US4.
