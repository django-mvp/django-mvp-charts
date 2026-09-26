# Implementation Plan: Charts a reader can follow without telling colours apart

**Branch**: `003-patterns-beside-colour` | **Date**: 2026-09-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-patterns-beside-colour/spec.md`

## Summary

Documentation, one demo chart and tests. The package's own code does not change (FR-005).

The README gains a section on ECharts' decal patterns: what they are, the Python that turns them on
where a chart is built with ECharts' generated description off, which marks carry them, what the
colour-independent cue is where they don't, and how their colour is set. The demo's Options page
gains a two-series bar chart built that way, shown beside the function that built it. `CONTEXT.md`
defines **decal pattern** and **generated description**. Every statement the README makes about
which marks carry a pattern is asserted in chromium against what ECharts drew.

## Technical context

**Language/Version**: Python 3.12+. No JavaScript is written.

**Primary dependencies**: pyecharts 2.1.0 (already a dependency), ECharts 6.1.0 from the CDN in
the demo. No new dependency.

**Storage**: none.

**Testing**: pytest + pytest-django for rendered output; Playwright/chromium for what ECharts drew
(ADR 0002). The `chromium` fixture already decides what a missing browser means.

**Target platform**: any Django project installing the package; the demo project on port 8019.

**Project type**: reusable Django package with a demo project in the same repository.

**Constraints**: nothing in `mvp_charts/` changes (FR-005, Articles XIV and XV). Assertions are
made against rendered output and drawn elements, never class names (Article XV).

**Scale/scope**: two stories, eight tasks.

## Technical approach

### The Python the guidance shows

Patterns are an init option in pyecharts, because pyecharts files `aria` under `InitOpts`. The
documented call passes ECharts' own `aria` object as a plain dictionary:

```python
Bar(
    init_opts=opts.InitOpts(
        aria_opts={"enabled": True, "label": {"enabled": False}, "decal": {"show": True}}
    )
)
```

**Not `opts.AriaDecalOpts`.** Measured on ECharts 6.1.0 (see `research.md` R1): pyecharts'
`AriaDecalOpts` always writes a single `decals` object, and ECharts applies a single object to every
series, so two series get the same pattern and are still told apart by colour alone. Leaving
`decals` out lets ECharts give each series its own pattern from its built-in set, which is the whole
point. The dictionary also reads line for line against ECharts' `aria` documentation, which the
README links for everything it does not cover (spec clarification 4).

`"label": {"enabled": False}` is required, not tidy. ECharts turns the generated description on by
default once `aria.enabled` is true, and the generated description replaces the `aria-label` the
component wrote from `name` (spec clarification 1).

### Where it goes in the README

A new `## Patterns as well as colour` section after `## Placing the chart` and its subsections,
because it leans on `name` and `description` having been explained. The accessibility paragraph in
"Giving the chart a box" that already says a chart is invisible "to anyone who cannot tell its
colours apart" links to it.

The section carries, in this order:

1. What decal patterns are and that pyecharts leaves them off (FR-001). One sentence on when they
   earn their place: series told apart by colour alone. Not for a single series, and not where each
   series is already labelled on the chart (edge cases).
2. The Python, as a fenced `python` block, which is the demo builder's source verbatim (FR-002,
   AS1-3). The name and description on the tag stay the chart's text alternative (FR-003).
3. Why not `AriaDecalOpts`: one sentence, the measured reason.
4. Which marks carry a pattern (FR-007): bars and pie slices; a line only on the area under it,
   which pyecharts draws at zero opacity, so a plain line shows nothing until the area is shaded
   with `areastyle_opts`; scatter points never. The legend's icons follow their series.
5. The cue where there is no pattern (FR-008): a line's `linestyle_opts` type (solid, dashed,
   dotted), and a scatter series' `symbol`. Both set where the chart is built.
6. Colour (FR-009): the default pattern is dark and translucent, which barely shows on a dark fill
   or a dark page. Its colour is set by giving `decal` a `decals` list, one object per series in
   order, each with its own `color`. A single object rather than a list applies to every series,
   which is the `AriaDecalOpts` trap again.
