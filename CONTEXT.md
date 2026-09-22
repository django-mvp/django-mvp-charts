# django-mvp-charts

Domain model for django-mvp-charts — charts as Cotton components for projects built on django-mvp.

The terms below are the ones to use in issues, commits, tests and component names. Several exist to
keep this package's language distinct from the charting libraries it renders with, because those
libraries use the same English words for different things and mixing the two vocabularies makes a
bug report unreadable.

## Core concepts

**Chart component**:
The unit this package ships: one Cotton component that renders one chart, configured entirely
through its attributes. `<c-echarts.line>` is a chart component.
_Avoid_: widget, graph, plot, visualisation, chart type (which means something narrower — see
below).

**Backend**:
A charting library this package can render with. ECharts is the first backend. A backend is chosen
by the template author per chart, by picking a namespace, and is never swapped by configuration.
_Avoid_: engine, renderer (ECharts uses *renderer* for its canvas-versus-SVG choice, which is a
different decision entirely), driver, provider.

**Namespace**:
The first segment of a component tag, naming the backend: `echarts` in `<c-echarts.line>`. Cotton
resolves it to a directory, so `mvp_charts/templates/cotton/echarts/`. The namespace is the
backend rather than this package, which is what allows a second backend to be added alongside the
first without touching it.
_Avoid_: prefix, module, family.

**Chart type**:
What is being drawn — line, bar, scatter, pie. The second segment of the tag. A chart type belongs
to a backend: `echarts.line` and a hypothetical `plotly.line` are distinct components with
distinct attributes, not two implementations of one thing.

**Series**:
One set of values drawn as a single visual run: one line, one set of bars. The word is the
charting libraries' own and is used here in exactly their sense.

**Options**:
The configuration object a backend consumes — for ECharts, the object passed to `setOption`. The
components build it from their attributes and hand it over. Named attributes cover the common
cases; anything else passes through unchanged.
_Avoid_: config, settings (which means Django settings), spec, schema.

**Pass-through**:
The rule that an option this package does not name is still reachable, forwarded to the backend
untouched rather than being mirrored as a Python or template API. The alternative is a mapping of
someone else's option surface that is permanently one release behind it.

**Host project**:
The Django project that installs this package. It owns the theme, the base template, the data and
how the charting library is delivered to the browser in production.
_Avoid_: consumer, client, downstream, user.

**Theme**:
A daisyUI theme, supplied by django-mvp and selected by the host project. It styles the page a
chart sits on and nothing inside the chart. Colours inside a chart come from the charting library
or from the options the page passes it, and a chart does not change when the theme does.
_Avoid_: skin, palette (the palette is part of a theme, not a synonym for it), colour scheme
(ECharts has a `theme` of its own, which is a different thing entirely and never a synonym for
this one).

**Delivery**:
How the backend's JavaScript reaches the browser. Two supported answers: a CDN, used in development
and in the demo project, and a bundle the host project builds, which is the production
recommendation. This package never vendors or serves the library itself.
_Avoid_: bundling (that names only one of the two), asset pipeline, static files.

## Terms deliberately not used

**Agnostic**: overloaded to the point of being misread as "charts are portable between backends",
which is the opposite of the design. Say which backend, or say *per-backend namespace*.

**Dashboard**: a thing built out of charts, not a thing this package ships. Naming it would invite
requests for layout, filtering and refresh, none of which belong here.

**Data source**: implies this package fetches or queries something. It does not; data arrives as an
attribute.
