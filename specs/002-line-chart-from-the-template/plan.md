# Implementation Plan: A line chart, drawn from values written in the template

**Branch**: `002-line-chart-from-the-template` | **Date**: 2026-09-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-line-chart-from-the-template/spec.md`

## Summary

The first chart type. `<c-echarts.line>` takes an id, a list of values and a list of point labels
written on the tag as Python values, renders a chart region and an ECharts options object beside
it, and a browser module draws the one into the other. The options object holds an axis pair and a
series and nothing else, so what appears is what ECharts draws for that data. Anything the
component does not name is written on the tag as `options` and deep-merged over the built object on
its way to the browser.

Two behaviours that exist today change. A region renders without an accessible name and without a
text alternative, where it used to report their absence in place of the chart (FR-010), and an id
stays the one thing it still refuses without. Neither the line component nor the region acquires a
default height, a colour, or any other appearance decision.

## Technical context

**Language/Version**: Python 3.12+, browser JavaScript written to the same no-build, no-dependency
rule as `chart-region.js` (ES5-compatible, safe to evaluate twice).

**Primary dependencies**: Django 5.2 / 6.0, django-cotton, django-mvp. Apache ECharts 6.x, which
this package never ships and reaches only through `window.echarts` (Article XII, ADR 0003).

**Storage**: none. Data arrives as a template attribute.

**Testing**: pytest + pytest-django for rendered output; Playwright/chromium for the three
guarantees that only exist in a browser (ADR 0002). The `chromium` fixture already decides what a
missing browser means.

**Target platform**: any Django project installing the package; the demo project on port 8019.

**Project type**: reusable Django package with a demo project in the same repository.

**Constraints**: the package emits no script tag (Article XII, ADR 0004/0005); the project loads
both modules from its own base template. Assertions are made against rendered output, never
against class names (Article XV). Coverage floors: project 90%, patch 85%.

**Scale/scope**: one chart type, one series, one namespace. Three user stories, thirteen tasks.

## Technical approach

### The component surface

`<c-echarts.line>` names five attributes and nothing else:

| Attribute | Required | Carries |
|---|---|---|
| `id` | yes | the element id, the author's to give; the package generates none (FR-006) |
| `:values` | no | one run of numbers, as a Python value (FR-002) |
| `:labels` | no | what the points are called, as a Python value (FR-002) |
| `name` | no | accessible name (FR-008, FR-009) |
| `description` | no | text alternative (FR-008, FR-009) |
| `:options` | no | raw ECharts options, merged over everything built (FR-012) |

`values`, `labels` and `options` carry Python values. The package never reads data out of text
(FR-002a): no splitting on a separator, no guessing at numbers, no rule about what an empty item
means. It does not report the mistake either. A string written where a list belongs is carried
into the options object exactly as any other unexpected value is, and the chart does not draw —
which is how the author finds out. That is the ruling recorded in the specification's
clarifications and in `decisions.md`: the two failures the previous feature reports are conditions
a correct template can still meet, and a misspelt attribute is not one of them. The guidance on
writing an attribute with a colon lives in the README.

An attribute written empty is treated as not given (FR-009), which is also why the component
declares every attribute with an empty default in `<c-vars>` and keeps its real defaults in Python.

### What the component asks ECharts for

The whole built options object, for a chart with labels:

```python
{
    "xAxis": {"type": "category", "data": ["Jan", "Feb", "Mar"]},
    "yAxis": {"type": "value"},
    "series": [{"type": "line", "data": [12, 14, 15]}],
}
```

Without labels, `xAxis` loses its `data` key and ECharts derives the categories from the series'
own indices, which is what writing that chart by hand looks like. There is no `grid`, no
`tooltip`, no `legend`, no `animation`, no `lineStyle`, no `symbolSize`, no `axisTick`, no
`splitLine` and no colour, because every one of those is an appearance decision and FR-013 says
the package makes none. That is also what makes FR-014 testable: the object above is what someone
writing ECharts directly would pass, key for key.

`name` and `description` do not enter the options object at all. They are the region's, and the
region already carries them as an accessible name on the drawing surface and a text alternative in
a `figcaption`.

### Pass-through

`options` is deep-merged over the built object, last, so it beats anything the component wrote
(FR-012, SC-005). Mappings merge recursively; a list replaces a list, because an author has to be
able to take a list back. `series` is the one exception and is merged entry by entry against
position, so adding an area fill to the series does not replace the data with an area fill and
nothing else. Unknown keys are carried through untouched — the component never checks a key
against a list of ones it knows, which is what makes an option added to ECharts after this release
reachable today.

### Getting the options to the browser, and drawing

The component renders the region and, beside it, the options object through Django's
`json_script`, which escapes the character sequences that can end a script element early and keeps
a long series out of an HTML attribute.

```html
<c-echarts.region id="revenue" name="…" description="…" />
<script id="revenue-options" type="application/json"
        data-mvp-echarts-options-for="revenue">{…}</script>
