# Implementation Plan: A chart region, and the library that draws into it

**Branch**: `001-chart-region-and-delivery` | **Date**: 2026-09-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-chart-region-and-delivery/spec.md`

## Summary

Ship one Cotton component — a chart region in the `echarts` namespace — that a template author
places inside a wrapper the project already sized, plus the means for ECharts to reach the browser
and the in-page reporting for the two states where a region cannot draw. Nothing is drawn: the
region is the space a later chart type will draw into, and this feature delivers the space, the
library's presence, the failure messages and the sizing behaviour.

Server-rendered markup covers placement, the accessible name and text alternative, and the missing
attribute report. A small dependency-free JavaScript module, shipped in this package's own static
files and loaded once per page only when a region is on it, covers the three things the server
cannot know: whether the library arrived, whether the wrapper resolved to a usable height, and what
size the wrapper is now.

## Technical Context

**Language/Version**: Python 3.12+ (CI matrix 3.12 and 3.13), Django 5.2 and 6.0

**Primary Dependencies**: django-mvp ≥ 0.23.0 (layout primitives, prebuilt daisyUI stylesheet, the
bundled front-end runtime); django-cotton, pinned by django-mvp and deliberately undeclared here.
No new runtime dependency.

**Front-end**: vanilla ES2020 in one file, `mvp_charts/static/mvp_charts/js/chart-region.js`. No
build step, no bundler, no npm in this repository. ECharts is never vendored (Article XII).

**Charting library version**: ECharts 6.x. The development delivery pins 6.1.0 with a
subresource-integrity hash; the package declares the range it is known to render against and pins
nothing as a dependency.

**Storage**: N/A — presentation only, no models, no migrations.

**Testing**: pytest + pytest-django for the rendered-output contract; pytest-playwright (chromium)
for everything whose subject is the browser. Both already ship in the `mvp-shared[test]` bundle.

**Target Platform**: any browser the host project supports; the demo project runs on the
development server on port 8019.

**Project Type**: installable Django package plus a demo project that is never deployed.

**Performance Goals**: a burst of wrapper size changes coalesces to one measurement per animation
frame, so a drag-resize does not queue work per event.

**Constraints**: the package ships no stylesheet, so every class in its markup must be one the
prebuilt django-mvp stylesheet already emits — verified by grep against
`mvp/static/css/django-mvp.css` rather than assumed. `min-h-*` utilities beyond `min-h-0`,
`min-h-full` and `min-h-screen` are **not** emitted, and neither are fixed `h-*` heights such as
`h-64`, which is why the failure state's readable height is an inline style and the demo's wrappers
carry explicit inline heights.

**Scale/Scope**: one component namespace, two components (`region`, `cdn`), one template-tag
module, one JavaScript module, two demo pages, four stories, 23 tasks.

## Constitution Check

*GATE: passed before Phase 0. Re-checked after the design below was written.*

| Article | How this plan satisfies it |
|---|---|
| I — Test-First | Every task below names the test that fails first. The rendered-output contract is pytest; the browser guarantees are Playwright. |
| II — Simplicity | One template-tag module, one JavaScript module, no classes for behaviour the browser already has. No Alpine component, no registry, no settings. |
| III — Anti-Abstraction | No shared "plumbing" layer for a second namespace that does not exist. The region lives in the `echarts` namespace and is factored out when a second backend arrives. |
| IV — Integration-First | The contract a later chart type consumes — the drawing surface element and a resize event carrying the measured box — is designed and tested here, before any chart type exists. |
| V — Security | Every author-supplied value is rendered through the template layer. The development delivery pins a version and carries an integrity hash; no third-party origin is added on a reader's behalf (Article XII). |
| VI — Documentation | README gains the placement example with its wrapper, both delivery routes, the supported ECharts range and the two failure messages. CHANGELOG entry lands in the same pull request. |
| VII — Dependency discipline | No new dependency of any kind. `deptry` unaffected. |
| VIII — Internationalization | Every message the region can show is wrapped for translation, and the package gains `locale/` with a base English catalog — its first user-facing strings arrive with this feature. |
| IX — Data-model conventions | N/A. No models, no migrations. |
| X — Test structure | `tests/test_templatetags/test_mvp_charts.py` mirrors `mvp_charts/templatetags/mvp_charts.py`. Component and browser tests have no Python module to mirror, so `tests/test_components/` is added to the `[tool.forge.conformance] non-mirror-paths` list in `pyproject.toml`, which currently names only `tests/test_app.py` and `tests/test_demo.py`. That edit is part of T001, not an assumption. |
| XI — Cohesion | The template tags share a subject — the region's per-request identity and its one-time asset tag — so they are methods on one class, with the tags as thin registered wrappers. |
| XII — No library vendored or served | ECharts is never committed, never placed in static files, never bundled. The development delivery is a component the **project** places in its own base template; no region injects a script. |
| XIII — One namespace per backend | The region is `<c-echarts.region>`, in the namespace that names the library whose presence it checks for. |
| XIV — Pass through rather than mirror | The region names two attributes, both of which the accessibility contract requires. Nothing else is named. |
| XV — Rendered output is a contract | Assertions are against rendered output and against measured boxes in a real browser, never against the presence of a class name. The name and the text alternative are required and reported when missing, never defaulted. |
| XVI — Compatibility | Pre-1.0 surface, CHANGELOG entry for the new components, supported ECharts range stated per namespace. |

**One constraint this plan cannot satisfy inside its own pull request**, recorded rather than worked
around: the browser tests need `install-playwright: true` on the `call-tests` job in
`.github/workflows/tests.yml`. Editing a workflow file is outside what automation may push in this
organisation, so the line is the repository owner's to add. Until it is there the browser tests
skip on CI while passing locally, and the pull request says so. Tracked as a follow-up issue rather
than left in a comment.

## Project Structure

### Documentation (this feature)

```text
specs/001-chart-region-and-delivery/
├── spec.md              # on main since the specification merged
├── decisions.md         # on main; appended to by this stage and by implementation
├── plan.md              # this file
├── research.md          # what was established before the design was chosen
├── tasks.md             # the task graph
├── progress.md          # per-task narrative
└── feature-state.json   # the ledger
```

### Source (repository root)

```text
mvp_charts/
├── templates/cotton/echarts/
│   ├── region.html            # <c-echarts.region name="…" description="…" />
│   └── cdn.html               # <c-echarts.cdn /> — the development delivery
├── templatetags/
│   ├── __init__.py
│   └── mvp_charts.py          # per-request region ids + the once-per-page asset tag
├── static/mvp_charts/js/
│   └── chart-region.js        # library wait, height check, resize contract
├── locale/en/LC_MESSAGES/
│   └── django.po              # base English catalog
└── versions.py                # the ECharts range this namespace claims

