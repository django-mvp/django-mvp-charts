# ADR 0004 — The project loads the browser module, and the project names its regions

**Status:** accepted
**Supersedes:** [ADR 0001](0001-the-browser-module-is-one-file-loaded-once-per-page.md)
**Amended by:** [ADR 0006](0006-the-chart-is-built-in-python-with-pyecharts.md). Both decisions
below stand — the project still loads the module with its own `{% static %}` tag, and the id is
still the author's to give. What changed is the surface they apply to: there is one component
rather than a region and a chart type, the module is `mvp-charts.js`, and a missing attribute is no
longer replaced by a message in the page.

## Decision

A chart region emits no script tag. `chart-region.js` is loaded by the host project, from its own
template, with an ordinary `{% static %}` tag beside whichever line supplies the charting library.

A chart region generates no id. `id` joins `name` and `description` as a required attribute, and a
region missing any of the three is replaced by a message naming what is missing, which is what the
region already did for the other two.

Both properties are asserted: a rendered region contains no `<script>` at all, and a region given no
id renders no figure.

## Why

ADR 0001 built a per-request object that emitted the module's tag the first time a region asked for
it and nothing thereafter, and numbered regions that arrived without an id. Both were there so that a
project could install the package and configure nothing.

The owner's ruling, on reading the result: neither question is this package's to answer.

**Where a script tag goes is a property of the project, not of the component.** A project has a
content security policy, an asset pipeline, a decision about which pages carry which bundles, and an
opinion about what belongs in `<head>`. A tag emitted mid-body by whichever component happened to
render first is a decision taken on the project's behalf in the one place the project cannot reach.
Every project that disagreed would then need a way to turn it off — and a setting that disables a
default nobody asked for is a second mechanism paying the upkeep of the first.

**A developer who can load the charting library can load one more file.** The library already arrives
by a line the project writes itself, for exactly the reasons in ADR 0003. The module sits next to it.
That is one line of documentation, and it is a line the reader can see, move, bundle or drop.

**A generated id is stable only until the page changes.** Numbering regions in render order means
`mvp-chart-region-2` becomes `mvp-chart-region-3` the day someone adds a chart higher up the page —
silently, taking any stylesheet rule, test selector or event listener that named it. Asking the
template author for an id is an ordinary request, and the author is the only one who knows what the
region should be called.

**What this costs, stated plainly.** Renaming or splitting the module in a later version breaks every
project that named the old path, and a project upgrading has to read the changelog to find out. That
is what a changelog is for, and a package that avoids the cost by taking the decision is not avoiding
the cost so much as moving it somewhere the project cannot see.

**What it buys beyond the removal.** With no tag reading `context.request`, a region renders in any
template context at all, including one assembled outside the request cycle.

## Revisit if

Nothing foreseeable. A project wanting the old behaviour writes an include of its own, which is a
thing a project can do without this package's help.
