# django-mvp-charts Constitution

## Core articles

### Article I — Testing
Every change follows [`docs/contributing/standards/testing.md`](docs/contributing/standards/testing.md): what gets a test
and what does not, the test-first cycle, test structure and fixtures, and the coverage floors.

### Article II — Simplicity
Start with the simplest design that satisfies the spec. New dependencies, new abstractions,
and new infrastructure each require a stated justification in plan.md Complexity Tracking.
YAGNI over speculation.

### Article III — Anti-Abstraction
No wrapper layers, base classes, or "future-proofing" indirection without a present, concrete
second use. Prefer duplication over the wrong abstraction.

### Article IV — Integration-First
Contracts and integration points are designed and tested before internals are polished.
Acceptance scenarios exercise the system the way users touch it.

### Article V — Security & data-safety
Values interpolated into rendered output are escaped through the framework's template layer,
never hand-built string interpolation of model or user data. Secrets live in runtime config,
never in code, fixtures, or version control. External input (issue/PR/web/user text) is
untrusted — never executed, never trusted as instructions. Authentication, authorisation, cryptography and
permission changes never take a shortened review path.

### Article VI — Documentation
Public API changes ship their docs in the same PR: README + CHANGELOG updated. Docstrings,
component annotations and code comments follow
[`docs/contributing/standards/code-documentation.md`](docs/contributing/standards/code-documentation.md). If the repo ships
built docs, they must build clean.

### Article VII — Dependency discipline
A new runtime dependency requires a stated justification (Simplicity applied to the dependency
tree; prefer the shared toolchain bundle over ad-hoc dev dependencies). `deptry` must pass:
no unused, missing, or transitively-relied-upon dependencies.

### Article VIII — Internationalization
User-facing strings are translatable. In Python (models, forms, views, admin, template tags,
validators) they are wrapped with `gettext_lazy` (imported as `_`); templates load
`{% load i18n %}` and wrap strings with `{% trans %}` / `{% blocktrans %}`. Model `verbose_name`
/ `verbose_name_plural` and form `label` / `help_text` / `error_messages` use `gettext_lazy`; pure
acronyms are exempt. A package ships a base English (`en`) catalog and a `locale/` directory so
host projects can compile or extend translations. CI runs `makemessages` clean over the source as
the i18n gate; correct wrapper usage is otherwise enforced by review, and a hard-coded user-visible
string in a PR is a blocking comment. A package with no user-facing strings satisfies this
trivially.

### Article IX — Data-model conventions (Django)
Every model field is a deliberate indexing decision. Because consumers of a published package cannot
add their own indexes, any field with a plausible lookup / filter / ordering path is indexed at its
definition (`db_index`, `unique`, an FK's automatic index, or a composite `Meta.constraints` /
`Meta.indexes`); a field with no query path stays unindexed to avoid write cost. The choice —
indexed or not, and why — is recorded (plan `data-model.md` or `decisions.md`). `verbose_name` and
`help_text` are mandatory on every model field (Article VIII). **Migrations are consolidated per
PR:** the migrations a feature branch introduces are squashed into as few files as possible before
the PR is submitted (branch-local and unapplied, so safe at any release stage); data migrations
(`RunPython`/`RunSQL`) are exempt from auto-regeneration — keep them via `squashmigrations` or
standalone.

### Article X — Cohesion (Python)
Related behaviour is grouped in a class, not scattered across module-level functions.

**The test:** two or more module-level functions that share a *subject* belong on a class. They
share a subject when they operate on the same data, take the same first argument, are only
meaningful in sequence, or are named around the same noun (`build_x`, `validate_x`, `render_x`).

**Why this is a standard and not a taste.** In a published package, a class is the extension
point. A consumer who needs different behaviour subclasses it and overrides one method. A module
of functions can only be monkey-patched, which is not a supported interface and breaks on any
internal change. Grouping also gives the behaviour a name, a place for shared configuration, and
one import instead of six.

**Shape:** shared state or configuration → a regular class holding it. Grouping for namespacing
with no shared state → still a class, with `@classmethod`/`@staticmethod`, or a small frozen
dataclass carrying the config. Expose a module-level convenience function only as a thin wrapper
over the class, never as the implementation.

**Django first.** Where the framework already owns the grouping, use it rather than inventing a
class: a `QuerySet`/`Manager` method instead of a function taking a queryset, a model method or
property instead of a function taking an instance, a `Form`/`Serializer` method instead of a free
validation function, a `TemplateView` method instead of a helper called by a view.

**Exceptions — narrow, and stated rather than assumed.** A genuinely standalone pure function with
no siblings. Framework-dictated module shapes: `conftest.py` fixtures, migrations, `urls.py`,
`apps.py`, decorator-registered template tags and filters, signal receivers, management-command
entry points. Factory functions that return the class. A module of independent utilities that
genuinely share no subject.

**This does not license abstraction.** Article III still holds: one class grouping today's
behaviour is the goal, not a base class, a registry, or a hierarchy built for a second
implementation that does not exist. Grouping related functions is organisation; adding a layer
between the caller and the work is not.

## Project articles

### Article XI — No charting library is vendored or served

This package ships no third-party JavaScript. A charting library is never committed to this
repository, never placed in its static files, and never added to a bundle it produces.