demo/
├── templates/demo/
│   ├── chart_region.html      # placing a region, and five independent regions
│   └── chart_region_failures.html
├── views.py                   # two more MVPTemplateViews
├── urls.py
├── menus.py                   # CHART_PAGES gains its first entries
└── templates/base.html        # includes <c-echarts.cdn /> in extra_js

tests/
├── test_components/           # no Python module to mirror — declared non-mirror
│   ├── __init__.py
│   ├── test_region.py         # rendered-output contract
│   ├── test_cdn.py            # the development delivery's markup, and no remote script elsewhere
│   ├── test_region_e2e.py     # placement, delivery, failures, resize — real browser
│   └── test_delivery_e2e.py   # bundle-supplied library, late arrival
├── test_templatetags/
│   ├── __init__.py
│   └── test_mvp_charts.py
├── conftest.py                # browser guard, region fixtures
└── test_demo.py               # the two new pages, the Charts section
```

**Structure Decision**: the package keeps the layout it was scaffolded with. Components go in the
`echarts` namespace directory Cotton already resolves, the JavaScript goes in the package's own
static namespace, and the demo gains pages the same way `AGENTS.md` already describes. Nothing
moves.

## Design

### The region's markup

```html
<figure id="{{ id }}" class="relative h-full w-full" data-mvp-chart-region>
  <div class="absolute inset-0"
       role="img"
       aria-label="{{ name }}"
       aria-describedby="{{ id }}-description"
       data-mvp-chart-region-surface></div>
  <figcaption id="{{ id }}-description" class="sr-only">{{ description }}</figcaption>
