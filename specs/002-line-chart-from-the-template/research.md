# Research — a line chart drawn from values written in the template

What was read before planning, and the questions each reading settled.

## What the repository already decided

**FS-001 shipped the region and the two events this feature consumes.** `chart-region.js` publishes
`mvp-chart-region:state` (`waiting` / `ready` / `missing-library` / `no-height`) and
`mvp-chart-region:resize`, and its own source calls them "the contract being designed before there
is a consumer for it". This feature is that consumer, so the drawing module subscribes rather than
re-implementing: no second library poll, no second height check, no second resize observer. A
chart draws when its region says `ready` and resizes when its region says the box changed.

**ADR 0003 makes `window.echarts` the whole delivery contract**, and ADR 0004/0005 make the script
tags the project's to write. Both hold unchanged here, which is why the drawing module is a second
file in the same static directory and a second line in the demo's base template rather than
anything the package emits.

**ADR 0001 — one module, loaded once per page.** `echarts-chart.js` follows the same shape:
guarded against double evaluation, no dependencies, no build step.

**The resolve run behind issue #19** removed the delivery component and made the project name its
own regions. Nothing in this feature re-introduces either.

## The sketch branch

`sketch/chart-component-api` designed the component surface for four chart types and went through
two rounds with the repository owner before the specification was written. It is prior art the
specification already absorbed, and its settled parts are carried over here:

- **Data arrives as a Python value, written with a colon.** Round 1 also parsed `values="12,14,15"`
  by splitting on commas; that was removed on the owner's instruction, and the specification
  records the same rule as FR-002a. Splitting on a separator means inventing a data format —
  deciding what a comma inside a label means, what an empty item is, which strings look enough like
  numbers to become them — and every one of those decisions is wrong at some edge.
- **Every attribute is declared with an empty default in `<c-vars>`.** Cotton cannot tell an absent
  attribute from one written empty, so a default written in the template would silently beat
  anything else. Defaults live in Python.
- **Raw options merge last and beat everything**, and `series` is the one list merged entry by
  entry rather than replaced. This was found by building it: adding an area fill through raw
  options replaced the whole series list and wiped the data, because a series is identified by its
  position and the component built the one at that position.
- **`json_script` carries the options to the page.** It is Django's own answer, it escapes the
  sequences that can end a script element early, and it keeps a long series out of an HTML
  attribute.

What the sketch did that this feature does **not** do:

- It wrote appearance into every chart — a legend rule, bar widths, a line width, marker sizes and
  a marker threshold, solid gridlines, a dropped axis line, an animation setting. Issue #17 raised
  that as an open question and the specification answers it: the package contributes no appearance
  decision at all (FR-013). None of it is carried over.
- It built four chart types, a `series` attribute for several named runs, and a `config` object
  assembled in a view. All three are later roadmap items and the specification puts them out of
  scope.
- It generated an id when none was written. FR-006 keeps the id the author's, because a generated
  one is stable only until a chart is added above it.

## ECharts behaviour the plan relies on

**A category axis with no `data` derives its categories from the series' own indices.** This is
what makes FR-003 — values with no point labels still draw, in the order given — a matter of
omitting a key rather than of the package numbering the points itself. Numbering them would be the
package inventing data.

**An options object is additive and unfiltered.** `setOption` accepts keys this package has never
heard of, which is the whole mechanism behind FR-012 and SC-005: pass-through needs no list of
known options and therefore cannot fall behind ECharts' own releases.

**`echarts.init` measures the element it is given at init time and does not watch it.** Resizing is
the caller's job, which is why the region's resize event is a contract rather than a convenience.

## What "no appearance from this package" can be tested against

FR-014 says a chart drawn through this package asks ECharts for the same thing that drawing the
same data directly would. That is assertable two ways, and both are cheap:

1. **From rendered output** — the options object in the page is compared, whole, against the
   literal dictionary a person would write by hand. A whole-object comparison is what catches a key
   nobody meant to add; asserting the absence of a list of known appearance keys would only catch
   the ones somebody thought to list.
2. **In a browser** — the series data and category values are read back out of the live ECharts
   instance, so the claim rests on what the library received rather than on what the page contains.

Neither rests on looking at the drawn chart.

## Rejected alternatives

**Letting the drawing module find its options by id convention** (`region.id + "-options"`). Fewer
characters in the page, but the coupling is invisible from either end and a region with a
surprising id fails silently. The script carries `data-mvp-echarts-options-for` pointing at its
region instead: one query finds every chart on the page, and the relationship is readable in the
rendered output.

**Adding the options reference to `region.html`.** It would make the region — the one component
that deliberately knows nothing about chart types — carry a chart type's wiring, and every future
backend would have to agree on the attribute name.

**Mirroring ECharts options as named attributes.** Article XIV forbids it, and the specification
names only the attributes carrying data. Axes, legends and tooltips are R5, and they are reachable
through `options` today.
