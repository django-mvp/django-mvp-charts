# Brainstorm

Working notes from the conversation that started this package. Not decisions of record — where
something here hardens into an architectural commitment, it becomes an ADR under `docs/adr/`.

## Prior art

Surveyed before scaffolding, to check the idea was not already solved.

| Package | State | Shape | Overlap |
|---|---|---|---|
| [django-echarts](https://github.com/kinegratii/django-echarts) | Last released March 2023 | A whole-site scaffold built on pyecharts: views, URLs, navigation, chart pages | Same library, entirely different unit of delivery |
| [pyecharts](https://github.com/pyecharts/pyecharts) | Actively maintained | Python option-builder that emits ECharts JSON and its own HTML | Real overlap on option construction, none on Django integration |
| [django-chartjs](https://github.com/peopledoc/django-chartjs) | Last released February 2022 | Ajax view mixins returning Chart.js data | Abandoned, and a view layer rather than a template layer |
| [django-plotly-dash](https://github.com/GibbsConsulting/django-plotly-dash) | Actively maintained | Embeds Dash applications in Django templates | Different problem: interactive apps, not charts |

Nothing Cotton-based exists. Nothing renders charts as components configured by template
attributes. The two healthy packages solve adjacent problems rather than this one.

**pyecharts is the one worth revisiting.** It is alive, it builds ECharts options competently, and
it would save writing an option builder. It is not adopted at the outset for two reasons: it is
ECharts-specific, so leaning on it would put a backend-specific dependency underneath a package
whose whole structure assumes more than one backend; and it emits its own HTML and JavaScript,
which is the layer this package exists to own. If option construction turns out to be the expensive
part, using it privately behind the ECharts namespace stays available.

## Why not one interface across libraries

The obvious design is a neutral `<c-chart.line>` that renders through a configurable backend, so a
project could swap ECharts for Plotly without touching its templates. Rejected before any code was
written.

Charting libraries differ in many small ways rather than a few large ones, and those differences
are usually the reason a library was chosen. A common interface can only expose the intersection,
which is thin. Every real chart then reaches for something outside it, so the interface grows an
escape hatch to native options, and once templates contain native options the portability the
abstraction was built for is already gone. What remains is a translation layer to work around.

The alternative adopted here is explicit choice: each backend gets a namespace, speaks its own
library's vocabulary, and the template author picks one. What the package shares across backends is
the plumbing — container markup and sizing, responsive resize, theme handoff from daisyUI, script
delivery, and serialising Python data into the shape the library wants.

## Delivery of the JavaScript

No charting library is vendored into this package or served from its static files.

Development and the demo project load ECharts from a CDN, which keeps the local loop free of a Node
toolchain. Production projects are expected to bundle it themselves. ECharts is built for this: it
ships ES modules with per-chart-type and per-component entry points, so a project importing only a
line chart and a tooltip pays for a fraction of the full build. Shipping a vendored copy would take
that choice away and hand every project the whole library.

The open question is how a component discovers which of the two is in play, and it is deliberately
left open until the first components exist.

## Dependency on django-mvp

Hard, not optional. Chart colours come from the daisyUI theme django-mvp supplies, and the
components render inside its layout primitives. Without it a chart renders into an unstyled page
against a palette that is not defined. django-cotton is not declared here at all: django-mvp pins
it exactly, and a second constraint could only fight that one.
