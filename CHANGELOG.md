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

- `demo/templates/cotton/documentation.html`, the display surface django-mvp's
  `{% show_code %}` tag renders through. The tag ships with django-mvp; the
  template it names does not, so a project calling the tag has to supply one.
  It shows a component live, the Cotton that produced it, and the HTML it
  rendered to.

### Changed

- The demo project runs on django-mvp's application shell — sidebar, header,
  breadcrumbs, theme switcher — instead of a single hand-written page. Its
  navigation is declared in `demo/menus.py`, and a chart page joins it as one
  entry in `CHART_PAGES`.
- The test settings inherit the demo project's configuration instead of
  restating it, so the suite exercises the project a reader actually opens.
