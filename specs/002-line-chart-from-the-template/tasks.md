# Tasks — a line chart, drawn from values written in the template

Three stories, run in priority order. Each is independently testable and leaves the suite green.
Documentation ships in the story that introduces the public name it describes.

Test-first throughout (Article I): the assertions in each task are written and failing before the
code that satisfies them.

## US1 — Draw a line chart from values written in the template (P1)

Delivers FR-001 … FR-007, SC-001, SC-002, SC-006.

- **T001** — `tests/test_components/test_line.py`: the rendered-output contract for a line chart
  given an id, values and labels. Assert the options object carried in the page is exactly
  `{"xAxis": {"type": "category", "data": [...]}, "yAxis": {"type": "value"}, "series": [{"type":
  "line", "data": [...]}]}` for the values and labels written, in the order written; that the
  template output contains no `<script>` the author wrote; that values without labels drop
  `xAxis.data` and keep the values in order; and that a value list containing `None`, a float and a
  zero survives unchanged. Compile the Cotton source directly, as `test_region.py` does.
- **T002** — `mvp_charts/echarts/__init__.py` and `mvp_charts/echarts/options.py`: `Attribute`,
  reading one attribute's Python value and refusing a string with a message naming the fix
  (FR-002a); `Line`, building the options object above and nothing else. No grid, tooltip, legend,
  animation, colour, line width, symbol, axis tick or split line (FR-013). `Line` takes labels and
  values, drops `xAxis.data` when there are no labels, and never reorders, drops, combines, rounds,
  caps or fills in a value (FR-004).
- **T003** — `mvp_charts/templatetags/mvp_charts.py`: `{% echarts_chart %}`, which builds the chart
  from the attributes and returns an object carrying the id, the options-script id and the
  `json_script` payload. One tag, registered on the package's own library.
- **T004** — `mvp_charts/templates/cotton/echarts/line.html`: the component. Declares every
  attribute with an empty default, calls the tag, renders `<c-echarts.region>` with the id, name
  and description, and the options script beside it carrying
  `data-mvp-echarts-options-for="{{ id }}"`. A missing id renders the region's existing missing-id
  message and no options script (FR-006). Annotated to the gallery standard, as `region.html` is.
- **T005** — `mvp_charts/static/mvp_charts/js/echarts-chart.js`: find every
  `[data-mvp-echarts-options-for]`, wait for its region to reach `ready` on
  `mvp-chart-region:state`, `echarts.init` the drawing surface, `setOption` the parsed options, and
  `resize` on `mvp-chart-region:resize`. No library poll, no height check, no resize observer of
  its own — the region owns all three. Guarded against double evaluation, no dependencies, safe on
  a page with no charts.
- **T006** — the demo project: `demo/views.py`, `demo/urls.py`, `demo/menus.py` (the first entry in
  `CHART_TYPE_PAGES`, which brings the Charts group into the sidebar), `demo/templates/demo/line.html`
  showing a line chart inside the wrapper that sizes it, and `demo/templates/base.html` loading
  `echarts-chart.js`. The page follows `chart_region.html` exactly: a `c-section` per example, each
  inside `{% show_code %}{% cotton:verbatim %}`. Update `tests/test_demo.py`, which names the pages
  the sidebar holds (FR-007, SC-006).
- **T007** — `tests/test_components/test_line_e2e.py`: in a real browser, a line is drawn; the
  series data and the category values are read back out of the live ECharts instance and match what
  the template wrote, in order; a chart and a bare region on one page both work and neither reads
  the other's state (US1 scenario 4); and the chart's canvas still matches its wrapper after a
  viewport change (US1 scenario 5, FR-005).
- **T008** — README: the line-chart section, showing the complete markup including the wrapper that
  sizes it, and the install section's second script line. State plainly that an attribute carrying
  data takes a Python value written with a colon, and show one (FR-002a, FR-007). CHANGELOG entry.

## US2 — A chart with nothing around it (P2)

Delivers FR-008 … FR-011, SC-003.

- **T009** — `tests/test_components/test_region.py` and `test_line.py`: a region and a line chart
  given an id and nothing else render, with no message about a missing name or description anywhere
  in the output; the drawing surface carries no `role="img"` and no `aria-label` when there is no
  name, and no `figcaption` when there is no description; both are carried exactly as before when
  given; an empty string is treated as not given; a missing id is still reported. The two
  assertions in `test_region.py` that state the superseded behaviour are replaced, and the
  replacement names FR-010.
- **T010** — `mvp_charts/templates/cotton/echarts/region.html`: render without a name and without a
  description. The missing-id branch stays; the missing-name and missing-description branches go.
  Update the component's own annotation block, which currently states the superseded rule.
- **T011** — the demo's line page gains the smallest working chart — one tag, an id and values —
  beside the fully-described one. README: the paragraph stating what a chart with no name and no
  text alternative costs the people reading the page, so omitting them is a decision rather than an
  accident (FR-011). CHANGELOG entry for the behaviour change (Article XVI).

## US3 — The chart is ECharts', not the package's (P3)

Delivers FR-012 … FR-016, SC-004, SC-005.

- **T012** — `tests/test_components/test_line.py`: an `options` attribute deep-merges over the
  built object and wins on every key it names; a mapping merges recursively; a list replaces a
  list; `series` merges entry by entry against position, so an option added to the series keeps the
  data; a key this package has never heard of arrives unchanged; and the object built for a chart
  given values alone is byte-for-byte the dictionary a person writing ECharts by hand would pass.
  A browser assertion in `test_line_e2e.py` reads an author-supplied colour back off the live
  instance.
- **T013** — `mvp_charts/echarts/options.py`: the merge. Deep for mappings, replacing for lists,
  entry by entry for `series`, no key filtering anywhere. README: the styling section saying
  appearance belongs to the page, showing how to reach ECharts' own options from the template, and
  showing a colour being set by the author rather than derived from the theme (FR-016). CHANGELOG
  entry.

## Exit

Full suite green, `pre-commit run --all-files` green, the demo's line page drawing in a browser,
and the README's examples run as written against this branch.
