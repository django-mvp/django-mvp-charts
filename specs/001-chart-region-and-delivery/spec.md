# Feature Specification: A chart region, and the library that draws into it

**Feature Branch**: `001-chart-region-and-delivery`

**Created**: 2026-09-21

**Status**: Draft

**Serves**: G1 — a chart is put on a page by passing attributes to a component, data included, and
the page author writes no JavaScript

**Roadmap**: R1 — a chart occupies a region of the page, and the library reaches the browser

**Input**: A chart region that a template author places like any other component, expanding to fill
the sized wrapper the project gives it, holding its shape when the window or that wrapper changes
and when it becomes visible after being hidden, with several on a page fully independent of each
other. The charting library is present in development without a build step and comes from the host
project's own bundle in production, with no declaration required either way. When the library is
absent, or the region resolves to no height, the page says so where the chart would have been
rather than showing a blank rectangle. It draws no chart.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Put a chart region on a page (Priority: P1)

A template author building a page wants somewhere for a chart to live. They already have a card, a
panel or a grid cell with a height. They place one component tag inside it, give it a name and a
description of what the chart will show, and get a region that fills that space. They write no
JavaScript and they pick no size, because the space they put it in is the size.

**Why this priority**: Nothing else in this feature has a subject without it. The region is what
every later chart type is drawn into, and it is the only part a template author touches directly.

**Independent Test**: Render a page with the component inside a wrapper of a known height and assert
against the rendered output that the region is there, carries the author's name and description, and
claims the wrapper's space. No charting library and no chart type are needed to prove it.

**Acceptance Scenarios**:

1. **Given** a wrapper with a height, **When** an author places one chart region inside it and
   supplies a name and a description, **Then** the rendered page contains a region occupying that
   wrapper's full width and height, carrying that name and description, and the author has written
   no JavaScript.
2. **Given** an author places a chart region, **When** they omit the name or the description,
   **Then** the page says which one is missing where the region would have been, rather than
   rendering a region with an empty name.
3. **Given** a page with five chart regions in five wrappers of different sizes, **When** the page
   renders, **Then** each region fills its own wrapper, each is separately identifiable, and none
   of them reads or changes another's state.
4. **Given** a chart region, **When** the page is read by someone who cannot see it, **Then** the
   region announces itself by the author's name and its description is reachable as text.

---

### User Story 2 - The charting library reaches the browser (Priority: P2)

Someone setting a project up wants a chart to work. Locally that has to happen without installing a
JavaScript toolchain or running a build first. They add the package, open a page, and the library is
there. In production they build a bundle carrying only the chart types they use, and the region uses
that bundle without being told about it. Neither case asks them to configure which one is in play.

**Why this priority**: A region with nothing to draw into it is inert. This is what makes the region
capable of holding a chart, and it is the half of the feature a project owner touches rather than a
template author.

**Independent Test**: Start the project with no build tooling present and confirm a page carrying a
region reports the library as available. Then supply the library the way a bundling project does and
confirm the same page works with no settings changed between the two runs.

**Acceptance Scenarios**:

1. **Given** a project with no JavaScript build tooling installed, **When** a developer opens a page
   carrying a chart region, **Then** the library is available to that region and the region does not
   report it missing.
2. **Given** a project that builds its own bundle exposing the library, **When** a page carrying a
   chart region renders, **Then** the region uses that bundle, and no project setting was added to
   say so.
3. **Given** a project that installs this package, **When** its pages are served to a reader,
   **Then** the package has added no third-party origin the project was not already loading, and has
   shipped no copy of a charting library.

---

### User Story 3 - A region that cannot draw says why (Priority: P3)

A region with no library, and a region squeezed into a wrapper with no resolved height, are the same
blank rectangle to anyone looking at the page. Both states say what is wrong, in the page, where the
chart would have been. Whoever is looking can act on what it says without opening developer tools and
without knowing how the package works.

**Why this priority**: Both failures are silent by default, and both are the standard way a first
attempt goes wrong. The second one is created by this feature's own decision that a region has no
size of its own. A failure nobody can diagnose costs more than the feature saves.

**Independent Test**: Render the page with the library withheld and assert the rendered output names
it. Separately, place a region in a wrapper whose height does not resolve and assert the page says so
and takes enough room to be read.

**Acceptance Scenarios**:

1. **Given** the charting library is not available to a region, **When** the page renders, **Then**
   the space the region occupies carries a message naming what is missing and what would fix it.
