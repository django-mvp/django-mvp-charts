# django-mvp-charts

Charts as Cotton components for [django-mvp](https://github.com/django-mvp/django-mvp) projects. One namespace per charting library, starting with [Apache ECharts](https://echarts.apache.org/).

Putting a chart on a Django page is mostly plumbing. You serialise a queryset to JSON, drop a `<div>` with an id, write a `<script>` block that finds the div and hands the JSON to a charting library, then repeat all of it on the next page with slightly different options and a slightly different id. The chart is three lines of intent buried in thirty lines of wiring.

This package moves the wiring into a component, so the intent is what stays in your template:

```html
<c-echarts.line id="revenue" name="Revenue" description="Revenue by month."
                :values="[820, 932, 901]" :labels="['Jan', 'Feb', 'Mar']" />
```

## Status

Version 0.0.1. The chart region is in place, and so is the first chart type — a line chart. Nothing here is stable.

## Requirements

- Python 3.12+
- Django 5.2 or 6.0
- django-mvp 0.23.0+

## Install

```bash
pip install django-mvp-charts
```

Add it to `INSTALLED_APPS`, after `mvp`:

```python
INSTALLED_APPS = [
    ...,
    "mvp",
    "mvp_charts",
]
```

Components are then available under the namespace of the library they render with:

```html
<c-echarts.bar ... />
```

Then load three scripts from your own base template — ECharts, and this package's two modules:

```html
{% load static %}
{% block extra_js %}
  {{ block.super }}
  <script src="https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js"
          integrity="sha384-C2iskrW/uPW46KzOjrvJIQo4YkV8lkD+QS0CrDN18IIPIpT/g2USu8bTP3nvmIAD"
          crossorigin="anonymous"
          referrerpolicy="no-referrer"></script>
  <script defer src="{% static 'mvp_charts/js/chart-region.js' %}"></script>
  <script defer src="{% static 'mvp_charts/js/echarts-chart.js' %}"></script>
{% endblock %}
```

`chart-region.js` is what a chart region needs in the browser: it checks the library arrived, checks the region has a box to draw into, and publishes the resize contract below. `echarts-chart.js` is what a line chart needs beside it: it waits for a region to report it is ready, draws into it, and redraws on the resize contract `chart-region.js` publishes. Neither has a dependency of any kind, both are safe to evaluate twice, and both are served from this package's static files.

All three lines are yours. This package emits no script tag of any kind and supplies no component that does. Which pages carry them, where in the document they go, whether they are bundled with the rest of your JavaScript, and whether they need a nonce under your content security policy are your project's decisions to make, and a component making them on your behalf would be taking them away. If one page in your project shows a chart, put all three lines on that page rather than in the base template.

The ECharts line above is the development route, covered in full under [Getting ECharts to the browser](#getting-echarts-to-the-browser). A project that bundles ECharts itself drops it and keeps the other two.

## Placing a chart region

A chart region is the space a chart is drawn into. Give it a height:

```html
<c-echarts.region id="monthly-revenue"
                  name="Monthly revenue"
                  height="320px"
                  description="Revenue by month over the last year, rising from January to a December peak." />
```

**A region can also take its height from the element around it, instead of carrying one itself:**

```html
<div style="height: 200px">
  <c-echarts.region id="signups"
                    name="Signups"
                    description="New accounts per week for the last quarter." />
</div>
```

This is a second sizing mode, not a replacement for the first — a chart sharing a grid row, a dashboard tile or a flex child has no fixed number to write on the tag, and filling the wrapper exactly is what that mode buys. Neither mode invents a height: no default, no minimum, no aspect ratio. A region placed in an element with no resolved height, and given none of its own, gets none at all — which is the most common way a first attempt goes wrong, so the region says so on the page instead of rendering as an empty box.

Only `id` is required:

- `id` is the element id. The caption and the drawing surface are both built from it, which is what ties the right description to the right chart, and it is how your own JavaScript finds the region to listen to. Leave it out, or pass an empty string, and the region is replaced by a message saying so. It is never defaulted to nothing and never generated for you — an id this package invented would be stable only until someone added a second chart higher up the page, at which point every id below it would shift.
- `name` is what a screen reader announces the chart as. Optional: leave it out, or pass an empty string, and the region still renders, with no `aria-label` on the drawing surface.
- `description` is what the chart shows, in words. Optional in the same way, and carried as a `figcaption` only when given.

**A chart drawn into a canvas is invisible to anyone who cannot see it, and to anyone who cannot tell its colours apart.** Leaving out `name` and `description` is a real choice, not a shortcut: without them there is nothing else on the page for a screen reader to announce, or for someone who cannot make out the shape of the line to read instead. Give both whenever the chart is more than decoration.

## Drawing a line

`<c-echarts.line>` is a chart region that already knows how to draw. It takes everything a region does — `id` is required and `name`/`description` are optional in exactly the same way — plus the values to draw and, optionally, what each point is called. The smallest working chart is one tag, an id and values, and nothing else:

```html
<c-echarts.line id="quarterly-orders" height="320px" :values="[54, 61, 58, 70]" />
```

The fully-described version below is the one to reach for whenever the chart is more than decoration:

```html
<c-echarts.line id="monthly-revenue"
                name="Monthly revenue"
                height="320px"
                description="Revenue by month over the last year, rising from January to a December peak."
                :values="[820, 932, 901, 934, 1290, 1330, 1320, 1250, 1400, 1520, 1600, 1710]"
                :labels="['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']" />
```

**`:values` and `:labels` carry Python values, and the colon is what says so.** Write `:values="[820, 932, 901]"`, never `values="820, 932, 901"` — the second form is text, and this package never reads data out of text. It splits nothing on a separator, guesses at no numbers, and does not report the mistake: a value written as text travels into the chart's options object exactly as it arrived, and the chart does not draw, which is how you find out.

`:labels` is optional. Leave it out and the points still draw, in the order the values were given, numbered by their position rather than named.

Every value you pass is drawn, in the order you passed it. Nothing is reordered, dropped, combined, rounded or filled in — the original list is gone by the time the component holds it, and no template could put any of that back.

## Styling a chart

A chart's appearance belongs to the page, not to this package. `<c-echarts.line>` writes no colour, no line width, no marker, no legend rule, no grid or axis line decision, no animation and no typeface — a chart given values and nothing else looks the way ECharts draws that data on its own.

`:options` is how you reach anything ECharts offers, including an option this package has never heard of. It carries a Python value, deep-merged over what the component built, and it wins on every key it names:

```html
<c-echarts.line id="conversion-rate"
                name="Conversion rate"
                height="320px"
                :values="[2.1, 2.4, 2.2, 2.8, 3.1, 3.4, 3.0]"
                :options="{'series': [{'lineStyle': {'color': '#7c3aed'}}]}" />
```

That chart draws with the colour given, and no other. This package neither supplies a palette of its own nor derives one from the daisyUI theme your project is running — a colour left unset is ECharts' own default, not this package's.

The merge is deep: a mapping in `:options` merges recursively with the mapping the component built, rather than replacing it wholesale, so `{'xAxis': {'axisLine': {'show': false}}}` only turns the axis line off and leaves everything else about `xAxis` as it was. A list, `series` aside, replaces a list outright — there is no position to merge two arbitrary lists against. `series` is the one exception: its entries are matched by position, so `{'series': [{'lineStyle': {'color': '#7c3aed'}}]}` adds a line colour to the first series without touching the data that series already carries.

`docs/options.md` describes how the options object is built, for anyone reading the source or adding a chart type.

## Keeping its shape

A page is not a fixed rectangle. The window is resized, a sidebar collapses, a tab reveals content that was hidden when the page loaded. A region tracks the element around it through all of that, so it is never left at a size the page has stopped having.

When its box changes, a region dispatches `mvp-chart-region:resize` on itself, carrying the measured box:

```js
document.querySelector('#monthly-revenue').addEventListener(
  'mvp-chart-region:resize',
  (event) => { chart.resize(event.detail); }
);
```

| | |
|---|---|
| Event | `mvp-chart-region:resize`, bubbling |
| Target | the region element |
| `detail` | `{ width, height }` in CSS pixels |
| Fires | whenever the region's box changes, including when it is first revealed |

This is what a chart type subscribes to in order to redraw. It exists before any chart type does, so the first one has a contract to meet rather than a gap to work around. The event carries the box because the alternative is every listener measuring the same element again.

## When a region cannot draw

Two things stop a region drawing, and both look identical on screen: an empty box, no error, nothing to act on. So neither is left as one. The region says what is wrong, in the page, where the chart would have been — the same in development and in production, because a blank rectangle in production is exactly as undiagnosable as one in development.

**No charting library.** The region waits first. A bundle that loads a moment after the page does is an ordinary project, and accusing it would send someone to fix something that is not broken. Once waiting stops being a reasonable explanation — the page has finished loading, and a few seconds have passed since — it says so and names both ways to supply one.

**No height to fill.** The wrapper resolved to nothing, usually a percentage height inside an ancestor sized by its own content. The region takes enough room to say so, and points at the element that should be carrying the height.

The height is judged the first time the region is visible, not the first time the page paints. A region inside a collapsed panel or an unselected tab has no height for reasons that are not a mistake, and it is measured when it is revealed. Once a region has been seen at a usable height it is never judged again, so closing that panel later reports nothing: that is the page working, not a fault.

One region failing leaves every other region on the page working.

## Getting ECharts to the browser

A region reads one thing: `window.echarts`. Anything that puts the library there works, and nothing in this package records or asks which route you chose.

**In development**, a script tag in your own base template is the whole of it — no Node toolchain, no build step. The line under [Install](#install) is one you can copy.

Two details in it are worth keeping. Pin the version rather than floating it, because a URL without a version is a different file on any given day. Then `integrity` and `crossorigin` go together: a browser only checks an integrity hash on a cross-origin request made in CORS mode, so a hash without `crossorigin` is never verified while still looking as though it is.

This package does not supply that tag, and there is no component here that renders one. It ships no copy of ECharts, names no origin, and loads nothing on a reader's behalf, so installing it adds no external origin you did not choose.

**In production**, build a bundle and expose the library as `window.echarts`. Drop the script tag and change nothing else. ECharts ships per-chart-type and per-component entry points, so a page importing a line chart and a tooltip pays for a fraction of a full build, which is why the recommendation is to bundle rather than to keep loading the whole thing.

`mvp_charts.versions.ECHARTS_SUPPORTED_VERSIONS` states what the `echarts` namespace is known to render against: `>=6.0,<7.0`. The library is not a dependency of this package, so that is not enforced at install time. It is what the namespace claims, and a bundle outside the range is untested rather than blocked.

## Scope & philosophy

**What this is.** A presentation layer for charts: Cotton components that take data and options as attributes and render the markup and initialisation a charting library needs. How a chart looks is the page's call rather than this package's: a series is drawn with the charting library's own palette and the library's own defaults until an attribute or a passed-through option says otherwise.

**Each charting library gets its own namespace, and you choose one.** `<c-echarts.line>` speaks ECharts. A future Plotly namespace would speak Plotly. There is no neutral `<c-chart.line>` that renders through a swappable backend, and there is not going to be one. Charting libraries differ in small, load-bearing ways, and an interface that hides those differences can only expose what all of them have in common — then needs an escape hatch to the native options for anything real, at which point it is a translation layer you are paying to work around. Library-agnostic here means the package is not welded to one library, not that a chart is portable between them.

**What this deliberately is not.**

- **Not a JavaScript distribution.** No charting library is vendored into this package or served from it. Development and the demo project load ECharts from a CDN. Production projects are expected to bundle it themselves, importing only the chart types and renderers they use — a full ECharts build is several hundred kilobytes, and most pages need a fraction of it.
- **Not an application.** No models, no views, no URLs, no migrations. Data arrives as an attribute on the component, from a view the project already has.
- **Not a query or aggregation layer.** Turning a queryset into series is the project's job. This package takes the result.
- **Not a dashboard framework.** Components render one chart each. Composing them into a page is layout, which django-mvp already handles.
- **Not a wrapper around every ECharts option.** The common cases get named attributes. Everything else passes through to the underlying options object rather than being mirrored in Python.
- **Not a theming layer.** Nothing here reads the daisyUI theme your site is running, translates it into chart colours, or repaints a chart when the theme changes. Deriving a palette from a running theme means implementing colour-space maths, watching for the theme to change and repainting on every chart, and it would make this package responsible for a guarantee no charting library offers. Give a chart the colours you want it to have.

**Tie-breaks.** When these pull against each other: passing through beats abstracting, what the page asked for beats a default this package invented, and one obvious way to render a common chart beats a complete mapping of the option surface.

## License

MIT
