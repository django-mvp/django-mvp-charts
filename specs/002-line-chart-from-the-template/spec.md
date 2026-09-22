# Feature Specification: A line chart, drawn from values written in the template

**Feature Branch**: `002-line-chart-from-the-template`

**Created**: 2026-09-22

**Status**: Draft

**Serves**: G1 — a chart is put on a page by passing attributes to a component, data included, and
the page author writes no JavaScript. G4 — whatever the charting library can do stays reachable from
the template, without writing JavaScript

**Roadmap**: R2 — Python values become chart data without hand-serialising

**Input**: A template author puts a working line chart on a page by writing one tag with the values
and point labels on it as Python literals, no JavaScript anywhere and nothing prepared in a view
first, drawn the way ECharts draws it with no colour or appearance decisions taken by the package,
and with an accessible name and description available but not required.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Draw a line chart from values written in the template (Priority: P1)

A template author has a page and some numbers they can type. They write one tag inside a wrapper with
a height, give it the values and what the points are called, and a line chart appears. They write no
JavaScript, they prepare nothing in a view, and they pick no size, because the wrapper is the size.

**Why this priority**: It is the first time anything in this package draws. Every other story here
changes a chart that has to exist before it can be changed, and the claim the package was built to
make is true of nothing until this one is done.

**Independent Test**: Render a template containing the tag with values and labels written on it, and
assert from the rendered page that those values and labels reached the chart in the order given. A
browser then confirms a line is drawn. No view, no data preparation and no other story are needed.

**Acceptance Scenarios**:

1. **Given** a wrapper with a height, **When** an author writes one line chart tag inside it with an
   id, a list of values and a list of point labels, **Then** the page renders a line chart drawn from
   exactly those values, and the template contains no JavaScript.
2. **Given** a line chart tag, **When** the author gives values but no point labels, **Then** the
   chart still draws, with the points in the order they were given.
3. **Given** a list of values, **When** the chart is drawn, **Then** it draws every value it was
   given, in the order it was given, with nothing reordered, dropped, combined, rounded or filled in.
4. **Given** a page carrying a line chart and a bare chart region from the previous feature,
   **When** the page renders, **Then** both work and neither reads or changes the other's state.
5. **Given** a line chart, **When** its wrapper or the window changes size, **Then** it keeps filling
   its wrapper, exactly as a region does.

---

### User Story 2 - A chart with nothing around it (Priority: P2)

A page needs a chart and nothing else: no heading, no caption, no card. The author writes the tag
with an id and the data and gets a chart. Giving it an accessible name and a text alternative is
still available, still worth doing, and no longer a condition of anything appearing.

**Why this priority**: It is the most common way a chart is placed, and it is the shape the previous
feature refuses to render. Until it works, the simplest use of the package is the one it rejects.

**Independent Test**: Render the tag with an id and values alone, and assert a chart is drawn rather
than a message about what is missing. Render it again with a name and a description and assert both
are carried.

**Acceptance Scenarios**:

1. **Given** a line chart tag carrying an id and values and nothing else, **When** the page renders,
   **Then** a chart is drawn, and no message about a missing name or description appears anywhere.
2. **Given** a line chart tag carrying a name and a text alternative as well, **When** the page
   renders, **Then** the chart announces itself by that name and the text alternative is reachable as
   text, exactly as the previous feature specified.
3. **Given** a line chart tag with no id, **When** the page renders, **Then** the page says the id is
   missing, because an id is still the author's to give and the package still invents none.
4. **Given** a name or a text alternative supplied as an empty string, **When** the page renders,
   **Then** it is treated as not given rather than carried as empty.

---

### User Story 3 - The chart is ECharts', not the package's (Priority: P3)

Someone who knows ECharts wants the chart ECharts would draw. They get it: the package writes no
colour, no line width, no marker size, no legend rule and no grid or axis decision. Anything the
component does not name is written on the tag and reaches ECharts untouched, so nothing about the
chart is out of reach from the template.

**Why this priority**: Without it nobody can style the chart at all, because the package supplies no
appearance of its own by deliberate decision and names only the attributes that carry data. It comes
after the chart draws because there is nothing to pass options to until then.