</figure>
```

- `relative h-full w-full` is the whole of the sizing rule: the region is exactly its wrapper, and
  it has no height of its own (FR-002, FR-003). A wrapper that resolves to nothing gives a region
  that resolves to nothing, which is the case US3 reports.
- The drawing surface is absolutely positioned inside the figure so a future chart type can be
  handed a box whose size never depends on what is drawn in it.
- `figure` + `figcaption` carries the text alternative as real text rather than an attribute, and
  `sr-only` keeps it out of the visual layout while leaving it in the accessibility tree and in the
  page's text (FR-005, SC-006).
- `id` comes from the template tag below when the author does not supply one, so several regions on
  a page are separately identifiable and `aria-describedby` always points at the right caption
  (FR-004).

**A missing name or text alternative replaces the region rather than degrading it** (FR-006): the
component renders a `role="alert"` message naming which attribute is missing, and renders no
region at all. Empty string and omitted are the same thing.

### Per-request identity, and one script tag per page

`mvp_charts/templatetags/mvp_charts.py` holds one class with two registered wrappers:

- `{% chart_region_id %}` → `mvp-chart-region-1`, `-2`, … counting per request. Deterministic
  numbering keeps the rendered-output tests readable; the counter lives on the request, so two
  concurrent requests never share one.
- `{% chart_region_assets %}` → the `<script defer src="…chart-region.js">` tag the **first** time
  it is called in a request, and the empty string every time after. A page with five regions loads
  the module once, and a page with no regions loads nothing at all (SC-008, FR-010).

Both are `simple_tag(takes_context=True)` wrappers over `ChartRegionAssets`, which is where the
state and the logic live (Article XI; registered template tags are the framework-shaped exception
for the wrappers themselves).

### How the library reaches the browser

The region reads one thing: the global `window.echarts`. That is the contract, and it is the same
sentence for both routes, which is what makes "no declaration either way" true (FR-009).

- **Development** — `<c-echarts.cdn />` renders a single pinned, integrity-checked script tag. The
  project places it in its own base template (the demo puts it in `{% block extra_js %}`). The
  package never emits it from a region (Article XII, FR-010).
- **Production** — the project's own bundle assigns the library to `window.echarts`. Nothing in the
  package changes, and no setting names which route is in play.

`mvp_charts/versions.py` states the range this namespace is known to render against
(`ECHARTS_SUPPORTED_VERSIONS = ">=6.0,<7.0"`) and the exact version the development delivery pins.
README quotes both (FR-011, FR-012).

### The JavaScript module

One file, no dependencies, idempotent, guarded so a second execution is a no-op. For each element
carrying `data-mvp-chart-region` it owns three jobs and nothing else.

**1. Is the library there?** (FR-013, FR-018) A region does not judge at first render. It resolves
as soon as `window.echarts` appears, and reports it missing only once the page has fired `load`
**and** a 3-second grace window has elapsed — a deferred or asynchronously loaded bundle is
ordinary, and accusing a correctly configured project is worse than saying nothing. The wait is
polled on a 100 ms interval and cleared the moment it resolves.

**2. Did the wrapper give it a height?** (FR-014, FR-015, FR-022) Measured at the region's **first
visibility**, not at first paint, using an `IntersectionObserver`: a region inside a collapsed panel
or an unselected tab has no height for reasons that are not a mistake, and judging it at load would
report every one of them. A region whose first visible measurement is under 1 px reports that it has
no height to fill and takes an inline `min-height` so the message can be read. A region that
measured fine once never reports height again, however small it later becomes.

**3. What size is the wrapper now?** (FR-020, FR-021, FR-023) A `ResizeObserver` on the figure,
coalesced through `requestAnimationFrame`, dispatches a `mvp-chart-region:resize` event on the
element carrying `{ width, height }`. That event is the contract a chart type will subscribe to in
a later feature; today it is what the browser tests measure and what proves a burst of changes
collapses to one measurement per frame rather than one per event.

Each region is initialised inside its own `try`/`catch`, so a region that cannot draw — for any of
these reasons — leaves every other region on the page working (FR-017). Messages are rendered into
the region's own surface, in the page, identically in development and production, and never only to
the console (FR-016).

### The two failure messages

Both are translatable, both name what is wrong and what would fix it, and both are placed where the
chart would have been:

- *This chart region has no charting library to draw with. Load ECharts in your base template with
  `<c-echarts.cdn />`, or expose it as `window.echarts` from your bundle.*
- *This chart region has no height to fill. Give the element around it a height — a chart region
  takes its size from its wrapper and has none of its own.*

The strings live in the JavaScript module, which cannot use `gettext`, so they are passed to it from
the server: the region element carries them as `data-` attributes rendered through `{% trans %}`.
That keeps one translation catalog for the package and keeps the module free of English.

**Because the messages are server-rendered, their text is asserted without a browser.** The module
decides *when* a message is shown; the page already carries *what* it says, so the wording, the
translation and the presence of both attributes are a rendered-output test that runs on every pull
request whatever CI does about browsers. The browser tests then assert only the part that is
genuinely browser-shaped: that the message becomes visible in the region's own area, and when.

### The demo project

Two pages, both under a new **Charts** section that arrives with the first of them (the empty
`CHART_PAGES` list in `demo/menus.py` is what currently keeps the section out of the tree):

1. **Chart region** — one region in a wrapper with an explicit inline height, its markup shown
   through `{% show_code %}`, and five regions in five differently sized wrappers to demonstrate
   independence (FR-007, SC-002).
2. **When a region cannot draw** — the missing-library state, the no-height state (a region in a
   wrapper with no resolved height), a missing text alternative, and one working region beside a
   failing one (FR-019).

**The failures page suppresses the inherited delivery.** The development delivery line lives in the
demo's own `base.html`, inside `{% block extra_js %}`, so every page in the project inherits it —
including the page whose subject is a region with no library. The failures page therefore overrides
that block with an empty one (no `{{ block.super }}`), which is ordinary Django block inheritance
across a grandparent template and needs no mechanism of its own. Without it the page loads ECharts,
`window.echarts` resolves, and the state the page exists to show cannot occur.

## Task graph

Four stories in priority order, each independently demonstrable, 23 tasks. Detail in
[tasks.md](./tasks.md).

| Story | Tasks | What lands |
|---|---|---|
| US1 (P1) | T001–T007 | The region component, per-request ids, the missing-attribute report, the i18n catalog, the demo page, README placement section, and a browser test that the region's box equals its wrapper's |
| US2 (P2) | T008–T012 | `<c-echarts.cdn />` with a pinned integrity-checked tag, the `window.echarts` contract, the asset tag, the stated version range, and browser tests for both delivery routes |
| US3 (P3) | T013–T018 | The library wait and its report, the first-visibility height check and its report, isolation between regions, and the failures demo page |
| US4 (P4) | T019–T023 | The resize contract: window resize, wrapper resize, reveal after being hidden, burst coalescing, and the documentation for the event a chart type will use |

## Complexity Tracking

| Violation | Why needed | Simpler alternative rejected because |
|---|---|---|
| A template-tag module for a package that renders no Python-side API | The region needs a per-page-unique id for `aria-describedby`, and the JavaScript must load once per page and never on a page without a region. Both are per-request facts a Cotton template cannot hold. | Hard-coding an id makes two regions on one page describe each other. Emitting the script from every region loads it five times on a five-region page; putting it in the project's base template loads it on every page whether or not a region is there, which SC-008 forbids. |
| A JavaScript module in a package whose position is that a template author writes no JavaScript | The three facts the region reports — library present, wrapper height, current size — exist only in the browser. FR-013, FR-014 and FR-020…FR-023 cannot be satisfied server-side at all. | Doing it with an inline Alpine component puts a copy of the logic in every region's markup and ties the package to Alpine's registration lifecycle. The author still writes no JavaScript, which is what the requirement is about. |
