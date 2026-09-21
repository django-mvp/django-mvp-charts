# django-mvp-charts

Charts as Cotton components for [django-mvp](https://github.com/django-mvp/django-mvp) projects. One namespace per charting library, starting with [Apache ECharts](https://echarts.apache.org/).

Putting a chart on a Django page is mostly plumbing. You serialise a queryset to JSON, drop a `<div>` with an id, write a `<script>` block that finds the div and hands the JSON to a charting library, then repeat all of it on the next page with slightly different options and a slightly different id. The chart is three lines of intent buried in thirty lines of wiring.

This package moves the wiring into a component, so the intent is what stays in your template:

```html
<c-echarts.line :data="monthly_revenue" x="month" y="total" title="Revenue" />
```

## Status

Version 0.0.1. The repository is scaffolded and the test harness is green. No components are written yet, and nothing here is stable.

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
