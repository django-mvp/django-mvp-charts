# AGENTS.md — Agent Configuration for django-mvp-charts

<!-- Thin index only — bloat here = ignored instructions. Details live in the pointed-to files. -->

django-mvp-charts places charts built in Python on django-mvp pages. A view builds the chart with
pyecharts; one Cotton component, `<c-chart>`, places it and carries its options to the browser as
JSON. `CONTEXT.md` defines the terms; use them.

Presentation only. No models, no views, no forms, no URLs, no migrations. Data arrives as an
attribute from a view the host project already has.

No charting library is vendored here or served from this package. The project loads ECharts and
`mvp_charts/js/mvp-charts.js` from its own base template; the demo loads ECharts from a CDN.

## Stack & commands

- **Stack:** Python 3.12+ / Django 5.2, 6.0 and 6.1, uv-managed (hatchling build backend), built on
  django-mvp and Cotton
- **Install:** `uv sync`
- **Test:** `uv run pytest`
- **Lint:** `uv run pre-commit run --all-files` (ruff lint + format, mypy, deptry)
- **Type-check:** `uv run mypy`
- **Build:** `uv build`
- **Demo project:** `uv run python manage.py runserver 0.0.0.0:8019`
- **Bump the version:** `uv version` — never edit `pyproject.toml` alone, because `uv.lock`
  records this package's own version too

Lint is the pre-commit run, not a bare `ruff check .`: the hook config excludes `docs/` and
migrations, and a raw invocation reports findings in paths the gate does not cover.

## Component layout

The package ships one component, `mvp_charts/templates/cotton/chart.html`, which Cotton resolves
as `<c-chart>`. The file name is the tag name. A component Cotton cannot resolve renders as empty
output rather than raising, so a renamed file breaks every chart without an error anywhere, which
is why `tests/test_app.py` asserts where it lives.

## Demo project

`demo/` is a Django project that runs on django-mvp's application shell. It is how a component is
looked at while it is being written, and it is never deployed. Nothing in it is distributed:
`pyproject.toml` packages `mvp_charts` alone.

`tests/settings.py` inherits `demo/settings.py` rather than restating it, so there is one
description of the shell. Everything in the demo fails quietly — an unresolvable Cotton component
renders as empty output, a Tailwind class the packaged stylesheet does not emit does nothing, and a
menu entry whose URL will not resolve is dropped — which is why `tests/test_demo.py` asserts against
the rendered page.

The sidebar holds the pages that exist: **Overview**, **Chart types** and **Options**, declared in
`demo/menus.py`.

**Adding a page** takes a view, a route, a template and one menu entry:

1. A view in `demo/views.py` on `mvp.views.MVPTemplateView`, setting `page_title` and `breadcrumbs`.
2. A route in `demo/urls.py`.
3. A template extending `page_view.html`, filling `{% block page.content %}`. Wrap each example in
   `{% show_code %}{% cotton:verbatim %}…{% endcotton:verbatim %}{% endshow_code %}` to get the
   component, its source and its rendered HTML together. The `cotton:verbatim` wrapper is required:
   without it Cotton compiles the markup before the tag can capture it.
4. A `MenuItem` in `demo/menus.py`.

`{% show_code %}` renders through a template named `cotton/documentation.html`, which django-mvp
ships alongside the tag from 0.24.0 onwards. This project supplied its own while the package had
none and no longer does. Do not add one back: `demo` comes first in `INSTALLED_APPS`, so a copy
here shadows the packaged surface by name, and this demo would go on showing an older one after
every other project had moved.

## Releasing

Releases run through the shared release flow, never by hand and never by pushing a tag.

1. Dispatch **Prepare Release** with a bump level. It opens a pull request carrying the version
   bump and the CHANGELOG section.
2. Merging that pull request is the release decision. **Tag Release** then cuts the tag and the
   GitHub Release from the merge commit.
3. **Publish** uploads to PyPI through trusted publishing. PyPI's trusted publisher is bound to
   the `publish.yml` filename — renaming that file breaks publishing until the PyPI project
   settings are changed to match.

`pyproject.toml` holds the version and is the single source of truth for all three steps.

**Tag Release skips a version with no matching CHANGELOG section.** Leave new entries under
`## [Unreleased]` until Prepare Release promotes them — writing a version heading by hand makes the
next push to `pyproject.toml` tag and release it.

## Agent skills

### Issue tracker

Issues tracked in GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary mapped 1:1 to canonical roles (needs-triage, needs-info, ready-for-agent,
ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — one `CONTEXT.md` at root and `docs/adr/` for architectural decisions.
See `docs/agents/domain.md`.

### CI checks

CI runs from the shared reusable workflows in `django-mvp/shared`, pinned at `v0.6.0`. Because
they are called rather than inlined, those status checks carry their caller job as a prefix.
The required checks are:

- `call-build / Code Quality`
- `call-build / Security Scan`
- `call-build / Build Package`
- `call-tests / Test Python 3.12, Django 5.2`
- `call-tests / Test Python 3.12, Django 6.0`
- `call-tests / Test Python 3.13, Django 5.2`
- `call-tests / Test Python 3.13, Django 6.0`
- `call-tests / Test Python 3.12, Django 6.1`
- `call-tests / Test Python 3.13, Django 6.1`

Automated contributors commit and push under the repository's bot identity, never a personal
token. The default branch requires one approval, so the author and the approver are always distinct.

`tests.yml` and `build.yml` deliberately carry no `paths:` filter on `pull_request`. A required
check that is filtered out never reports, and a check that never reports blocks the merge.

## Development workflow

Feature work follows a spec-driven process: spec → plan → tasks → implement → review → pull
request, with `specs/NNN-slug/` directories generated per feature. Project standards and the
quality bar live in `CONSTITUTION.md`.

`docs/brainstorm.md` holds the working notes the package was founded on: the prior-art survey, why
there is no interface across charting libraries, and why nothing is vendored. Those are
conclusions, not ratified decisions. Anything that hardens goes to `CONSTITUTION.md` or an ADR.
