# Feature Specification: Charts a reader can follow without telling colours apart

**Feature Branch**: `003-patterns-beside-colour`

**Created**: 2026-09-25

**Status**: Draft

**Serves**: G4 — a chart is usable by someone who cannot see it, extended here to someone who can
see it but cannot tell its colours apart

**Roadmap**: R4 — a chart that is genuinely usable without seeing it

**Issue**: #55

**Input**: A host project building charts for a general audience finds, in this package's
documentation, that ECharts can draw each series with its own decal pattern as well as its own
colour, how to turn that on where the chart is built, and when it is worth doing, so that readers who
cannot tell the colours apart can still follow the chart. The package draws nothing itself and
defaults nothing: the patterns are the chart object's to ask for, and the name and description on
the tag remain the chart's only text alternative.

## Clarifications

### Session 2026-09-25

- Q: What turns the patterns on without costing the chart its accessible name? → A: ECharts' `aria`
  option has two parts. Its generated description writes a sentence into the drawing surface's
  accessible name, replacing the one the author gave on the tag. Its decal patterns are drawn inside
  the chart and touch nothing else. The guidance turns `aria` on with the generated description off
  and the patterns on, which draws the patterns and leaves the author's name in place. Checked
  against the demo project on ECharts 6.1.0.
- Q: Which marks actually receive a pattern? → A: Checked by reading the elements ECharts drew rather
  than by looking at the chart. Bars and pie slices are patterned. A line's pattern goes on the area
  under it, which pyecharts leaves at zero opacity, so nothing shows unless that area is shaded.
  Scatter points are never patterned. The legend's icons follow the series in every case.
- Q: What does the demo show? → A: A bar chart with at least two series told apart only by colour,
  because that is the case the patterns exist for and a mark type they visibly apply to.
- Q: Does the guidance document every decal setting ECharts offers? → A: No. It shows how to turn the
  patterns on and how to change their colour, and points at ECharts' own documentation for the rest.
  Describing the whole decal option surface here would be the mirror this package declines to keep.
- Q: What does the guidance say about a project that leaves ECharts' generated description on? → A:
  That it replaces the name given on the tag, because the chart object asked ECharts to write one,
  and that the package does not step in. The recommendation is to leave it off and write the name and
  description on the tag.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Turn patterns on without losing the chart's name (Priority: P1)

A host project has a chart whose series are told apart only by colour, and some of its readers
cannot tell those colours apart. The developer reads this package's documentation, finds that ECharts
can give each series a pattern as well as a colour, copies the lines that turn the patterns on where
the chart is built, and gets a chart those readers can follow. The name and description they wrote
on the tag still reach a screen reader exactly as before.

**Why this priority**: It is the whole of what the issue asks for. Without it the option exists in
ECharts, pyecharts turns it off, and nothing here says it is there.

**Independent Test**: Follow the documented example on a chart with two series, and confirm from the
elements ECharts drew that each series' bars carry a pattern, and from the drawing surface that the
name given on the tag is still its accessible name.

**Acceptance Scenarios**:

1. **Given** a chart built with the documented patterns option, **When** it is drawn, **Then** each
   series' bars are drawn with a pattern as well as their colour, and the legend's icons match.
2. **Given** that chart placed with a `name` and a `description`, **When** it is drawn, **Then** the
   drawing surface's accessible name is still the `name`, and the description is still what it
   points at.
3. **Given** the documentation, **When** a developer looks for how to turn patterns on, **Then** they
   find the Python that does it, written where a chart is built, and it is the same code the demo
   project runs.
4. **Given** the demo project, **When** it is running, **Then** one of its pages shows a chart with
   patterns on, beside the code that built it.
5. **Given** a chart built without the patterns option, **When** it is drawn, **Then** nothing about
   it changes: the package turns nothing on by itself.

---

### User Story 2 - Know where patterns show and where they don't (Priority: P2)

A developer turns patterns on for a line chart, or a scatter chart, and sees nothing change. Before
that happens, the guidance has told them which kinds of chart the patterns apply to, what the
colour-independent cue is on the kinds they don't, and what to change when the patterns are hard to
see. Each of those statements is checked against the version of ECharts the package claims to render
against, so the guidance cannot quietly stop being true.

**Why this priority**: The P1 story is enough for the case the patterns are for. This one stops the
guidance from misleading anyone outside that case, which matters, but only once the option is
described at all.