2. **Given** a region in a wrapper whose height does not resolve to a usable value, **When** the page
   renders, **Then** the region reports that it has no height to fill, and takes enough vertical
   space for that message to be read.
3. **Given** a page with several regions where one of them cannot draw, **When** the page renders,
   **Then** the failing region carries its message and every other region on the page still works.
4. **Given** either failure, **When** it happens in a production project rather than in development,
   **Then** the page states it the same way, rather than failing silently or reporting only to a
   developer console.

---

### User Story 4 - The region holds its shape as the page changes (Priority: P4)

A page is not a fixed rectangle. The window is resized, a sidebar collapses, a tab reveals content
that was hidden when the page loaded. A region tracks the wrapper it was given through all of that,
so it is never left at a size the page has stopped having.

**Why this priority**: It is the difference between a region that works on the developer's screen and
one that works on a real page. The region has to exist and be fillable before it can be made to
survive change.

**Independent Test**: Change the wrapper's size and the window's size after the page has rendered, and
reveal a region that started hidden, asserting in each case that the region's measured area matches
its wrapper's.

**Acceptance Scenarios**:

1. **Given** a rendered page with a chart region, **When** the browser window is resized, **Then** the
   region still fills its wrapper exactly, with no clipped or leftover area.
2. **Given** a rendered page with a panel that collapses or a layout that reflows, **When** the
   wrapper itself changes size without the window changing, **Then** the region follows it.
3. **Given** a region inside a container that was hidden when the page loaded, **When** the container
   is revealed, **Then** the region fills it at that point rather than staying at the size it had
   while hidden.
4. **Given** a wrapper that is resized repeatedly, **When** the changes arrive faster than the region
   can respond to each one, **Then** the region settles at the final size rather than falling behind
   or leaving the browser busy.

---

### Edge Cases

- **A wrapper whose height never resolves.** The common shape is a percentage height inside an
  ancestor sized by its own content, which resolves to nothing. Covered by US3 as a reported failure
  rather than a blank.
- **A region that had a height and loses it later**, because a user collapsed the panel holding it.
  This is not a setup mistake and is not reported as one. The region has no room to draw in, and gets
  it back when the panel reopens.
- **A region placed with no wrapper at all**, directly in the flow of the page. It resolves to no
  height and is reported the same way as any other unresolved wrapper.
- **The library arriving after the region runs**, which is what a deferred or asynchronously loaded
  bundle does. Reporting it missing the instant a region renders would be wrong in a project doing
  nothing unusual.
- **A library present at a version the namespace does not claim to render against.** The package
  states a supported range per namespace and does not pin the library, so this case is stated rather
  than policed.
- **Two regions given the same name by the author.** Independence is the requirement, so they stay
  separate regardless.
- **A name or description supplied as an empty string** rather than omitted. Treated as omitted.
- **A page with no regions on it.** The package adds nothing to such a page.

## Requirements *(mandatory)*

### Functional Requirements

**Placing a region — US1**

- **FR-001**: A template author MUST be able to place a chart region with a single component tag and
  no JavaScript anywhere in the template.
- **FR-002**: A chart region MUST expand to fill the width and height of the wrapper the host project
  places it in.
- **FR-003**: A chart region MUST have no size of its own. The wrapper is the only thing that decides
  how large a region is, and the package MUST NOT supply a fallback height that lets a region appear
  at a size nobody chose.
- **FR-004**: Several chart regions on one page MUST be independent of one another: each identified
  by an id its template author gave it, and none reading or writing another's state. The package MUST
  NOT generate an id for a region, because an id it invented would be stable only until the page
  placed another region above it.
- **FR-005**: Every chart region MUST carry an id, an accessible name and a text alternative
  describing what the chart shows, all three supplied by the template author.
- **FR-006**: A region whose id, name or text alternative is missing or empty MUST report that
  visibly, in place of the region, rather than rendering with an empty value.
- **FR-007**: The demo project MUST show a placed region inside the wrapper that sizes it, and the
  documentation MUST show the markup that produced it, wrapper and every required attribute included,
  since neither the size nor the id has a default for an example to fall back on.

**Getting the library to the browser — US2**

- **FR-008**: A project in development MUST be able to render a working chart region without
  installing a JavaScript toolchain and without running a build.
