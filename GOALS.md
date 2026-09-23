# Goals

These are the standing directions `django-mvp-charts` works toward. Each one is a capability or
quality to steer by, not a task that gets ticked off. Whether any goal has been served well enough
is decided in the roadmap, the feature specs, and review, never by the goal itself.

This file carries no version numbers or release plan; that lives in the roadmap. For what the
package is, what it stays out of, and the principles that settle a close call, read the
*Scope & philosophy* section of the [README](README.md).

Importance is a tag on each goal, not a ranking:

- **Essential** — not worth adopting without it.
- **Expected** — a complete, dependable version is expected to have it.

| ID | Goal | Importance | Status | Notes |
|----|------|------------|--------|-------|
| G1 | A chart built in Python is put on a page with one tag, and the page author writes no JavaScript | Essential | | |
| G2 | Whatever ECharts can draw is reachable, without this package having to name it first | Essential | | |
| G3 | The types a Django view produces reach a chart without being converted first | Expected | | |
| G4 | A chart is usable by someone who cannot see it | Expected | | |

_Written 2026-09-21. Revise as the goals change._
