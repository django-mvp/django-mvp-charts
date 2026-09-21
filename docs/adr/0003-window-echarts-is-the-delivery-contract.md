# ADR 0003 — `window.echarts` is the whole delivery contract, and nothing declares which route supplied it

**Status:** accepted

## Decision

A chart region looks for `window.echarts` and uses whatever it finds. That is the entire contract
between this package and the project that installs it.

A project in development places `<c-echarts.cdn />` in its own base template. A project in production
builds a bundle and exposes the library as that global. Nothing in this package records, reads or
asks which of the two is in play, and the two pages are byte-identical once a region has settled.

## Why

The requirement is that neither route is declared. A setting naming the route, a data attribute
carrying it, or a registry of delivery strategies would each be a declaration, and each would need
maintaining in step with what the project actually does — a project that changes its mind and forgets
the setting gets a package confidently wrong about its own environment.

The global does not need inventing. A script tag from a public copy defines it, and a bundle that
imports ECharts and assigns it produces the same one. The contract already exists in both routes, so
adopting it costs nothing and describes what is true rather than imposing something new.

It also keeps this package out of the business of loading third-party code. A region never injects a
script tag at an origin the project did not choose; the delivery component is a tag a project places
itself, and a project that bundles omits it. Installing this package adds no external origin.

The cost is that a region cannot tell "not loaded yet" from "never coming", which is why it waits
before reporting rather than judging at first render. That is a consequence of this decision, and it
is carried in the specification rather than worked around.

## Revisit if

A second backend arrives. The global's name belongs to the backend, not to this package, so this is a
per-namespace fact — the second namespace states its own and neither reads the other's.