- **FR-009**: A project that builds a bundle exposing the charting library MUST have that bundle used,
  without adding any project setting naming which delivery is in play.
- **FR-010**: The package MUST NOT vendor, serve or bundle a charting library, and a chart region MUST
  NOT load one from a third-party origin on a reader's behalf. A project that installs the package
  gains no external origin it was not already loading.
- **FR-010a**: A chart region MUST emit no script tag of any kind, including for the package's own
  module. Which pages carry that module, where in the document it goes and whether it is bundled with
  the project's other JavaScript are the project's decisions, and the package MUST NOT take any of
  them.
- **FR-011**: The package MUST state, per namespace, the range of the charting library's own versions
  it is known to render against, and MUST NOT pin that library as a dependency.
- **FR-012**: The documentation MUST state both ways the library reaches the browser and what a
  project does for each, and MUST show the script tag that loads the package's own module, since none
  of it is discoverable from the component surface.

**Saying what is wrong — US3**

- **FR-013**: When the charting library is not available to a region, the page MUST show, in the space
  the region occupies, a message naming what is missing and what would fix it.
- **FR-014**: When a region's wrapper gives it no usable height at the time it first renders, the page
  MUST show, in that region, a message saying so, and the region MUST take enough vertical space for
  that message to be read.
- **FR-015**: A region that renders successfully and later loses its height MUST NOT report a failure.
  It has no room to draw in until it is given room again.
- **FR-016**: Both failure messages MUST appear in the page itself, identically in development and in
  production, rather than only in a developer console.
- **FR-017**: A region that cannot draw MUST NOT prevent any other region on the same page from
  working.
- **FR-018**: A region MUST NOT report the library missing on the strength of its being absent at the
  instant the region first runs, because a project may legitimately load it a moment later.
- **FR-019**: The demo project MUST show both failure states deliberately, rather than leaving them to
  be discovered.

**Holding shape — US4**

- **FR-020**: A rendered region MUST continue to fill its wrapper when the browser window is resized.
- **FR-021**: A rendered region MUST continue to fill its wrapper when the wrapper changes size
  without the window changing.
- **FR-022**: A region that was not visible when the page loaded MUST fill its wrapper when it becomes
  visible.
- **FR-023**: Rapid, repeated size changes MUST leave the region at the final size, without the region
  falling behind or leaving the browser unresponsive.

### Traceability

| Story | Requirements | Success criteria |
|---|---|---|
| US1 — Put a chart region on a page | FR-001 … FR-007 | SC-001, SC-002, SC-006 |
| US2 — The charting library reaches the browser | FR-008 … FR-012 | SC-003, SC-004 |
| US3 — A region that cannot draw says why | FR-013 … FR-019 | SC-005 |
| US4 — The region holds its shape as the page changes | FR-020 … FR-023 | SC-007 |

### Key Entities

- **Chart region**: the sized area of the page a chart occupies, placed as a component by a template
  author and filled by the chart drawn into it. It is the unit this feature delivers. A region exists
  and is placeable before any chart type does, and chart types are later drawn into it rather than
  replacing it. This is a new term for the package glossary.
- **Wrapper**: the host project's own element that gives a region its size — a card, a panel, a grid
  cell. It belongs to the project rather than to this package, and this feature's central decision is
  that it is the only thing deciding how big a region is.
- **Delivery**: how the charting library reaches the browser. Already defined in the package glossary
  and used here in exactly that sense: a public network copy during development, and the host
  project's own bundle in production.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a base template that already loads the two scripts, a template author puts a
  working chart region on a page by writing one component tag inside a wrapper they already have, with
  zero lines of JavaScript in the template.
- **SC-002**: A page carrying five chart regions renders all five, each filling its own wrapper, with
  no region affected by any other.
- **SC-003**: A developer who has installed the Python package and added two script tags to their base
  template renders a page with a working region, having run no build step and installed no JavaScript
  tooling.
- **SC-004**: A project supplying the library from its own bundle needs zero configuration entries to
  make the package use it, and zero changes when moving between the two ways of getting it.
- **SC-005**: In every state where a region cannot draw, someone looking at the page can name the
  cause from what the page says, without opening developer tools and without reading this package's
  source.
- **SC-006**: Every packaged region is usable by someone who cannot see it: it carries a name and a
  description, and a region missing either fails visibly rather than rendering nameless.
- **SC-007**: After the window is resized, after the wrapper is resized, and after a hidden region is
  revealed, the region's area matches its wrapper's with no clipped or leftover space.

