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
  how big it is. `name` and `description` are required and carry the
  accessible name and the text alternative; leaving either out replaces the
  region with a message naming what is missing, rather than rendering with an
  empty value.
- Per-request numbering for regions without an author-supplied `id`, so
  several regions on one page stay separately identifiable and each one's
  description is tied to the right chart.
- `mvp_charts/locale/`, with a base English catalog. These are the package's
  first user-facing strings.
- A demo page showing a region in a sized wrapper, four more at four different
  heights, and the markup that produced them.
- `<c-echarts.cdn>`, the development delivery: one script tag, pinned to an
  exact ECharts version and carrying a subresource integrity hash. A project
  places it in its own base template. No component emits it, so installing
  this package adds no external origin a project did not choose.
- `mvp_charts.versions`, stating the ECharts range the `echarts` namespace is
  known to render against and the exact version the delivery component pins.
  ECharts remains undeclared as a dependency, because this package does not
  ship it.
- A region loads the package's own module once per page, whatever the number
  of regions on it. A page carrying no region requests nothing.
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
- A second demo page showing both failure states on purpose.
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

- `docs/adr/`, with the three architectural decisions this feature settled:
  how browser behaviour is delivered, what counts as evidence for a guarantee
  that only exists in a running page, and the single contract between this
  package and the project that installs it.

### Changed

- The demo project runs on django-mvp's application shell — sidebar, header,
  breadcrumbs, theme switcher — instead of a single hand-written page. Its
  navigation is declared in `demo/menus.py`, and a chart page joins it as one
  entry in `CHART_PAGES`.
- The test settings inherit the demo project's configuration instead of
  restating it, so the suite exercises the project a reader actually opens.
