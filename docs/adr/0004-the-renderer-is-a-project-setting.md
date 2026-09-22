# ADR 0004 — The renderer is a project setting, and no chart names its own

**Status:** accepted

## Decision

Which renderer ECharts draws with — `canvas` or `svg` — is read from
`MVP_CHARTS_CONFIG["echarts"]["renderer"]` and applied to every chart in the project. No chart
component takes a `renderer` attribute.

The setting is validated when it is read. A value that is neither `canvas` nor `svg` raises
`ImproperlyConfigured` rather than being quietly treated as `canvas`.

This is the package's first project-level setting, and it establishes the shape of the rest:
settings are grouped by charting library, because a renderer means nothing to a library that is not
ECharts and a flat key would have to be renamed the day a second one arrives.

## Why

The renderer is an argument to `echarts.init`, not one of the options `setOption` takes, so raw
`options` cannot reach it. Whatever this package does with it is the only route a project has.

What decides the renderer is a fact about a project rather than about a chart. ECharts' own
guidance puts the choice on the devices being served, how many charts a page carries and how much
memory they have between them — canvas above roughly a thousand points, SVG where memory is tight,
where a page holds many charts at once, or where a chart is zoomed or printed. A template author
writing one tag among several on a page is not the person holding that information, and a page
whose charts disagreed about the renderer would be the result of nobody deciding rather than
somebody choosing.

There is a harder reason, which is what settles it. A project that bundles ECharts itself imports
only the renderers it uses. Asking for one it did not register is not an error: zrender falls back
to whichever renderer the bundle does have and says nothing, so a template reading `renderer="svg"`
can be drawing on canvas with nothing anywhere reporting the difference. Whether `svg` can be
honoured at all is a property of the project's bundle — decided by the same person, in the same
place, as the setting.

Validating the setting follows from the same fact. ECharts will not complain about a renderer it
does not know, so a typo would produce a chart that looks entirely correct and ignores what the
project asked for. There are exactly two legal values and they are known at startup, which is early
enough to refuse.

## Revisit if

A project has a genuine reason for one chart on a page to differ from the rest — a single
print-targeted chart among screen ones, or one chart far larger than its neighbours. A per-chart
attribute overriding the setting can be added then, and it will be answering a case somebody
actually had rather than one this package imagined.
