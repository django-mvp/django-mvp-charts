# Decisions — 003 Charts a reader can follow without telling colours apart

## One place for a chart's text alternative

ECharts' `aria` option can write its own description of a chart into the drawing surface's
accessible name. That is the job `name` and `description` on `<c-chart>` already do, and when both
are present ECharts' sentence silently replaces the author's name. A feature to reconcile the two was
proposed as #54 and rejected on 2026-09-25: two places to write the same thing is the problem, so the
answer is to keep one. The text alternative is written on the tag, and this feature's guidance turns
the patterns on with the generated description off.

The generated description was also a poor alternative on its own terms. On the demo project it is
English only, and on a category chart it reads each category's position out as though it were a
value ("the data for North is 0, 154").

## Which marks are patterned is measured, not read

ECharts' documentation says what decal patterns are, not which marks of which series carry one. This
feature's statements about that come from reading the elements ECharts drew on the demo project, on
ECharts 6.1.0, and the same reading is what the tests assert, so the guidance fails loudly if a later
ECharts release changes the answer.

## D1 — the guidance passes ECharts' `aria` object as a dictionary, not through `AriaDecalOpts`

pyecharts' `AriaDecalOpts` always writes one `decals` object, and ECharts gives every series that
one pattern, so a chart built with it still tells its series apart by colour alone — measured on
ECharts 6.1.0 in `research.md` R1. Leaving `decals` out lets ECharts give each series its own
pattern. The documented call therefore passes `{"enabled": True, "label": {"enabled": False},
"decal": {"show": True}}` as `InitOpts(aria_opts=...)`, which also reads line for line against
ECharts' own `aria` documentation. The README says why in one sentence, because `AriaDecalOpts` is
the name a pyecharts user will reach for first.

**Revisit if:** a pyecharts release lets `AriaDecalOpts` leave `decals` out, or write a list.

**ADR:** none — a documentation choice about which spelling of an upstream option to show; the package
carries whichever the chart object uses, unchanged.

## D2 — the demo chart goes on the Options page, not a page of its own

The Options page exists to show options set where the chart is built, which is exactly what the
patterns are. A new page would add a route, a view and a menu entry for one chart.

**ADR:** none — demo-content placement local to this feature.

## D3 — the browser tests read drawn elements, not `getOption()`

`getOption()` returns what was sent, which is what the rendered-output tests already assert. The
statements the guidance makes are about what ECharts drew, and the only place that exists is the
instance's data visuals and ZRender's display list. Both are ECharts internals; a release that
changes them fails the tests, which is the loud failure the specification asks for.

**ADR:** none — a testing choice local to this feature, applying ADR 0002.
