# django-mvp-charts

Charts as a Cotton component for [django-mvp](https://github.com/django-mvp/django-mvp) projects, built in Python with [pyecharts](https://pyecharts.org) and drawn by [Apache ECharts](https://echarts.apache.org/).

Putting a chart on a Django page is mostly plumbing. You serialise a queryset to JSON, drop a `<div>` with an id, write a `<script>` block that finds the div and hands the JSON to a charting library, then repeat all of it on the next page with slightly different options and a slightly different id.

This package is the plumbing, and nothing else. Your view builds a chart:

```python
from pyecharts.charts import Line

context["revenue"] = (
    Line()
    .add_xaxis(["Jan", "Feb", "Mar"])
    .add_yaxis("Revenue", [820, 932, 901])
)
```

Your template places it:

```html
<c-chart :chart="revenue"
         id="revenue"
         height="320px"
         name="Monthly revenue"
         description="Revenue by month over the first half of the year, rising from January to a June peak." />
```

That is the whole API. One component, seven attributes, and no JavaScript on the page.

## Status

Version 0.0.1. Nothing here is stable.

## Requirements

- Python 3.12+
- Django 5.2 or 6.0
- django-mvp 0.24.0+
- pyecharts 2.1+

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

Then load two scripts from your own base template — ECharts, and this package's module:

```html
{% load static %}
{% block extra_js %}
  {{ block.super }}
  <script src="https://cdn.jsdelivr.net/npm/echarts@6.1.0/dist/echarts.min.js"
          integrity="sha384-C2iskrW/uPW46KzOjrvJIQo4YkV8lkD+QS0CrDN18IIPIpT/g2USu8bTP3nvmIAD"
          crossorigin="anonymous"
          referrerpolicy="no-referrer"></script>
  <script defer src="{% static 'mvp_charts/js/mvp-charts.js' %}"></script>
{% endblock %}
```

`mvp-charts.js` finds every chart on the page, hands its options to ECharts and keeps it at the size of its box. It has no dependency of any kind, it is safe to evaluate twice, and it is served from this package's static files.

Both lines are yours. This package emits no script tag and supplies no component that does. Which pages carry them, where in the document they go, whether they are bundled with the rest of your JavaScript, and whether they need a nonce under your content security policy are your project's decisions, and a component making them on your behalf would be taking them away. If one page in your project shows a chart, put both lines on that page rather than in the base template.

The ECharts line is the development route, covered in full under [Getting ECharts to the browser](#getting-echarts-to-the-browser). A project that bundles ECharts itself drops it and keeps the other.

## Building the chart

The chart is a pyecharts object, built wherever it is convenient to build one — a view, a service function, a management command that caches the result. pyecharts is a mature Python API over the whole of ECharts, so anything ECharts can draw is reachable, and it is reachable in Python rather than through a template attribute someone here had to think of first.

```python
from pyecharts import options as opts
from pyecharts.charts import Line


class ConversionView(TemplateView):
    template_name = "conversion.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["conversion"] = (
            Line()
            .add_xaxis(["Jan", "Feb", "Mar", "Apr", "May", "Jun"])
            .add_yaxis(
                "Conversion rate",
                [2.1, 2.4, 2.2, 2.8, 3.1, 3.4],
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=3, color="#7c3aed"),
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Conversion rate", subtitle="Per cent"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
            )
        )
        return context
```

pyecharts' own [documentation](https://pyecharts.org/#/en-us/) is the reference for what a chart can be told to do. This package neither extends it nor restricts it: whatever `dump_options()` returns is what reaches the browser.

**The types a Django view produces survive the trip.** Dates, times, `Decimal` values out of a money column and `None` where a row has no value are all serialised by pyecharts, so there is nothing to convert first and nothing arrives as the string `"None"`.

**A chart's appearance is pyecharts'.** Point labels, the legend, the tooltip and the animation are on by default because pyecharts turns them on, not because this package has an opinion — it writes no colour, no width, no marker and no default of any kind. Every one of them is a keyword argument where the chart is built.

## Placing the chart

`<c-chart>` renders the figure, its caption, the accessible name, the text alternative and the options payload. It names seven attributes and nothing about the chart itself.

| Attribute | Required | What it does |
|---|---|---|
| `:chart` | Yes | The pyecharts chart to draw. Written with a colon, because it is a Python value. |
| `id` | Yes | The element id. The caption and the text alternative are tied to it, and it is how your own JavaScript finds the figure. |
| `height` | No | A CSS height for the figure, caption included. |
| `aspect-ratio` | No | The shape of the figure instead of its height. Ignored when `height` is also given. |
| `name` | No | What a screen reader announces the chart as. |
| `caption` | No | A line printed under the chart, for everybody. Read out with the chart as well. |
| `description` | No | What the chart shows, in words, read instead of the picture. Never shown. |

`id` is never generated for you — an id this package invented would be stable only until someone added a second chart higher up the page, at which point every id below it would shift.

### Giving the chart a box

A chart is drawn into a canvas, and a canvas has to be told how big it is. There are three ways to say it, and the package invents none of them: no default height, no minimum, no fallback shape.

**A height on the tag** is the first, and it is the one above.

**A ratio on the tag** gives the figure its width from the page and works the height out from that:

```html
<c-chart :chart="signups" id="signups" aspect-ratio="16/9" name="Signups" />
```

Write it as a number, `2`, or as the fraction it comes from, `16/9`. The chart then keeps its shape at every window width instead of growing squatter as the column narrows, and a chart in a column that has no height of its own still has one. Both are what an outer element sized for the chart would otherwise be for.

**Neither** leaves the figure filling the element around it:

```html
<div style="height: 200px">
  <c-chart :chart="signups" id="signups" name="Signups" />
</div>
```

That suits a chart in a grid row, a dashboard tile or a flex child, where the layout already decides the box and there is no number to write on the tag.

**A chart drawn into a canvas is invisible to anyone who cannot see it, and to anyone who cannot tell its colours apart.** Leaving out `name` and `description` is a real choice, not a shortcut: without them there is nothing else on the page for a screen reader to announce, or for someone who cannot make out the shape of the line to read instead. Give both whenever the chart is more than decoration.

**A caption and a description are different texts, and a figure can carry both.** The caption is printed under the chart and assumes the reader can see it — the denominator, the unit, the date the figures were taken, or the one reading the chart cannot state on its own:

```html
<c-chart :chart="scores" id="scores" height="320px"
         name="Scores"
         caption="Usually 6 out of 10."
         description="Scores from 1 to 10, peaking at 6, with most between 4 and 8." />
```

The description replaces the picture for someone who cannot see it, so it carries what the chart shows. A screen reader reads the caption first and then the description. Only the caption takes room on the page: it sits inside the figure, under the chart, and the chart gives up the height it needs, so `height` and `aspect-ratio` still describe the whole figure.

### While the chart is still on its way

A chart is drawn by the browser, after the charting library has loaded and run. Until then the figure would be an empty box the size of the chart that is coming, so it holds a spinner in its centre instead. The browser module takes the spinner out once the chart is on the surface.

There is no attribute for it and nothing to switch on. Every chart waits, so every figure says so. A chart is arriving rather than missing, which is what a spinner says and an empty box does not.

There are no words with it either. A message this package wrote would need a translation catalogue it does not ship, and one you wrote would be a second thing to position and to keep away from a screen reader, which has the chart's `name` to announce already.

The spinner goes only when a chart replaces it, so a chart that never draws keeps it. That is deliberate: a figure that empties itself and stays empty tells a reader less than one that never stopped waiting. It is not a failure message, and this package still writes none — what went wrong is in the console.

## Keeping its shape

A page is not a fixed rectangle. The window is resized, a sidebar collapses, a tab reveals content that was hidden when the page loaded. Each chart watches its own figure and redraws at the new size, so it is never left at a size the page has stopped having.

## When something goes wrong

Three things go to the browser console, and nowhere else.

**No charting library.** `window.echarts` is not there. The message names both ways to supply one.

**A chart that throws while drawing.** Reported with the id of the figure it belongs to, and the other charts on the page carry on.

**A figure with a width and no height.** The one failure that otherwise leaves no trace: the options are right, ECharts started, nothing threw, and the reader sees blank page. It is almost always a percentage height inside an element sized by its own content. Said once per chart, naming the figure, and a `height` or an `aspect-ratio` on the tag is the fix. A chart inside a closed panel or an unselected tab measures nothing on either axis, which is the page working as intended, so it is not reported — and it draws itself when the panel opens.

Nothing is written into the page. What a project shows its readers when something is broken is the project's decision — an empty box with your own words around it, a fallback table, or nothing at all — and a message this package drew into the page would take that decision away.

## Reaching the chart from your own JavaScript

Once a chart is drawn, its figure dispatches an `mvp-chart:drawn` event carrying the ECharts instance. The event bubbles, so one listener on the document hears every chart on the page, and `event.target` is the figure, so the `id` you gave the tag says which chart it is:

```html
<script>
  document.addEventListener("mvp-chart:drawn", (event) => {
    if (event.target.id !== "revenue") return;
    const chart = event.detail.chart;
    chart.setOption({ tooltip: { formatter: (p) => `${p.name}: ${p.value}` } });
    chart.on("click", (p) => { /* … */ });
  });
</script>
```

That is the way in for anything the chart object cannot say from Python: a JavaScript formatter, a click handler, a chart redrawn when something else on the page changes. `setOption` merges into what the chart already has, so the options the server built stay as they were.

Each figure announces its chart once, when it is drawn and already sized to its box. A listener has to be in place before that happens: an inline script anywhere in the page is, and so is a script of your own loaded before `mvp-charts.js`. A script that only runs once the page has finished loading can miss the event, and can still reach a chart that has been drawn with `echarts.getInstanceByDom()` on the figure's `[data-mvp-chart-surface]` element.

## Getting ECharts to the browser

The module reads one thing: `window.echarts`. Anything that puts the library there works, and nothing in this package records or asks which route you chose.

**In development**, a script tag in your own base template is the whole of it — no Node toolchain, no build step. The line under [Install](#install) is one you can copy.

Two details in it are worth keeping. Pin the version rather than floating it, because a URL without a version is a different file on any given day. Then `integrity` and `crossorigin` go together: a browser only checks an integrity hash on a cross-origin request made in CORS mode, so a hash without `crossorigin` is never verified while still looking as though it is.

This package does not supply that tag, and there is no component here that renders one. It ships no copy of ECharts, names no origin, and loads nothing on a reader's behalf, so installing it adds no external origin you did not choose.

**In production**, build a bundle and expose the library as `window.echarts`. Drop the script tag and change nothing else. ECharts ships per-chart-type and per-component entry points, so a page importing a line chart and a tooltip pays for a fraction of a full build, which is why the recommendation is to bundle rather than to keep loading the whole thing.

A bundle has to register the renderer its charts are drawn with as well as their chart types. The renderer is the chart's to name, where it is built:

```python
Line(init_opts=opts.InitOpts(renderer="svg"))
```

A chart that names none is drawn to a canvas, because that is pyecharts' default, so a bundle carrying only `SVGRenderer` needs every chart built with the line above. SVG keeps a chart sharp when the page is zoomed and when it is printed. A canvas is a bitmap and stays one. The renderer is the only init option carried to the browser: the figure's box decides the size, so `width` and `height` there change nothing.

`mvp_charts.versions.ECHARTS_SUPPORTED_VERSIONS` states what this package is known to render against: `>=6.0,<7.0`. The library is not a dependency of this package, so that is not enforced at install time. It is what the package claims, and a bundle outside the range is untested rather than blocked.

## What does not cross to the browser

pyecharts' `JsCode`, which wraps a JavaScript function so it can be written inside a Python option, does not survive this route and is not supported. A chart carrying one is refused where its options are serialised, with an error naming the option it sits on, rather than reaching the browser as a document the page cannot parse.

Neither way of serialising such a function is offered as support. `dump_options()` emits it unquoted, which is no longer JSON and could only be delivered by evaluating server-rendered code in the page. The quoted variant is valid JSON, but the function arrives as a string and ECharts ignores it without a word — a formatter that silently does nothing is worse than one that is not offered.

Where you need a JavaScript formatter, write it in your own JavaScript and set it on the chart once it is drawn, as shown under [Reaching the chart from your own JavaScript](#reaching-the-chart-from-your-own-javascript).

## Scope & philosophy

**What this is.** A presentation layer for charts: one Cotton component that takes a chart object and renders the markup and initialisation ECharts needs. How a chart looks is decided where the chart is built, in Python, and never here.

**Python builds the chart; the template places it.** There is no attribute vocabulary over ECharts' options and there is not going to be one. An attribute layer is permanently behind the library it wraps, it forces a decision about every option whether or not anyone asked for it, and it can only ever expose the part someone here thought of — at which point every real chart reaches past it for the raw options anyway.

**What this deliberately is not.**

- **Not a JavaScript distribution.** No charting library is vendored into this package or served from it. Development and the demo project load ECharts from a CDN. Production projects are expected to bundle it themselves, importing only the chart types and renderers they use — a full ECharts build is several hundred kilobytes, and most pages need a fraction of it.
- **Not an application.** No models, no views, no URLs, no migrations. The chart arrives in the template context, from a view the project already has.
- **Not a query or aggregation layer.** Turning a queryset into series is the project's job. This package takes the result.
- **Not a dashboard framework.** The component renders one chart. Composing several into a page is layout, which django-mvp already handles.
- **Not a wrapper around pyecharts.** Nothing here subclasses a pyecharts chart, extends its options or adds a helper for building one. Whatever pyecharts returns is what is rendered.
- **Not a theming layer.** Nothing here reads the daisyUI theme your site is running, translates it into chart colours, or repaints a chart when the theme changes. Give a chart the colours you want it to have.

**Tie-breaks.** When these pull against each other: passing through beats abstracting, what the chart object says beats anything this package could add, and one obvious way to place a chart beats a second way to do the same thing.

## License

MIT