```

The script points at the region rather than the region at the script. That keeps `region.html` —
FS-001's component, and the one thing on this page that knows nothing about chart types —
unchanged, and it leaves the drawing module a single query to find its work.

A new browser module, `mvp_charts/static/mvp_charts/js/echarts-chart.js`, is that module. It is the
consumer the region's two events were designed for and were shipped without: it waits for a region
to report `ready` on `mvp-chart-region:state`, calls `echarts.init` on the drawing surface, hands
over the parsed options, and calls `resize` on `mvp-chart-region:resize`. It adds no polling, no
library check and no height check of its own — the region already owns all three, and a second
copy of that logic is a second thing to keep in step.

Like `chart-region.js`, the project loads it from its own base template. That is Article XII and
ADR 0004/0005, and it is why the demo's `base.html` and the README's install section both grow one
line.

### What changes in FS-001's work

`region.html` renders without a name and without a description (FR-010). When neither is given the
drawing surface carries no `role="img"` and no `aria-label` — an image role with no accessible name
is worse than no role — and no `figcaption` is emitted. A missing id is still reported exactly as
it is today. `tests/test_components/test_region.py` is updated where it asserts the superseded
behaviour, and the new assertions state what replaced it.

## Constitution check

| Article | How this plan satisfies it |
|---|---|
| I — Test-First | Every task writes its assertions before the code it is about; the story's acceptance scenarios are the test names. |
| II — Simplicity | One module per job: an options builder, one template tag, one component, one browser module. No registry, no base class hierarchy for a single chart type. |
| III — Anti-Abstraction | One class, no base class, no registry, no backend interface (Article XIII forbids one). `Line` is a class under Article XI rather than Article III: reading this chart's attributes, building its options and merging the author's over them share one subject. |
| IV — Integration-First | The demo project's line page is a task in US1, not a finishing touch, and the browser tests run against it. |
| V — Security | The options object reaches the page through `json_script`, which is Django's own answer to closing a script element early. Nothing is rendered unescaped into markup. |
| VI — Documentation | README grows the line-chart section in US1, the paragraph on what omitting a name costs in US2, and the styling section in US3. Each ships in the story that introduces its public name. |
| VII — Dependency discipline | No new dependency of any kind. |
| VIII — Internationalization | Every new string the package renders goes through `trans`; there is exactly one, and it is the existing missing-id message reused. |
| X — Test structure | Every new Python module gets the test module that mirrors its path: `tests/test_echarts/test_options.py` and `tests/test_templatetags/test_mvp_charts.py`. `tests/test_components/` stays a declared non-mirror path, because its subject is still the Cotton templates; the rendered-output and browser tests sit on top of the mirrored unit tests rather than instead of them. |
| XI — Cohesion | Reading one attribute's Python value is a classmethod on `Attribute`; building one chart's options is `Line`. Nothing is a loose function operating on someone else's data. |
| XII — Nothing vendored | ECharts is reached through `window.echarts`. The package's own module ships in its static files, as `chart-region.js` already does, and the project writes both script tags. |
| XIII — One namespace per backend | Everything lands under `mvp_charts/echarts/` and `templates/cotton/echarts/`. |
| XIV — Pass through | `options` is the escape hatch, merged last and unfiltered. The five named attributes are the ones carrying data, plus the two the region needs. |
| XV — Rendered output is a contract | Every assertion reads rendered output or a value read back out of a live ECharts instance. Appearance belongs to the page, which is this feature's central claim. |
| XVI — Compatibility | `region.html` changes behaviour, which is a CHANGELOG entry under a pre-1.0 minor. Recorded in US2. |

No violations to track.

## Project structure

### Documentation (this feature)

```text
specs/002-line-chart-from-the-template/
├── spec.md              # on main, unchanged by this branch
├── decisions.md         # on main, appended to
├── plan.md              # this file
├── research.md
├── tasks.md
├── progress.md
└── feature-state.json
```

### Source code

```text
mvp_charts/
├── echarts/
│   ├── __init__.py          # new
│   └── options.py           # new — Attribute, Line
├── templatetags/
│   ├── __init__.py          # new
│   └── mvp_charts.py        # new — {% echarts_chart %}
├── templates/cotton/echarts/
│   ├── region.html          # changed — name and description optional
│   └── line.html            # new
└── static/mvp_charts/js/
    ├── chart-region.js      # unchanged
    └── echarts-chart.js     # new

demo/
├── templates/demo/line.html # new
├── templates/base.html      # changed — loads the drawing module
├── menus.py                 # changed — the first chart type page
├── urls.py                  # changed
└── views.py                 # changed

tests/
├── test_echarts/
│   ├── __init__.py          # new
│   └── test_options.py      # new — mirrors mvp_charts/echarts/options.py
├── test_templatetags/
│   ├── __init__.py          # new
│   └── test_mvp_charts.py   # new — mirrors mvp_charts/templatetags/mvp_charts.py
├── test_components/
│   ├── test_line.py         # new — rendered output
│   ├── test_line_e2e.py     # new — measured in a browser
│   └── test_region.py       # changed — FR-010 supersedes two assertions
└── test_demo.py             # changed — the sidebar gains a page
```

**Structure decision**: the package already separates the backend namespace (`cotton/echarts/`)
from the shared browser plumbing (`static/mvp_charts/js/`), and this feature keeps that line. The
Python for a backend goes in a package named after it, so a second backend is a sibling directory
rather than a parameter. This feature is the first to add Python modules under `mvp_charts/`, so it
is also the first that has anything to mirror in `tests/` — the two new test packages exist for
that reason and `pyproject.toml`'s non-mirror declaration is left alone, since what it exempts is
still only the template tests.

## Complexity tracking

Nothing to justify. No new dependency, no new layer, and the one class exists because the roadmap's
next item adds three more chart types to it.
