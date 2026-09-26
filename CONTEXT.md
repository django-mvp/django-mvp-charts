# django-mvp-charts

Domain model for django-mvp-charts — charts built in Python and placed on a page with one Cotton
component, for projects built on django-mvp.

The terms below are the ones to use in issues, commits and tests. Several exist to keep this
package's language distinct from the libraries it sits between, because those libraries use the
same English words for different things and mixing the vocabularies makes a bug report unreadable.

## Core concepts

**Chart object**:
A pyecharts chart, built by the host project in Python and put in the template context. It carries
the chart type, the data and every option. It is the thing this package renders, and this package
never builds one, subclasses one or adds to one.
_Avoid_: chart component (the component is the tag, not the chart), figure, widget, plot.

**Component**:
`<c-chart>`, the single Cotton component this package ships. It renders the figure a chart is drawn
into, the accessible name and text alternative, and the options payload. It names nothing about the
chart.
_Avoid_: namespace, chart type as a component name, tag family.

**Chart type**:
What is being drawn — line, bar, scatter, pie. A property of the chart object, decided by which
pyecharts class the project instantiated, and never visible in the template.

**Series**:
One set of values drawn as a single visual run: one line, one set of bars. The word is pyecharts'
and ECharts' own and is used here in exactly their sense.

**Options**:
The configuration object ECharts consumes — the object passed to `setOption`. The chart object
builds it and `dump_options()` serialises it. This package escapes it for a script element and
carries it to the browser, and changes nothing else about it.
_Avoid_: config, settings (which means Django settings), spec, schema.

**Pass-through**:
The rule that this package names, defaults, filters and renames no option. Anything a chart can be
told is told to the chart object in Python. The alternative is a template-attribute mapping of
someone else's option surface that is permanently one release behind it.

**Host project**:
The Django project that installs this package. It owns the theme, the base template, the data, the
chart objects it builds, and how ECharts is delivered to the browser in production.
_Avoid_: consumer, client, downstream, user.

**Theme**:
A daisyUI theme, supplied by django-mvp and selected by the host project. It styles the page a
chart sits on and nothing inside the chart. Colours inside a chart come from the chart object, and
a chart does not change when the theme does.
_Avoid_: skin, palette (the palette is part of a theme, not a synonym for it), colour scheme
(ECharts has a `theme` of its own, which is a different thing entirely and never a synonym for
this one).

**Delivery**:
How ECharts' JavaScript reaches the browser. Two supported answers: a CDN, used in development and
in the demo project, and a bundle the host project builds, which is the production recommendation.
This package never vendors or serves the library itself.
_Avoid_: bundling (that names only one of the two), asset pipeline, static files.

**Decal pattern**:
A pattern ECharts draws on a series (stripes, dots, dashes) so it can be told from the others by
more than its colour. pyecharts leaves it off. It is switched on where the chart is built, through
the `aria` option, and this package neither adds nor removes it.
_Avoid_: texture, hatching, fill pattern, accessibility mode.

**Generated description**:
The sentence ECharts writes about a chart when its `aria` option is on and its label is not turned
off. It replaces the `aria-label` the component writes from `name`, so it is left off wherever the
tag's `name` and `description` are the chart's text alternative.
_Avoid_: auto description, aria label (the tag's `name` becomes the aria-label; this is a different text).

## Terms deliberately not used

**Backend**: there is one charting library and one Python API over it. The word implies a
swappable one, which would mean an interface across libraries, which this package does not have.

**Dashboard**: a thing built out of charts, not a thing this package ships. Naming it would invite
requests for layout, filtering and refresh, none of which belong here.

**Data source**: implies this package fetches or queries something. It does not; a finished chart
arrives in the template context.
