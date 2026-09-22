# Roadmap — django-mvp-charts

**Date:** 2026-09-21

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

Aspirational goals may be developed against v2 or v1 as required.

## Essential goals: v0.1.0

Everything needed to reach a minimum usable release.

### R1 — A chart occupies a region of the page, and the library reaches the browser

*feature · advances G1*

Before any chart type exists, a page needs somewhere to put one and a way to get hold of the
charting library. This item covers both, because neither is useful alone and the choices interact.
A chart holds a sized region that survives a window resize and a container that changes shape.
Several charts coexist on one page without interfering. The library is available in development
without a build step and comes from the host project's own bundle in production, with a clear,
early failure when it is absent rather than a blank rectangle.

This is the plumbing every later item stands on, which is why it comes first.

**Deliverables:**

- A chart region that is sized by the template author and holds its shape as the page changes
- Several charts on one page, independent of each other
- The library available in development without a build step
- The library taken from the host project's bundle when it has one
- A visible, diagnosable failure when the library is missing

Serves G1. Out of scope: any chart type, and any option a specific chart type understands.

### R2 — Python values become chart data without hand-serialising

*feature · advances G1*

The point at which a template author currently gives up and writes JavaScript is the data. This
item makes a Python value usable as a chart attribute directly, in the shapes a Django view
actually produces, with the awkward types handled rather than crashing at render or arriving as
the string `None`.

It comes second because every chart type needs it, and building it once against a real chart is
what stops it being designed in the abstract.

**Deliverables:**

- Values passed straight from a view to a component attribute
- The shapes a Django view produces in practice, including several named series
- Dates, times, decimals and missing values arriving as something the chart can draw
- Values escaped correctly, with a test that proves content cannot break out of the page

Serves G1. Out of scope: querying, aggregating or reshaping data, which stays the project's job.

### R3 — Four basic chart types: line, bar, pie and scatter

*multi-feature · advances G1, G2, G4*

The four shapes that cover most of what an application dashboard shows, and the item that proves
the whole idea end to end: a template author writes one tag with attributes and gets a working
chart with no JavaScript anywhere on the page.

They are one item rather than four because the attribute vocabulary is the real deliverable. Built
separately they would drift into four dialects; built together, the same words mean the same thing
whichever chart carries them, and the shared plumbing is forced out into the open by the second
type rather than discovered at the fourth. Scatter earns its place here despite being the least
reached-for, because its data is pairs rather than a series against categories, and a vocabulary
that has never met that shape will not survive meeting it later.

This item is also where the escape hatch gets settled, because the rule for a named attribute and
a passed-through option disagreeing can only be written honestly with several chart types to test
it against.

**Deliverables:**

- Line, bar, pie and scatter charts, each declared with attributes alone
- One series and several, on every type that admits the distinction
- One attribute vocabulary across the four, rather than four parallel ones
- An accessible name and a text alternative available on every type, so a chart can be made
  usable without seeing it
- Options the components do not name, reachable from the template, with a stated and tested rule
  for what happens when a named attribute and a passed option disagree
- The demo project rendering all four, and documentation showing the tags that produced them

Serves G1, G2 and G4. Out of scope: area fills, stacking and other variants, which arrive once
enough types exist to show which of them are genuinely shared; and colour, which the charting
library decides unless the page says otherwise.

## Expected goals: v1.0.0

The breadth that makes the package dependable rather than merely usable.

### R4 — Area, stacked and combined variants

*feature · advances G2*

The variants deferred from the basic types, once there are enough chart types to see which of them
are genuinely shared rather than particular to one shape. Serves G2.

### R5 — Axes, legend and tooltip as named attributes

*feature · advances G1, G2*

The configuration every chart type shares, promoted out of the escape hatch and named once, so it
reads the same whichever chart it is on. Serves G1 and G2.

### R6 — Values read the way people write them

*feature · advances G2*

Currency, percentages, thousands separators and dates on an axis, so a chart does not need
post-processing to be readable. Serves G2.

## Aspirational goals: v2.0

The payoff of the namespace design, if and when a second library is wanted.

### R7 — A second charting library

*multi-feature · advances G3*

A second library alongside ECharts, in its own namespace and speaking its own vocabulary. The work
is as much about what turns out to be genuinely shared as about the new components, and it is the
only thing that proves the namespace structure was worth having. Serves G3.
