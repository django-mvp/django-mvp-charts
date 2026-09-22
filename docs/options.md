# How a chart's options are built

The supported way to configure a chart is the template. Write the attributes on the tag, and write
anything the tag does not name in its `options` attribute. This page describes what happens to those
attributes afterwards, for anyone reading the source or adding a chart type.

The three classes below live in `mvp_charts/echarts/options.py`. They are the ECharts namespace's
internals rather than an API to import: nothing outside that namespace calls them, and a chart type
added later is expected to reuse them rather than to reimplement the same decisions.

## `Attribute`

One attribute's Python value, exactly as the template author wrote it.

A value left at the component's empty default reads as not given. Everything else is returned
untouched, including `0`, `0.0` and a string. The class splits nothing, parses nothing and reports
nothing, which is what makes a value written as text a mistake the author sees rather than one the
package guesses at.

## `Line`

The options object for a line chart: its labels, its values, and nothing else.

It writes no grid, tooltip, legend, animation, colour, line width, symbol, axis tick or split line.
Every one of those is an appearance decision, and this package makes none — a chart drawn through
the component asks ECharts for what writing the same data through ECharts by hand would ask for.

## `Merge`

The author's `options` attribute, merged over what the component built.

- A mapping merges recursively, and the author's value wins on every key it names.
- A list replaces a list. There is no position to merge two arbitrary lists against.
- `series` is the exception. Its entries are matched by position and merged like mappings, so an
  option added to an entry keeps that entry's own data.
- No key is filtered anywhere the merge looks, including a key this package has never heard of. An
  option added to ECharts after this package was written reaches it unchanged.

The last point is the reason the merge exists rather than a list of supported options. A chart's
appearance belongs to the page, and an author who knows ECharts should never find an option out of
reach from the template.
