# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

One component, and the chart it draws is built in Python. Nothing has been released, so nothing
here is a breaking change to anyone — but it replaces everything the package previously offered.

### Added

- `pyecharts` as a dependency, and the API. A chart is a pyecharts object built in the host
  project's own Python, which is where every chart type and every ECharts option already lives.
  The types a Django view produces — dates, times, `Decimal` values and `None` — are serialised by
  pyecharts, so nothing has to be converted first.
- `<c-chart>`, the single component this package ships. It renders the figure a chart is drawn
  into, its accessible name and text alternative, its size, and the chart's own options as JSON.
  It names six attributes: `:chart`, `id`, `height`, `aspect-ratio`, `name` and `description`. It
  names nothing about the chart.
- `aspect-ratio` on `<c-chart>`, a third way to give a chart a box: the figure takes the width the
  page gives it and works the height out from the ratio. Written as a number, `2`, or as the
  fraction it comes from, `16/9`. A chart then holds its shape at every window width, and a chart
  in a column with no height of its own still has one, without an outer element existing only to
  supply it. `height` wins when both are given.
- A spinner in the middle of every figure until the chart is drawn into it. There is no attribute
  for it and nothing to opt into: every chart waits for the browser, so every figure says so. The
  browser module takes it out once the chart is on the surface, and leaves it where a chart never
  draws, because a figure that empties itself and stays empty tells a reader less than one that
  never stopped waiting. It carries no words, so the package still ships no message catalogue.
- A console warning for a figure that has a width and no height — the one way a chart fails
  silently, with correct options, a started ECharts instance, nothing thrown and a blank space
  where the reader expected a chart. Said once per chart and naming the figure. A chart in a
  closed panel or an unselected tab measures nothing on either axis, so it is not reported, and it
  draws itself when the panel opens.
- `{% chart_options %}`, which escapes the three character sequences that can end a `<script>`
  element early. pyecharts escapes none of them, so a label read out of a database and carrying
  `</script>` would otherwise close the element it sits in. Asserted against three hostile labels.
- `mvp_charts/js/mvp-charts.js`, the one module a page needs. It finds every chart, hands its
  options to ECharts, and redraws each one when its box changes. The project loads it from its own
  template with a `{% static %}` tag, so which pages carry it and where it goes in the document
  stay the project's decisions.
- A demo project on the application shell showing line, bar, pie and scatter charts, the whole
  option surface reached in Python, and the awkward types drawn rather than described. The view
  code that built each chart is on the page beside it.
- `docs/adr/0006`, recording why an attribute vocabulary over ECharts' options was replaced by a
  chart object, and what that costs.

### Removed

- `<c-echarts.region>` and `<c-echarts.line>`, and the `echarts` namespace they sat in. There is
  one component now, and a chart type is the class the view instantiated.
- `:values`, `:labels` and `:options`, with the options builder and deep merge behind them. Every
  option is set on the chart object.
- The on-page failure messages for a missing charting library, a wrapper that resolved to no
  height, and a missing id — with the library poll, the load-grace window, the
  `IntersectionObserver`, the translated message catalogue and the custom-event contract between
  the two browser modules that supported them. What a project shows its readers when something is
  broken is the project's decision. Everything the package has to say now goes to the browser
  console instead.
- `mvp-chart-region:resize` and `mvp-chart-region:state`. The module that draws a chart is the
  module that watches its box, so there is no longer a contract between two of them.
- `mvp_charts/locale/`. The package has no user-facing strings left to translate.
- `docs/options.md`, which described an options builder that no longer exists.

### Changed

- A chart's appearance is pyecharts' rather than ECharts' bare defaults. Point labels, the legend,
  the tooltip and the animation are on because pyecharts turns them on. This package still writes
  no appearance of its own, and the README says whose the defaults are.
- `CONSTITUTION.md` Articles XII to XV, `CONTEXT.md`, `GOALS.md` and the roadmap, all rewritten
  against the one-component design.
- django-mvp 0.24.0 is the minimum, up from 0.23.0. It ships the display surface that
  `{% show_code %}` renders through, which this project had been supplying itself for want of one
  upstream. The demo's copy is gone, so its examples now use the packaged surface.

### Not supported

- pyecharts' `JsCode`. `dump_options()` emits such a function unquoted, which is not JSON and could
  only be delivered by evaluating server-rendered code in the page. The quoted variant is valid
  JSON, but the function arrives as a string and ECharts ignores it without a word. A formatter
  that silently does nothing is worse than one that was never offered, so neither route is taken.
  Write it against the chart instance in your own JavaScript.