## Clarifications

Resolved during specification from the agreed feature statement, the package constitution and the
founding notes. Rationale too long to carry here is in `decisions.md`.

### Session 2026-09-21

- **Q**: The library has to be present in development without a build step, but the constitution
  forbids a component loading a third-party script on a reader's behalf. Which gives way?
  **A**: Neither. The package supplies the development delivery as something the project includes
  deliberately, as one line in its own base template, rather than a region injecting it. A project
  that bundles the library does not include that line. This is not a declaration of which delivery is
  in play: nothing branches on a setting, and a region uses whatever it finds. Integrated into
  FR-008, FR-009 and FR-010.

- **Q**: "No declaration required either way" and "the region reports a missing library" appear to
  conflict. How does a region tell a project that has not loaded the library yet from one that never
  will?
  **A**: It does not decide at the instant it first renders. A deferred or asynchronously loaded
  bundle is ordinary, so a region that finds nothing waits, and reports only once waiting has stopped
  being a reasonable explanation. Integrated as FR-018 and as an edge case.

- **Q**: A region that resolves to no height is reported as a failure, but a user collapsing a panel
  also takes a region's height away. Are they the same state?
  **A**: No. The first is a setup mistake at first render and is reported. The second happens to a
  region that already rendered correctly and is not a mistake at all. The region has nothing to draw
  into, and recovers when the panel reopens. Integrated as FR-014 and FR-015.

- **Q**: Article XV requires an accessible name and a text alternative on every packaged component and
  forbids silently defaulting either to empty. Does that obligation start here, when nothing is drawn
  yet, or at the first chart type?
  **A**: Here. The region is the thing being placed, so it is the thing carrying them, and a region
  shipped without them would have to be changed rather than extended when chart types arrive. A
  missing value is reported rather than defaulted. Integrated as FR-005 and FR-006.

- **Q**: Does the region keep an intrinsic minimum height as a safety net against the zero-height
  case?
  **A**: No. The owner's ruling is that a region expands into the space the project gives it, and the
  project is responsible for providing a sized wrapper. A fallback height would draw a chart at a size
  nobody chose and hide the setup mistake rather than fix it, which is why the zero-height case is
  reported instead. Integrated as FR-003 and FR-014.

### Session 2026-09-22

- **Q**: The region emits its own module's script tag, once per request, and numbers regions that were
  given no id. Both exist so a project configures nothing. Is that worth the machinery?
  **A**: No. Neither is this package's decision to take. A developer who can put the charting library
  in their own base template can put one more script tag beside it, and where that tag goes, which
  pages carry it, and whether it is bundled with the rest of the project's JavaScript are answers only
  the project has. A package that emits the tag itself would then owe an opt-out, and an opt-out for a
  default nobody asked for is a second mechanism paying for the first. The same holds for the id: a
  template author naming their own region is an ordinary request, and an id generated per request is
  stable only until a region is added above it. Both are removed, the id joins the required
  attributes, and a breaking change is what the changelog is for. Integrated into FR-004, FR-005,
  FR-006, FR-010a and FR-012, and SC-008 is withdrawn.

## Assumptions

- A chart region is a component a template author places today, not internal machinery staying
  invisible until the first chart type exists. Three of the roadmap item's deliverables can only be
  demonstrated by something that renders.
- "Its container changes" covers a region revealed after being hidden as well as a window resize.
  Being revealed is the usual way a chart ends up at the wrong size.
- The host project already has, or can write, a wrapper with a height. The package does not supply
  one, and the layout primitives for building one come from django-mvp rather than from here.
- Nothing in this feature colours anything. Theme handoff arrives with the first chart type, because
  until something is drawn there is nothing to colour.
- An empty region is a legitimate state between this feature and the first chart type, and should read
  as deliberate rather than broken.

## Out of Scope

Each of these belongs to a later roadmap item, and none is deferred work owed by this feature.

- Any chart type, and any option a chart type understands — line, bar, pie and scatter are R3.
- Turning a Python value into chart data, including dates, decimals and missing values — R2.
- Chart colour and theme handoff — R3, where something is first drawn.
- Named attributes for axes, legends and tooltips — R5.
- Number and date formatting — R6.
- A second charting library alongside ECharts — R7.
- Querying, aggregating or reshaping data, which stays the host project's job at every roadmap item.