**Independent Test**: Draw a chart through the component and draw the same data through ECharts
directly with the equivalent options, and compare what each is asked to render. Then write an option
the component does not name on the tag and assert it arrives unchanged.

**Acceptance Scenarios**:

1. **Given** a line chart with values and nothing else, **When** it is drawn, **Then** it looks the
   way ECharts draws that data on its own, with no colour, width, marker, legend, grid, axis line,
   animation or typeface decision contributed by this package.
2. **Given** an option this component does not name, **When** an author writes it on the tag,
   **Then** it reaches ECharts unchanged, including options this package has never heard of.
3. **Given** an author who wants their chart to match their site, **When** they want a colour,
   **Then** they say which colour, and the package neither derives one from the running theme nor
   supplies one of its own.
4. **Given** the documentation, **When** an author looks for how a chart is styled, **Then** it says
   that appearance belongs to the page and shows how to reach ECharts' own options.

---

### User Story 4 - Data written as text says so (Priority: P4)

An author writes the values as a quoted string, the way an ordinary HTML attribute is written, rather
than as a Python value. Nothing about the page tells them what went wrong, because a component
Cotton cannot make sense of renders as nothing at all. This story makes the page say it.

**Why this priority**: It is a mistake every author will make once, and it is invisible without this.
It needs the chart to draw first, because the message only has a place to appear once a chart has one.

**Independent Test**: Render the tag with the values written as a plain string and assert the page
carries a message naming what to write instead, rather than an empty space or a chart drawn from
something invented.

**Acceptance Scenarios**:

1. **Given** values written as plain text rather than as a Python value, **When** the page renders,
   **Then** the space the chart would occupy carries a message naming what was given and what to
   write instead.
2. **Given** the same mistake, **When** it happens in a production project rather than in
   development, **Then** the page says it the same way, rather than failing silently or reporting
   only to a developer console.
3. **Given** text where a Python value was expected, **When** the page renders, **Then** the package
   does not split it, guess at separators, or decide which parts of it look like numbers.
4. **Given** one chart on a page making this mistake, **When** the page renders, **Then** every other
   chart and region on that page still works.

---

### Edge Cases

- **A chart given no values at all.** It draws whatever ECharts draws for an empty series. The
  package supplies no wording, no placeholder and no opinion about whether an empty chart should have
  been rendered, because only the page knows that.
- **More values than labels, or more labels than values.** Both are drawn as given. Padding one to
  match the other would be the package inventing data.
- **Values that are not numbers**, because a view handed over something unexpected. This feature
  passes what it was given, so the outcome is ECharts'. Converting types belongs to the next feature,
  where data comes from a view.
- **A name or description given but no id.** Still reported, since the id is the only one of the three
  that stays required.
- **A line chart placed with no wrapper**, or in a wrapper with no resolved height. Reported exactly
  as the previous feature reports it for a region.
- **An option written on the tag that ECharts rejects.** The package forwards it and ECharts decides.
  Policing someone else's option surface is what pass-through exists to avoid.
- **A page with a line chart and nothing else on it.** No card, no heading, no wrapper markup beyond
  the sized element. This is the ordinary case, not a corner.

## Requirements *(mandatory)*

### Functional Requirements

**Drawing a line chart — US1**

- **FR-001**: A template author MUST be able to put a working line chart on a page with a single
  component tag and no JavaScript anywhere in the template.
- **FR-002**: A chart's values MUST be given as a Python value written on the tag, and point labels
  MUST be given the same way. Neither MUST require anything to be prepared in a view first.
- **FR-003**: A chart given values and no point labels MUST still draw, with its points in the order
  they were given.
- **FR-004**: A chart MUST draw the values it was given, in the order it was given. The package MUST
  NOT reorder, drop, combine, round, cap or fill in data on the way through, because the original is
  gone by the time the component holds it and no template can undo any of those.
- **FR-005**: A line chart MUST occupy a region sized by the wrapper the host project places it in,
  MUST have no size of its own, and MUST keep filling that wrapper as the page changes, exactly as
  the previous feature specified for a region.
- **FR-006**: A line chart MUST carry an id supplied by its template author, and the package MUST NOT
  generate one.
- **FR-007**: The demo project MUST show a line chart on a page of its own, which is the first entry
  in its charts section, and the documentation MUST show the tag that produced it including the
  wrapper that sizes it.

