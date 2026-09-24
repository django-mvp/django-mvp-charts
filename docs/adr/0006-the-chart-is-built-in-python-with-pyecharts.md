# ADR 0006 — The chart is built in Python with pyecharts, and the template only places it

**Status:** accepted
**Supersedes:** the attribute-vocabulary direction recorded in [ADR 0004](0004-the-project-loads-the-browser-module-and-names-its-regions.md)'s
component surface, and the four-component sketch that was open against it.

## Decision

A chart is a [pyecharts](https://pyecharts.org) object, built by the host project in Python and put
in the template context. The package ships one Cotton component, `<c-chart>`, which renders the
figure, its accessible name and text alternative, its sizing, and the chart's own
`dump_options()` output as JSON. A single browser module hands that JSON to ECharts and keeps each
chart at the size of its box.

pyecharts becomes a hard dependency. It is the API: without it there is no way to build the object
the component takes.

No component names a chart type, and no attribute names an ECharts option. The five attributes on
the tag are `:chart`, `id`, `height`, `name` and `description`, and the last four are about the page
rather than about the chart.

## What this replaces

The package was building an attribute vocabulary over ECharts' option surface: `:values`,
`:labels`, `:options` and a deep merge behind them, with one component per chart type and a plan for
named attributes covering axes, legend, tooltip and value formatting. Alongside it, a set of
on-page failure states — a missing charting library, a wrapper that resolved to no height, a missing
id — each with its own translated message, its own wait-and-judge logic in the browser, and its own
demonstration.

Both are removed.

## Why

**An attribute vocabulary cannot be partial for long.** ECharts' option surface is large and it
grows. Every attribute named here is a decision about one option out of hundreds, and the first
chart that needs an unnamed one reaches past the vocabulary for raw options — from which point the
vocabulary is a second way to say what the options already said. Three roadmap items existed only to
extend it.

**pyecharts is that vocabulary, already written and maintained.** It is MIT-licensed, has shipped
since 2017, covers 44 chart types and 112 option classes, and it converts the types a Django view
actually produces — `date`, `datetime`, `Decimal` and `None` — without anything here doing it.
Whatever it can build, the component places.

**The feedback machinery cost more than it bought.** Reporting a missing library, an unresolved
height and a missing id took a library poll, a load-grace window, an `IntersectionObserver`, two
translated message strings carried as data attributes, a custom-event contract between two browser
modules, and the greater part of the test suite. What a project shows its readers when something is
broken is the project's decision, and a message this package drew into the page took it away.
Console messages are what remain.

## Consequences

**Charts look different.** pyecharts writes its own defaults — point labels on, animation on,
tooltip and legend configured — where this package wrote none and left ECharts' own. That is now
documented as pyecharts' doing rather than presented as taste, and every one of them is a keyword
argument where the chart is built.

**A second charting library is no longer a design this package holds open.** The per-library
namespace existed to make one possible. Binding the API to a pyecharts object binds it to ECharts,
so the component is `c-chart` with no namespace, and adding a second library would be a new decision
rather than a slot already cut for it.

**`JsCode` does not cross.** `dump_options()` emits a JsCode function unquoted, which is not JSON
and could only be delivered by evaluating server-rendered code in the page.
`dump_options_with_quotes()` is valid JSON, but the function arrives as a string and ECharts ignores
it silently. Neither is offered as support: a formatter that does nothing without saying so is worse
than one that was never advertised. A chart carrying one is refused where its options are
serialised, with an error naming the option, so the refusal is read where the chart is built rather
than in a browser console. A project needing a formatter writes it against the chart instance in its
own JavaScript.

**The `</script>` escape stays.** pyecharts escapes none of the three sequences that can end a
script element early, so a label read out of a database reaches `dump_options()`'s output verbatim.
The three-character translation table is what stands between a page's data and its structure, and it
is asserted against three hostile labels rather than assumed.

## Alternatives considered

**`render_embed()`.** pyecharts' own HTML output. It emits a complete `<!DOCTYPE html>` document
with a hardcoded CDN script tag, a Chinese locale and a fixed 900×500 pixel size. It is a
standalone-file exporter, not an embed, and none of those three is configurable from the call.

**Accepting either a chart object or a plain options dictionary.** Two supported shapes means a page
author has to know which to reach for, and every piece of documentation has to cover both. The
chart object is the one shape.
