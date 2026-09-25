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