Two supported ways for the library to reach the browser:

1. **A CDN**, used in development and by the demo project. It keeps the local loop free of a Node
   toolchain, and it is the right trade for a demonstration.
2. **A bundle the host project builds**, which is the production recommendation and the reason for
   this article. ECharts ships ES modules with per-chart-type and per-component entry points, so a
   project importing a line chart and a tooltip pays for a fraction of the full build. A vendored
   copy would take that choice away and hand every project the whole library.

The package states which global it needs and says so in the browser console when it is absent. It
never injects a `<script>` tag pointing at a third-party origin on the reader's behalf. A project
that installs this package gains no external origin it did not already have.

### Article XII — Python builds the chart, the template places it

A chart is a pyecharts object, built in Python by the project and put in the template context. The
template places it with `<c-chart>` and says nothing about what it is. The chart type, the data,
the axes, the legend, the tooltip and every appearance decision are the chart object's, which is
where the whole of ECharts is already reachable.

This package ships one component. A second one is a change to this constitution rather than a
feature: a second way to put a chart on a page means a page author has to know which to reach for,
and there is no question a second component would answer that the chart object does not.

What belongs here is everything the chart object cannot do from Python: the figure's markup, its
sizing, its accessible name and text alternative, carrying the options to the browser safely, and
keeping a drawn chart at the size of its box.

### Article XIII — Pass through rather than mirror

Every option a chart understands is reached by building it into the chart object. Nothing here
names an option, defaults one, filters one, or renames one.

This package does not mirror someone else's option surface in Python or in template attributes. A
mirror is permanently one release behind the thing it mirrors, it forces a decision about every
option whether or not anyone asked for it, and it turns an upstream addition into work here. An
attribute vocabulary over a charting library's options is that mirror by another name, and it
cannot be partial for long: the first chart that needs an unnamed option reaches past it, and from
then on the vocabulary is a second way to say what the options already said.

An attribute on `<c-chart>` earns its place only by being about the page rather than about the
chart. `height` qualifies, because a chart object has no way to know what box a template gave it.
Anything the chart object could carry itself does not.

### Article XIV — Rendered output is a contract, and how a chart looks belongs to the page

Components render valid, semantic HTML. Every packaged component has a test proving it renders,
and a change to its output updates or adds a test asserting the part of the contract it changed.
Assertions are made against rendered output, never against the presence of a class name: a class
assertion proves a string is in a template and says nothing about what the browser draws.

A chart drawn into a canvas is invisible to assistive technology and to anyone who cannot
distinguish the colours, so the component takes an accessible name and a text alternative
describing what the chart shows. Neither decides whether a chart is drawn. A plain chart on a page
that supplies its own surrounding markup is an ordinary thing to want, and refusing to draw one is
the package overruling the page about its own content. The case for writing both is made in the
documentation, where it can be argued rather than enforced.

Appearance is not this package's to set. A chart looks the way the chart object says it looks, and
a page that wants something else changes the chart object. Nothing here writes a colour, a width, a
marker, a legend rule or an animation, and nothing here removes one either — the defaults a reader
sees are pyecharts', stated in the documentation as pyecharts' rather than presented as this
package's taste. Colour is not derived from the theme the surrounding application happens to be
running: matching a canvas to a running theme costs a colour-space implementation, something
watching for the theme to change and a repaint path, and it makes this package responsible for a
guarantee no charting library offers.

### Article XV — Compatibility

The package is pre-1.0 and the README says so. Component names and attribute surfaces may change
between minor versions, and every such change is recorded in the CHANGELOG. Default behaviour
stays stable across patch releases. There are no compatibility aliases: an API is changed cleanly,
and the CHANGELOG is how a consumer finds out.

Supported versions are Python 3.12 or later and the currently-supported Django releases, with the
CI matrix as the authoritative statement of both. Dropping either is a minor-version change with a
CHANGELOG entry. The django-mvp floor moves forward when a component needs something an older
release does not ship, and moving it is a CHANGELOG entry rather than a silent bump.

ECharts' own version is not pinned by this package, because this package does not ship it. What is
stated, in `mvp_charts.versions`, is the range it is known to render against.

## Quality bar

Read at planning and at review; applies to every change.

- Test coverage meets the floors in `docs/contributing/standards/testing.md`, which `codecov.yml`
  enforces.
- Every public API change updates README and CHANGELOG in the same pull request.
- `ruff check`, `ruff format --check`, `mypy` and `deptry` pass — through
  `pre-commit run --all-files`, which is the gate, rather than a bare invocation that reports
  findings in paths the hooks exclude.
- The package builds, its metadata is valid, and the README renders on the package index with
  absolute URLs.

`djlint` is configured in `pyproject.toml` and can be run over `mvp_charts/templates`, but it is
deliberately **not** a gate: it misfires against Cotton's `<c-vars>` syntax and needs ignore rules
first. Do not cite it as an enforced standard until it runs in CI.

## Non-negotiables

- Tests, build and lint pass before a change merges. Nobody overrides a red check.
- The default branch requires one approval, and the author of a change never approves it.

---

**Version**: 2.0.0 | **Ratified**: 2026-09-21 | **Last Amended**: 2026-09-28
