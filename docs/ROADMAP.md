# Roadmap — django-mvp-charts

**Date:** 2026-09-23

This document was designed against [GOALS.md](../GOALS.md). See also [CONTEXT.md](../CONTEXT.md)
for domain terminology and [CONSTITUTION.md](../CONSTITUTION.md) for project standards.

## Versioning

Releases are gated on goal importance, not on a count of features.

| Version | Gate |
|---|---|
| `0.0.x` | Building toward the Essential goals. Pre-viable, expect churn, nothing published |
| `0.1.0` | All Essential goals delivered. The minimum usable release, and the first publish |
| `0.1.x` → `0.x` | Advancing the Expected goals, at whatever granularity the work takes |
| `1.0.0` | All Expected goals delivered. The complete, dependable release |
| `1.x` | Stable line: fixes and additive features only |
| `2.0` | The next major, where breaking changes go |

A goal is not one minor: some take several releases, and one release can move two. Once `1.0`
ships, a breaking change never goes out as `1.x` — it waits for the next major.


## Essential goals: v0.1.0

Everything needed to reach a minimum usable release.

### R1 — A chart built in Python is placed with one tag

*delivered in [#4](https://github.com/django-mvp/django-mvp-charts/issues/4) · advances G1, G2*

Delivered. A view builds a pyecharts chart, puts it in the context, and `<c-chart>` places it. The
component renders the figure, its accessible name and text alternative, its sizing, and the options
payload. `mvp-charts.js` hands that payload to ECharts and keeps each chart at the size of its box.

Because the chart is a pyecharts object, every chart type and every ECharts option arrives with it.
There is no attribute vocabulary to extend and no chart type to add: what pyecharts can build, this
places.

**Deliverables:**

- One component, placing any pyecharts chart
- Several charts on one page, independent of each other
- The library available in development without a build step, and taken from the host project's
  bundle when it has one
- A diagnosable failure in the console when the library is missing

### R2 — Documentation a reader can follow from an empty project

*delivered in [#20](https://github.com/django-mvp/django-mvp-charts/issues/20), [#21](https://github.com/django-mvp/django-mvp-charts/issues/21) · advances G1*

The API is small enough to state completely, which makes the documentation's job the part that is
not obvious: where a chart is built, what pyecharts is for, what this package does and does not
decide, and what happens to the awkward types. The README and the demo project are the two halves,
and they are checked against each other so an example cannot quietly stop being true.

**Deliverables:**

- A README that is followable start to finish by someone who has not seen pyecharts
- A demo project rendering the chart types an application dashboard shows, with the view code that
  built each one visible beside it
- The README's placement example asserted to be the markup the demo actually renders

## Expected goals: v1.0.0

The breadth that makes the package dependable rather than merely usable.

### R3 — The awkward types, proven rather than assumed

*feature · advances G3*

pyecharts serialises dates, times, decimals and missing values, and the demo shows it doing so. What
is not yet covered is the rest of what a Django view produces: querysets, `timezone`-aware
datetimes, `timedelta`, and the numeric types numpy and pandas introduce when a project reaches for
them. Each either works, or has a documented shape to convert to first.

Serves G3.

### R4 — A chart that is genuinely usable without seeing it

*feature · advances G4*

`name` and `description` are carried today, and that is the floor rather than the finish. What is
open is whether a canvas chart can offer more than a text alternative — ECharts' own `aria` support
emits a generated description and decal patterns for colour-blind readers, and both are off by
default in pyecharts. Whether to document them, recommend them, or leave them alone is the question
this item answers.

Serves G4.

### R5 — The ECharts 7 question

*feature · advances G2*

pyecharts follows ECharts by roughly a year: 2.1.0, the first release targeting ECharts 6, landed in
February 2026. When ECharts 7 arrives, this package has to decide what it claims and what it tells a
project that has bundled a version pyecharts does not yet build for. The answer is documentation and
a version range, not code, but it needs deciding before it is urgent.

Serves G2.
