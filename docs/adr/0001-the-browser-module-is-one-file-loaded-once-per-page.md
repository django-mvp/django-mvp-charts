# ADR 0001 — The browser behaviour is one static file, emitted once per page by the component that needs it

**Status:** superseded by [ADR 0004](0004-the-project-loads-the-browser-module-and-names-its-regions.md)

## Decision

Everything a chart region does in the browser lives in one dependency-free JavaScript file in this
package's own static files. A region emits its script tag through a template tag that returns the tag
the first time it is called in a request and an empty string every time after.

Three properties follow, and all three are asserted:

- A page carrying no region requests nothing from this package.
- A page carrying five regions loads the module once.
- A project configures nothing to get either.

## Why

Three constraints meet here, and only one arrangement satisfies all of them.

A page with no region must load nothing new. That rules out putting the tag in the project's base
template, which is otherwise the obvious place for it: every page then pays for a component most of
them do not use, and the cost of installing this package stops being zero for pages that ignore it.

A page with five regions must not load five copies, and must not carry five inline copies of the
logic. That rules out a script tag per region, and it rules out an inline component per region.

The template author must configure nothing. That rules out asking the project to include the module
itself, which would also make the module's presence a thing to remember rather than a thing that
follows from placing a region.

A once-per-request template tag satisfies all three and is about a dozen lines. The per-request state
it needs already exists for another reason — regions are numbered per request so several on a page
stay separately identifiable — so it is one more method on a class that had to exist anyway.

**Alpine was available and was not used.** django-mvp bundles it, and an inline Alpine component is
the idiomatic answer in that stack. Registering one requires code that runs before Alpine starts,
which is a lifecycle dependency taken on for behaviour that needs none: two observers, a poll and a
custom event. It would also put a copy of the logic in every region's markup, which is the second
constraint again.

## Revisit if

Regions start arriving after page load, inserted by htmx or anything else. The module's
initialisation is idempotent and exposed, but nothing currently re-runs it for markup that appears
later, so that case needs a decision rather than a patch.
