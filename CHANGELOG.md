# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Initial scaffold: build pipeline, test harness and demo project. No components
yet, and nothing released.

### Added

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
