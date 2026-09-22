# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

The first component: a chart region. Nothing draws into it yet, and nothing
has been released.

### Added

- `<c-echarts.region>`, the space a chart is drawn into. It fills the element
  around it and has no height of its own, so the project's own wrapper decides
  how big it is. `id`, `name` and `description` are all required: the id ties
  the caption to the right chart, and the other two carry the accessible name
  and the text alternative. Leaving any of them out replaces the region with a
  message naming what is missing, rather than rendering with an empty value.
- `mvp_charts/locale/`, with a base English catalog. These are the package's
  first user-facing strings.
- A demo page showing a region in a sized wrapper, four more at four different
  heights, the markup that produced them, and every state a region can be in
  when it cannot draw.
- `mvp_charts.versions`, stating the ECharts range the `echarts` namespace is
  known to render against. ECharts remains undeclared as a dependency, because
  this package does not ship it, and the range is not enforced anywhere — a
  bundle outside it is untested rather than blocked.
- `mvp_charts/js/chart-region.js`, the module a chart region needs in the
  browser. The project loads it from its own template with a `{% static %}`
  tag, next to whichever line supplies the charting library. A region emits no
  script tag of any kind, so which pages carry the module, where it goes in the
  document and whether it is bundled with the project's other JavaScript stay
  the project's decisions.
- A region that cannot draw says why, in the page, where the chart would have
  been. A missing charting library is reported once waiting for a late bundle
  stops being a reasonable explanation, and names both ways to supply one. A
  wrapper that resolves to no height is reported too, with enough room taken
  for the message to be read. Both messages are translatable and identical in
  development and production.
- The height is judged at a region's first visibility rather than at first
  paint, so a region in a collapsed panel or an unselected tab is measured
  when it is revealed. A region that loses its height afterwards reports
  nothing.
- One region failing leaves every other region on the page working.
- `mvp-chart-region:resize`, dispatched on a region whenever its box changes
  and carrying the measured `{ width, height }`. This is the contract a chart
  type subscribes to in order to redraw, designed before any chart type exists
  so the first one has something to meet rather than a gap to work around.
- A region keeps filling its wrapper through a window resize, a wrapper
  resized on its own, and being revealed after starting hidden.
- `demo/templates/cotton/documentation.html`, the display surface django-mvp's
  `{% show_code %}` tag renders through. The tag ships with django-mvp; the
  template it names does not, so a project calling the tag has to supply one.
  It shows a component live, the Cotton that produced it, and the HTML it
  rendered to.

- `docs/adr/`, with the architectural decisions this feature settled: how
  browser behaviour is delivered, what counts as evidence for a guarantee that
  only exists in a running page, the single contract between this package and
  the project that installs it, and which side of that line the script tags and
  the region's id fall on.
- The README shows the two script tags a project writes for itself — one for
  ECharts, one for this package's module — and what makes the first safe to
  copy. The package ships no charting library, names no origin and renders no
  script tag, so installing it adds nothing a project did not ask for.

### Changed

- The demo project runs on django-mvp's application shell — sidebar, header,
  breadcrumbs, theme switcher — instead of a single hand-written page. Its
  navigation is declared in `demo/menus.py`, and a chart page joins it as one
  entry in `CHART_PAGES`.
- The test settings inherit the demo project's configuration instead of
  restating it, so the suite exercises the project a reader actually opens.
