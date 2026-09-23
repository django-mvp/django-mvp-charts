# AGENTS.md — Agent Configuration for django-mvp-charts

<!-- Thin index only — bloat here = ignored instructions. Details live in the pointed-to files. -->

django-mvp-charts renders charts as Cotton components. Each charting library gets its own
component namespace and speaks that library's own vocabulary: `<c-echarts.line>` is ECharts and
nothing else. There is no neutral component that renders through a swappable backend, and adding
one is a constitutional change rather than a feature. `CONTEXT.md` defines the terms; use them.

Presentation only. No models, no views, no forms, no URLs, no migrations. Data arrives as an
attribute from a view the host project already has.

No charting library is vendored here or served from this package. Development and the demo project
load ECharts from a CDN; production projects bundle it themselves so they ship only the chart types
they use.

## Stack & commands

- **Stack:** Python 3.12+ / Django 5.2 and 6.0, Poetry-managed, built on django-mvp and Cotton
- **Install:** `poetry install`
- **Test:** `poetry run pytest`
- **Lint:** `poetry run pre-commit run --all-files` (ruff lint + format, mypy, deptry)
- **Type-check:** `poetry run mypy`
- **Build:** `poetry build`
- **Demo project:** `poetry run python manage.py runserver 0.0.0.0:8019`

Lint is the pre-commit run, not a bare `ruff check .`: the hook config excludes `docs/` and
migrations, and a raw invocation reports findings in paths the gate does not cover.

## Component layout

Components live at `mvp_charts/templates/cotton/<backend>/<chart-type>.html`. Cotton maps a tag's
first segment onto that directory, so `<c-echarts.line>` resolves to `cotton/echarts/line.html`.

The directory is named for the **charting library**, not for this package — unlike most packages in
this organisation, which namespace by package name. That is deliberate: the namespace is how a
template author chooses a backend, so it has to read as the library. It also means a second backend
is added by creating a directory next to the first, touching nothing that already works.

The name is load-bearing and fails quietly. A component Cotton cannot resolve renders as empty
output rather than raising, so a renamed directory breaks every tag in the namespace without an
error anywhere. `tests/test_app.py` asserts the directory exists for that reason.

## Demo project

`demo/` is a Django project that runs on django-mvp's application shell. It is how a component is
looked at while it is being written, and it is never deployed. Nothing in it is distributed:
`pyproject.toml` packages `mvp_charts` alone.

`tests/settings.py` inherits `demo/settings.py` rather than restating it, so there is one
description of the shell. Everything in the demo fails quietly — an unresolvable Cotton component
renders as empty output, a Tailwind class the packaged stylesheet does not emit does nothing, and a
menu entry whose URL will not resolve is dropped — which is why `tests/test_demo.py` asserts against
the rendered page.

The sidebar holds the pages that exist: **Overview**, then **Chart region**, then a **Charts**
group once there is a chart type to put in it. The group is a `MenuGroup` — a section heading with
its entries always visible — rather than something that collapses, so a chart type is never a click
away behind a closed control. It is left out of the tree entirely while `CHART_TYPE_PAGES` is empty,
because a navigation node with no children renders as an inert button rather than a heading.

**Adding a page for a new chart type** takes a view, a route, a template and one menu entry:

1. A view in `demo/views.py` on `mvp.views.MVPTemplateView`, setting `page_title` and `breadcrumbs`.
2. A route in `demo/urls.py`.
3. A template extending `page_view.html`, filling `{% block page.content %}`. Wrap each example in
   `{% show_code %}{% cotton:verbatim %}…{% endcotton:verbatim %}{% endshow_code %}` to get the
   component, its source and its rendered HTML together. The `cotton:verbatim` wrapper is required:
   without it Cotton compiles the markup before the tag can capture it.
4. A `MenuItem` in `CHART_TYPE_PAGES` in `demo/menus.py`. The Charts group appears with the first
   entry.

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

Nothing has been released. Two things are needed before the first release: a PyPI trusted publisher
for this project pointed at `publish.yml`, and a `RELEASE_TOKEN` that can write to this repository.

**Tag Release skips a version with no matching CHANGELOG section**, which is what keeps the seed
version from being cut as a release. Leave the scaffold version under `## [Unreleased]` until
Prepare Release promotes it — writing a `## [0.0.1]` heading by hand makes the next push to
`pyproject.toml` tag and release it.

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

CI runs from the shared reusable workflows in `django-mvp/shared`, pinned at `v0.4.1`. Because
they are called rather than inlined, those status checks carry their caller job as a prefix.
The required checks are:

- `call-build / Code Quality`
- `call-build / Security Scan`
- `call-build / Build Package`
- `call-tests / Test Python 3.12, Django 5.2`
- `call-tests / Test Python 3.12, Django 6.0`
- `call-tests / Test Python 3.13, Django 5.2`
- `call-tests / Test Python 3.13, Django 6.0`

`tests.yml` and `build.yml` deliberately carry no `paths:` filter on `pull_request`. A required
check that is filtered out never reports, and a check that never reports blocks the merge.

## Development workflow

Feature work follows a spec-driven process: spec → plan → tasks → implement → review → pull
request, with `specs/NNN-slug/` directories generated per feature. Project standards and the
quality bar live in `CONSTITUTION.md`.

`docs/brainstorm.md` holds the working notes the package was founded on: the prior-art survey, why
there is no interface across charting libraries, and why nothing is vendored. Those are
conclusions, not ratified decisions. Anything that hardens goes to `CONSTITUTION.md` or an ADR.
