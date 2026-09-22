# Progress — 002, a line chart drawn from values written in the template

A running log of what happened on this branch, newest entry last.

## 2026-09-22 — planning

Branch cut from `3efca44` on main, which already carries the specification (merged as #23) and the
constitution amendment that removed Article XV's colour claim (merged as #24). Baseline verified
green on that commit: lint, typecheck, 119 tests, build, conformance.

Plan, research and task list written. Thirteen tasks across the specification's three stories.
Three planning decisions recorded in `decisions.md`, none of which graduates to an architecture
decision record.

The sketch branch `sketch/chart-component-api` is prior art this plan draws on: its settled parts
(data as a Python value, empty defaults in `<c-vars>`, raw options merged last, `json_script` as
the carrier) are carried over, and the appearance defaults it wrote into every chart are not,
because the specification answers issue #17 by giving the package no appearance decisions at all.