7. The generated description (FR-010): turned on, it replaces the name given on the tag, because the
   chart object asked ECharts to write one; the package does not step in. Recommend leaving it off.
8. A link to ECharts' `aria.decal` documentation for the rest.

The README states nothing about which marks are patterned that is not asserted by a US2 test.

### The demo chart

A builder `orders_by_channel()` in `demo/views.py`: a `Bar` of the four regions with two series,
"Online" and "In store", patterns on per the documented call. Added to `ChartOptionsView` as a
fourth section, "Patterns as well as colour", listing `source_of(orders_by_channel)` beside a
`{% show_code %}{% cotton:verbatim %}` placement carrying `name` and `description`, exactly as the
styled chart's section does. The page already exists and is in the sidebar, so no route or menu
entry changes (FR-004).

### Tests

**Rendered output (`tests/test_demo.py`, a new `TestPatternsBesideColour`)** — the listing is the
builder that ran; the chart's payload carries `aria.enabled` true, `aria.label.enabled` false,
`aria.decal.show` true and no `aria.decal.decals`; the placement carries a `name` and a
`description`. **README ↔ demo** — the README's `python` block containing `aria_opts` is the
builder's body, whitespace-normalised, following `TestDocumentedExample`'s pattern (AS1-3).
**Nothing turned on by default** — a chart built without the option arrives with the `aria` object
pyecharts wrote, `{"enabled": false}`, which pins SC-004 and AS1-5 on rendered output.

**In chromium (`tests/test_components/test_chart_e2e.py`)** — against a probe page on the suite's
own urlconf (`probe/patterns/`, following `RendererProbe`) carrying a chart per mark kind, each built
with the documented call: a two-series bar, a pie, a two-series plain line, the same line with
`areastyle_opts(opacity=0.5)`, a two-series scatter; plus one bar with the generated description
left on. Every assertion reads what ECharts drew — ZRender's display list and the instance's data
visuals — never the options that were sent:

- US1: each bar series' drawn bars carry a pattern; the two series' patterns differ; each legend
  icon carries its series' pattern; the surface's `aria-label` is the tag's `name` and its
  `aria-describedby` still names the description.
- US2: pie slices carry a pattern; a plain line's area element carries one but is drawn at opacity
  0, and the shaded line's area is drawn above 0; scatter symbols carry none; the bar with the
  generated description on has an `aria-label` that is not the tag's `name`.

Each is written to fail if the statement is made false (SC-003): presence and absence are asserted
separately, and the distinctness assertion compares the two series rather than checking that a
pattern exists.

## Constitution Check

| Article | Holds because |
|---|---|
| I Test-first | every task pairs a failing test with the change |
| II/III Simplicity | no code in `mvp_charts/`; one builder, one probe view |
| V Security | no new input surface; the probe reuses the existing urlconf |
| VI Documentation | README section, CHANGELOG entry, CONTEXT terms, same PR |
| VIII i18n | demo copy is demo-only; no package strings added |
| X Test structure | new tests go in existing, declared modules (`test_demo.py`, `test_components/`) |
| XIV Pass-through | the package names, defaults and filters no `aria` key; the chart object carries it |
| XV Rendered output | assertions against payloads and drawn elements, not class names |

No violations. Complexity Tracking: none.

## Project structure

```text
README.md                                   # new section + link from the accessibility paragraph
CHANGELOG.md                                # [Unreleased] entry
CONTEXT.md                                  # decal pattern, generated description
demo/views.py                               # orders_by_channel(); ChartOptionsView context
demo/templates/demo/chart_options.html      # fourth section
tests/urls.py                               # PatternsProbe
tests/templates/probe/patterns.html         # the probe page
tests/test_demo.py                          # rendered-output + README↔demo tests
tests/test_components/test_chart_e2e.py     # browser tests
```

## Risks

- **ECharts internals in the browser tests.** Reading a drawn element's pattern relies on ZRender's
  display list and `getItemGraphicEl`. That is the only place the answer exists (research R1), and
  a later ECharts that changes it fails the tests loudly, which is what the spec asks for
  (decisions.md, "measured, not read").
- **The CDN in the probe page.** The probe loads the same pinned ECharts the demo does, so the
  tests run against the version the README makes claims about.