**Independent Test**: For each chart kind the guidance names, turn the patterns on and read back from
the elements ECharts drew whether the marks carry a pattern, and compare that with what the guidance
says.

**Acceptance Scenarios**:

1. **Given** the guidance, **When** a developer reads it, **Then** it says patterns apply to bars and
   pie slices, and to a line only when the area under it is shaded.
2. **Given** a plain line chart or a scatter chart, **When** a developer reads the guidance, **Then**
   it tells them the colour-independent cue there is the line's style or the points' shape, which are
   also set where the chart is built.
3. **Given** a chart shown on a dark background, **When** a developer reads the guidance, **Then** it
   tells them the default pattern is dark and translucent and where its colour is set.
4. **Given** a project that leaves ECharts' generated description on, **When** a developer reads the
   guidance, **Then** it tells them that description replaces the name on the tag, and recommends
   leaving it off.
5. **Given** each statement above about which marks are patterned, **When** the test suite runs,
   **Then** a test confirms it against the drawn chart.

---

### Edge Cases

- **A chart with a single series.** Patterns add nothing a reader needs, and the guidance says the
  option is for series told apart by colour alone.
- **Series already labelled directly on the chart.** Each label names its series, so colour is not
  the only cue and the guidance does not recommend patterns there.
- **A chart built with the generated description on.** It replaces the tag's name. The package does
  not intervene, because the chart object asked for it, and the guidance says so.
- **A chart that sets its own decal shapes or colours.** They reach ECharts untouched, as every
  option does.
- **A project bundling a version of ECharts outside the supported range.** The statements are
  checked against the supported range only. Outside it they are untested, like everything else.

## Requirements *(mandatory)*

### Functional Requirements

**Turning patterns on — US1**

- **FR-001**: The documentation MUST describe, in plain terms, that ECharts can draw each series
  with a pattern as well as a colour and that pyecharts leaves it off.
- **FR-002**: The documentation MUST show the Python that turns the patterns on where a chart is
  built, with ECharts' generated description off.
- **FR-003**: The documentation MUST state that the `name` and `description` on the tag remain the
  chart's text alternative when the patterns are on.
- **FR-004**: The demo project MUST show a chart with patterns on, of at least two series told apart
  by colour, beside the code that built it, and that listing MUST be the code the demo runs.
- **FR-005**: The package MUST NOT turn the patterns on, choose a pattern, or add any option or
  attribute for them. They are the chart object's to ask for.
- **FR-006**: `CONTEXT.md` MUST define **decal pattern** in ECharts' sense.

**Where patterns show — US2**

- **FR-007**: The guidance MUST name the marks that receive a pattern: bars, pie slices, and a line's
  area only when it is shaded.
- **FR-008**: The guidance MUST name the colour-independent cue for a plain line and for scatter
  points, which is the line's style and the points' shape.
- **FR-009**: The guidance MUST say the default pattern is dark and translucent and where its colour
  is set on the chart object.
- **FR-010**: The guidance MUST say that ECharts' generated description replaces the name on the tag
  and recommend leaving it off.
- **FR-011**: Every statement the guidance makes about which marks carry a pattern MUST be confirmed
  by a test that reads the drawn chart in a browser.

### Traceability

| Requirement | Story |
|---|---|
| FR-001 – FR-006 | US1 |
| FR-007 – FR-011 | US2 |

### Key Entities

- **Decal pattern**: ECharts' term for a pattern drawn on a series in addition to its colour. Set on
  the chart object, drawn inside the chart, and never part of the chart's text alternative.
- **Generated description**: ECharts' own machine-written sentence about a chart. Distinct from the
  `description` an author writes on the tag, and never recommended here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can turn patterns on for an existing chart by adding the documented lines
  where it is built and changing nothing on the tag.
- **SC-002**: On a chart with patterns on, 100% of its series' bars or slices carry a pattern, and
  the drawing surface's accessible name is the tag's `name`.
- **SC-003**: Every mark-type statement in the guidance has a browser test, and each of those tests
  fails if the statement is made false.
- **SC-004**: A chart built without the patterns option renders byte-identical options before and
  after this feature.

## Assumptions

- The work is documentation, a demo chart and tests. The package's own code does not change.
- The supported ECharts range is the one `mvp_charts.versions` already states, `>=6.0,<7.0`.
- pyecharts keeps emitting `aria` as part of a chart's options, which is how the patterns reach
  ECharts through this package without anything new being carried.
