# django-mvp-charts

Charts as Cotton components for [django-mvp](https://github.com/django-mvp/django-mvp) projects. One namespace per charting library, starting with [Apache ECharts](https://echarts.apache.org/).

Putting a chart on a Django page is mostly plumbing. You serialise a queryset to JSON, drop a `<div>` with an id, write a `<script>` block that finds the div and hands the JSON to a charting library, then repeat all of it on the next page with slightly different options and a slightly different id. The chart is three lines of intent buried in thirty lines of wiring.

This package moves the wiring into a component, so the intent is what stays in your template:

```html
<c-echarts.line :data="monthly_revenue" x="month" y="total" title="Revenue" />
```

## Status

Version 0.0.1. The chart region is in place and nothing draws into it yet — the chart types come next. Nothing here is stable.

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

Then load two scripts from your own base template — ECharts, and this package's module:

```html
{% load static %}
{% block extra_js %}
  {{ block.super }}
  <script src="https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js"
          integrity="sha384-C2iskrW/uPW46KzOjrvJIQo4YkV8lkD+QS0CrDN18IIPIpT/g2USu8bTP3nvmIAD"
          crossorigin="anonymous"
          referrerpolicy="no-referrer"></script>
  <script defer src="{% static 'mvp_charts/js/chart-region.js' %}"></script>
{% endblock %}
```

`chart-region.js` is what a chart region needs in the browser: it checks the library arrived, checks the region has a box to draw into, and publishes the resize contract below. It has no dependencies, is safe to evaluate twice, and is served from this package's static files.

Both lines are yours. This package emits no script tag of any kind and supplies no component that does. Which pages carry them, where in the document they go, whether they are bundled with the rest of your JavaScript, and whether they need a nonce under your content security policy are your project's decisions to make, and a component making them on your behalf would be taking them away. If one page in your project shows a chart, put both lines on that page rather than in the base template.

The ECharts line above is the development route, covered in full under [Getting ECharts to the browser](#getting-echarts-to-the-browser). A project that bundles ECharts itself drops it and keeps the second line.

## Placing a chart region

A chart region is the space a chart is drawn into. Put it inside an element that already has a height:

```html
<div class="rounded-box border-base-300 border" style="height: 320px">
  <c-echarts.region id="monthly-revenue"
                    name="Monthly revenue"
                    description="Revenue by month over the last year, rising from January to a December peak." />
</div>
```

**The wrapper is where the height lives.** A region fills the element around it and has no height of its own — no default, no minimum, no aspect ratio. That is deliberate: a height invented by this package would be wrong on most pages and would stop a chart sharing a grid row with anything else. It does mean a region placed in an element with no resolved height gets none itself, which is the most common way a first attempt goes wrong, so the region says so on the page instead of rendering as an empty box.

All three attributes are required:

- `id` is the element id. The caption and the drawing surface are both built from it, which is what ties the right description to the right chart, and it is how your own JavaScript finds the region to listen to.
- `name` is what a screen reader announces the chart as.
- `description` is what the chart shows, in words. A chart drawn into a canvas is invisible to anyone who cannot see it, and to anyone who cannot tell its colours apart.

Leave any of them out, or pass an empty string, and the region is replaced by a message saying which are missing. None of them is defaulted to nothing, and none is generated for you — an id this package invented would be stable only until someone added a second chart higher up the page, at which point every id below it would shift.

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

**What this is.** A presentation layer for charts: Cotton components that take data and options as attributes and render the markup and initialisation a charting library needs. Charts read their colours from the daisyUI theme the host project is running, so they re-theme with the rest of the site instead of pinning literal colours into the template.

**Each charting library gets its own namespace, and you choose one.** `<c-echarts.line>` speaks ECharts. A future Plotly namespace would speak Plotly. There is no neutral `<c-chart.line>` that renders through a swappable backend, and there is not going to be one. Charting libraries differ in small, load-bearing ways, and an interface that hides those differences can only expose what all of them have in common — then needs an escape hatch to the native options for anything real, at which point it is a translation layer you are paying to work around. Library-agnostic here means the package is not welded to one library, not that a chart is portable between them.

**What this deliberately is not.**

- **Not a JavaScript distribution.** No charting library is vendored into this package or served from it. Development and the demo project load ECharts from a CDN. Production projects are expected to bundle it themselves, importing only the chart types and renderers they use — a full ECharts build is several hundred kilobytes, and most pages need a fraction of it.
- **Not an application.** No models, no views, no URLs, no migrations. Data arrives as an attribute on the component, from a view the project already has.
- **Not a query or aggregation layer.** Turning a queryset into series is the project's job. This package takes the result.
- **Not a dashboard framework.** Components render one chart each. Composing them into a page is layout, which django-mvp already handles.
- **Not a wrapper around every ECharts option.** The common cases get named attributes. Everything else passes through to the underlying options object rather than being mirrored in Python.

**Tie-breaks.** When these pull against each other: passing through beats abstracting, theme-driven beats hard-coded, and one obvious way to render a common chart beats a complete mapping of the option surface.

## License

MIT