**A chart with nothing around it — US2**

- **FR-008**: A line chart MUST render when given no accessible name and no text alternative.
- **FR-009**: A name and a text alternative, when given, MUST be carried exactly as the previous
  feature specified, and an empty string MUST be treated as not given.
- **FR-010**: This supersedes the previous feature's requirement that a missing name or text
  alternative is reported in place of the region. The id is unaffected and stays required, and a
  chart or region missing one is still reported.
- **FR-011**: The documentation MUST state plainly what a chart without a name and a text alternative
  costs the people reading the page, so that omitting them is a decision rather than an accident.

**The chart is ECharts', not the package's — US3**

- **FR-012**: Options this component does not name MUST be reachable from the tag and MUST reach
  ECharts unchanged, including options this package has never heard of.
- **FR-013**: The package MUST NOT contribute any appearance decision to a chart. It writes no
  colour, no line width, no marker size or visibility rule, no legend rule, no grid or axis line
  decision, no animation setting and no typeface.
- **FR-014**: A chart drawn through this package MUST ask ECharts for the same thing that drawing the
  same data through ECharts directly, with the equivalent options, would ask for.
- **FR-015**: The package MUST NOT derive a colour from the theme the host project is running, and
  MUST NOT ship a series palette of its own.
- **FR-016**: The documentation MUST state that a chart's appearance belongs to the page, and MUST
  show how to reach ECharts' own options from the template.

**Data written as text — US4**

- **FR-017**: An attribute carrying data that is given as text rather than as a Python value MUST be
  refused, with a message in the space the chart would occupy naming what was given and what to write
  instead.
- **FR-018**: The package MUST NOT parse text into data: no splitting on a separator, no guessing at
  which parts are numbers, and no deciding what an empty item means.
- **FR-019**: The message MUST appear in the page itself, identically in development and in
  production, rather than only in a developer console.
- **FR-020**: One chart making this mistake MUST NOT prevent any other chart or region on the same
  page from working.

### Traceability

| Story | Requirements | Success criteria |
|---|---|---|
| US1 — Draw a line chart from values written in the template | FR-001 … FR-007 | SC-001, SC-002, SC-006 |
| US2 — A chart with nothing around it | FR-008 … FR-011 | SC-003 |
| US3 — The chart is ECharts', not the package's | FR-012 … FR-016 | SC-004, SC-005 |
| US4 — Data written as text says so | FR-017 … FR-020 | SC-007 |

### Key Entities

- **Chart type**: what is being drawn, and the second segment of a component tag. This feature
  delivers the first one, `line`. Already defined in the package glossary and used here in exactly
  that sense.
- **Series**: one set of values drawn as a single visual run. This feature draws one. The word is the
  charting libraries' own and keeps their meaning.
- **Options**: the configuration object ECharts consumes. The component builds it from the attributes
  it names and hands it over, and anything it does not name is forwarded into it untouched. Already
  defined in the package glossary.
- **Pass-through**: the rule that an option this package does not name stays reachable rather than
  being mirrored. Defined in the glossary and given its first concrete surface here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A template author puts a working line chart on a page by writing one component tag
  inside a wrapper they already have, with zero lines of JavaScript in the template and nothing added
  to any view.
- **SC-002**: The values drawn are the values passed, in the order passed, in every case, including
  ones the package would have to be told about to change.
- **SC-003**: The smallest working chart is one tag carrying an id and a list of values, and it needs
  no surrounding markup at all.
- **SC-004**: Every appearance decision a chart displays can be traced either to ECharts' own
  defaults or to something the author wrote, and none of it to this package.
- **SC-005**: An author can reach any ECharts option from the template, including ones added to
  ECharts after this package was released, without writing JavaScript.
- **SC-006**: The demo project draws a line chart, and the documentation shows the complete markup
  that produced it.
- **SC-007**: An author who writes the data as text can name the cause from what the page says,
  without opening developer tools and without reading this package's source.

## Clarifications

Resolved during specification from the agreed feature statement, the package constitution and the
decisions recorded on the tracker. Rationale too long to carry here is in `decisions.md`.

### Session 2026-09-22

