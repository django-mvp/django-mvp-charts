# Research — 001, a chart region and the library that draws into it

What was established by reading the environment before the design was chosen. Findings, with how
each one was checked, so a later reader can re-check rather than trust.

## The host package already ships a front-end runtime

`mvp/templates/mvp/base.html` loads `js/django-mvp.js` with `defer` — a bundle carrying Alpine with
its persist plugin, htmx and theme-change — and exposes a `{% block extra_js %}` at the end of
`<body>` plus `{% block head %}` and `{% block styles %}`.

Consequence for this feature: Alpine is available, and was still not used. The region's behaviour is
three browser facts and one event; expressing it as an Alpine component would mean either a copy of
the logic inline in every region's markup or a registration that has to happen before Alpine starts.
`extra_js` is where a project puts the development delivery line.

## The stylesheet is prebuilt, so the class vocabulary is fixed

django-mvp ships `mvp/static/css/django-mvp.css` (446 KB, prebuilt daisyUI + Tailwind). A class it
does not emit does nothing at all, silently.

Checked by grep against that file. Emitted and usable: `relative`, `absolute`, `inset-0`, `h-full`,
`w-full`, `flex`, `items-center`, `justify-center`, `text-center`, `text-sm`, `text-xs`,
`font-medium`, `opacity-70`, `p-4`, `gap-2`, `sr-only`, `alert`, `alert-warning`, `alert-error`,
`card`, `card-body`, `grid`, `grid-cols-2`.

**Not emitted**: every `min-h-*` except `min-h-0`, `min-h-full`, `min-h-screen`; fixed heights such
as `h-64` and `h-48`. Two consequences the design takes on directly — the readable height of the
no-height message is an inline style set by the module, and the demo's wrappers carry explicit inline
heights, which also makes the wrapper's role visible in the example rather than hidden behind a
utility class.

## ECharts versions and the development delivery

`https://registry.npmjs.org/echarts/latest` reports **6.1.0** (checked 2026-09-21). jsDelivr serves
an immutable file per version, so a pinned URL plus a subresource-integrity hash is safe and is what
the delivery component renders.

The namespace claims `>=6.0,<7.0` — the range it is known to render against, which is the range it
is tested against. 5.x is not claimed, because nothing here has been run against it. The library is
not a dependency of this package and is not pinned as one (FR-011, Article XII).

## Browser tests: available locally, blocked on CI by one line

`pytest-playwright` ships in the `mvp-shared[test]` bundle and is importable in this repository's
virtualenv. Chromium was downloaded for it during this stage
(`poetry run playwright install chromium` → Chrome Headless Shell 153.0.8010.12), so the browser
tests run here.

CI is a different matter. `django-mvp/shared`'s reusable `tests.yml` takes an `install-playwright`
input (default `false`) and, when true, caches and installs chromium before the run. django-mvp
itself passes `install-playwright: true`. This repository's `.github/workflows/tests.yml` does not,
so on CI there is no browser.

The shared workflow is not the problem and neither is the test design: one line in this repository's
own workflow file fixes it. Automation in this organisation does not push `.github/workflows/**` at
all, deliberately, so that line is the repository owner's to add. Until it exists the browser tests
pass locally and skip on CI. The guard is the one django-mvp uses, and the gap is filed as an issue
rather than described in a comment nobody will read — skipped browser tests reading as passes is a
known way this goes wrong (django-mvp issue #171).

## How a bundling project "exposes the library"

There is no settings-based hook to design, because the contract is the global the library defines
itself. Loading ECharts from a script tag sets `window.echarts`; a bundle that imports it and
assigns `window.echarts = echarts` produces the same global. So one sentence covers both delivery
routes and nothing branches on configuration.

The browser test for the production route supplies the library exactly that way — a small local
script that assigns the global — and asserts the region reports nothing, with no setting changed
between the two runs (FR-009, SC-004).

## A region that is not visible yet has no height for a good reason

A percentage-height box inside an ancestor sized by its content resolves to zero — the case the
specification reports. So does a region inside a collapsed panel, a hidden tab, or a `display: none`
ancestor, and those are not mistakes (FR-015, FR-022).

`IntersectionObserver` separates them without guessing: measure when the region is first visible
rather than when it first paints. A region revealed later is judged then, on the size it actually
has, which is the same mechanism the reveal requirement needs. `ResizeObserver` covers wrapper
changes the window does not cause, and `requestAnimationFrame` coalescing is what turns a drag-resize
into one measurement per frame (FR-023).

All three are baseline in every browser django-mvp targets, and none needs a polyfill or a
dependency.

## The Charts section of the demo sidebar arrives with the first page

`demo/menus.py` keeps `CHART_PAGES` empty and the `MenuCollapse` conditional on it, because
django-mvp draws a childless navigation node as an inert button rather than a section heading. The
first demo page this feature adds populates that list, so the section appears correctly with no
change to the mechanism.