- **Q**: The roadmap puts the escape hatch to unnamed options in R3, where four chart types make the
  rule for a named attribute disagreeing with a passed option worth writing. Does the first chart
  type therefore ship without one?
  **A**: No. Article XIV makes reachability a standing property of every component, not a feature that
  arrives later, and this package supplies no appearance of its own by deliberate decision. A chart
  type with neither would be unstyleable, so pass-through ships here. What stays with R3 is the part
  that genuinely needs several types: one vocabulary across them, and a stated and tested rule for
  what happens when a named attribute and a passed option disagree. This feature names only the
  attributes carrying data, so it has no such disagreement to rule on. Integrated as FR-012 and
  SC-005.

- **Q**: The previous feature requires an accessible name and a text alternative on every region and
  reports their absence in place of the chart. This feature makes both optional. Which holds?
  **A**: This one. Putting a plain chart on a page with no surrounding markup is an ordinary request,
  and refusing to draw it is the package overruling the page. Both stay supported and the
  documentation makes the case for writing them, which is where a recommendation belongs. The id is
  different and stays required: the package invents none, and a generated one is stable only until a
  chart is added above it. Integrated as FR-008, FR-009 and FR-010.

- **Q**: Article XV says chart colour comes from the daisyUI semantic palette supplied by django-mvp,
  never a literal and never a hard-coded series palette. This feature writes no colour at all.
  **A**: The article is wrong and is being changed, recorded as issue #22. How a chart looks belongs
  to whoever writes the page, and matching it to the surrounding theme is not something this package
  attempts. The parts of Article XV this feature does hold to are rendered output as a tested
  contract and assertions made against that output rather than against class names. Integrated as
  FR-013 and FR-015.

- **Q**: A chart given values but no point labels has nothing to label its points with. Does it
  refuse, invent labels, or draw?
  **A**: It draws. Labels are a separate attribute and a chart of unlabelled points is a legitimate
  thing to want, so their absence is not a mistake to report. Numbering the points on the author's
  behalf would be the package inventing data. Integrated as FR-003.

- **Q**: Data given as text is refused. Is that refusal raised, or reported in the page?
  **A**: Reported in the page, in the space the chart would occupy, which is how the previous feature
  reports a missing library and an unresolved height. A raised error reads differently in development
  and in production and would be the third way this package reports the same class of problem.
  Integrated as FR-017 and FR-019.

- **Q**: Should a chart with no values say so, the way a chart region with no height does?
  **A**: No. A missing height is a page built wrongly and nothing on it will be right until it is
  fixed. A chart with no data is a page working correctly on a day when there is nothing to show, and
  what should stand in its place is a decision about that page. The chart draws whatever ECharts
  draws for an empty series. This follows the ruling already recorded on issue #15. Integrated as an
  edge case.

## Assumptions

- The chart component renders its own region. A template author writes one tag, not a region wrapped
  around a chart, because the plain chart with no surrounding markup is the common case and the
  package can do that wiring itself. The region component stays exactly as the previous feature built
  it, for a project drawing into a region itself.
- A heading, a caption or a card around a chart comes from django-mvp, which ships those already.
  This package supplies no chrome and takes no layout decisions.
- This feature draws one series. Several named series arrive with the next one, where data comes from
  a view.
- Values written in a template are literals a person typed. Dates, decimals and missing values are
  the next feature's subject, because they are what a view produces rather than what anyone types.
- The demo project's charts section exists but is empty until a chart type does. This feature is what
  brings it into the navigation for the first time.
- A base template already loading the charting library and the package's own module is a precondition
  this feature inherits rather than restates.

## Out of Scope

Each of these belongs to a later feature or roadmap item, and none is deferred work owed by this one.

- Data reaching a chart from a view, the shapes a view produces, several named series, dates, times,
  decimals and missing values, and proving that content cannot break out of the page — the next
  feature under R2.
- Bar, pie and scatter, one attribute vocabulary across the four chart types, chart colour taken from
  the running theme, and the rule for a named attribute disagreeing with a passed option — R3.
- Named attributes for axes, legends and tooltips — R5.
- Number and date formatting — R6.
- A second charting library alongside ECharts — R7.
- Querying, aggregating or reshaping data, which stays the host project's job at every roadmap item.
