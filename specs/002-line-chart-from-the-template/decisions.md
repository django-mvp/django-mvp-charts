# Decisions — 002, a line chart drawn from values written in the template

Rationale behind the specification that is too long to carry inside it, plus every ambiguity resolved
without asking the repository owner. The specification stands alone. This file records why it reads
the way it does.

## The chart renders its own region, and the author writes one tag

**Decided**: `<c-echarts.line>` is a complete chart. It draws into a region it renders itself, and a
template author never has to place a region around it.

**Why**: the plain chart is the common case. A page that wants a chart and nothing else should cost
one tag, and making the author write a region, name it and then point a chart at it is plumbing the
package can do. The region component stays exactly where the previous feature left it, unchanged, for
a project that wants to draw into a region itself.

**The alternative, and why it lost**: the region could have grown a slot, so an author writes a
heading, the chart and a footnote inside one region. It reads well in a template and it puts a chart's
title next to the chart. The cost is that the region stops being the sized drawing area and becomes a
small card: the drawing surface needs its own height again, which is the blank-rectangle failure the
previous feature exists to prevent, and the package starts owning a piece of layout that django-mvp
already ships a card and a heading for. A package that supplies no chrome has one fewer thing to
disagree with the project about.

## Pass-through ships with the first chart type, not with the fourth

**Decided**: options this component does not name are written on the tag and reach ECharts untouched,
in this feature rather than in R3.

**Why**: the roadmap puts the escape hatch in R3 because the rule for a named attribute disagreeing
with a passed option can only be written honestly against several chart types. That reasoning is about
the *rule*, not about reachability. Article XIV makes reachability a standing property of every
component in the package, and this feature names only the attributes that carry data, so there is no
disagreement for it to rule on: nothing the component names and nothing an author passes can collide.

**What made it unavoidable rather than merely tidy**: the package writes no appearance of its own, by
deliberate decision. A chart type shipped with no named appearance attributes and no way to reach
ECharts' own options would be a chart nobody could style at all. The two decisions only work
together, and shipping the first without the second would be shipping a chart that cannot be made to
look like anything.

**What stays with R3**: one vocabulary across four chart types, and the stated and tested rule for a
named attribute and a passed option disagreeing. Both need the fourth type to be worth writing.

## A name and a text alternative stop being a condition of rendering

**Decided**: a chart draws with neither. The previous feature's requirement that their absence is
reported in place of the region no longer holds. The id is untouched and stays required.

**Why**: this is the owner's ruling. Putting a plain chart on a page with no surrounding markup is a
frequent and reasonable thing to want, and a package that refuses to draw one is overruling the page
about the page's own content. Neither value is something the package can supply: only the author
knows what the chart is called and what it shows, so the choice was never between a good name and a
bad one, it was between a chart and no chart.

**What is lost, and where it goes**: a chart drawn into a canvas is invisible to assistive technology
and to anyone who cannot distinguish the colours, and without a name and a description there is
nothing else for them to read. That case does not disappear because the requirement did. It moves to
the documentation, which states plainly what omitting them costs, so a page that omits them does so
knowingly. A recommendation that can be argued for is worth more here than a refusal that can only be
worked around.

**Why the id is different**: the package generates no id, and one generated per request is stable only
until a chart is added above it. There is nothing to fall back to, so its absence is still reported.

## The package contributes no appearance at all

**Decided**: no colour, no line width, no marker size or visibility rule, no legend rule, no grid or
axis line decision, no animation setting, no typeface. A chart with no options looks the way ECharts
draws that data.

**Why**: this is the owner's ruling, and it follows the two already recorded on the tracker — a pie
chart drawing its slices in the order given rather than sorted, and a chart with no data drawing
whatever ECharts draws rather than a sentence this package wrote. The asymmetry is the argument. A
default this package leaves out costs an author one line restoring it. A default this package applies
cannot be undone from a template at all, because by the time the component holds the data the
original is gone.

**The collision this creates**: Article XV says chart colour comes from the daisyUI semantic palette
supplied by django-mvp, never a literal value and never a hard-coded series palette. This feature
contradicts it directly. The article is being changed rather than the feature, recorded as issue #22.
Deriving a palette from the running theme costs a colour-space implementation, something watching for
a theme change and a repaint path, and it makes this package responsible for a guarantee no charting
library offers.

## Data is a Python value, and writing it as text is not reported

**Decided**: an attribute carrying data takes a Python value. The package never reads data out of
text, and it says nothing when someone writes text anyway. The documentation covers it.

**Why parsing lost**: splitting a string on commas means deciding what a comma inside a label means,
what an empty item is, and which strings look enough like numbers to become them. Every one of those
is a decision nobody asked for, made silently, and wrong at the edges. Python already has a list and
the template layer already passes one.

**Why it is not reported**: this was specified as a fourth story, with a message in the page naming
what to write instead, and the owner removed it. A developer who writes the attribute wrongly finds
out when the chart does not work, and this package does not exist to cover every mistake someone
could make with it. Hand-holding has a cost that is easy to miss: every guard is a behaviour to
specify, test, translate and keep true, and it competes with the chart types the package is actually
for.

**The line it draws, which is worth keeping**: the two failures the previous feature reports are
conditions a correct template can still meet. A project can load the library in a way that does not
arrive, and a wrapper's height can resolve to nothing without anyone writing anything wrong. Those
earn a message. A misspelled attribute does not, and neither will the next twenty ways a template can
be wrong.

## A chart with no data says nothing

**Decided**: it draws whatever ECharts draws for an empty series. No message, no placeholder, no
attribute for wording.

**Why**: this follows the ruling recorded on issue #15. A missing height is a page built wrongly and
nothing on it will be right until it is fixed, which is why that one is reported. A chart with no
data is a page working correctly on a day when there is nothing to show. Whether that should be an
empty chart, a sentence, a link or no chart at all is a decision about one page, and a page that
wants its own answer writes it around the tag or does not render the tag.

---

# Planning decisions

Recorded while the plan was written. Each one carries the verdict on whether it graduates to an
architecture decision record.

## D1 — the options script points at the region, not the region at the script

**Decided**: the line component renders `json_script` carrying
`data-mvp-echarts-options-for="<region id>"`, and the drawing module finds its work by querying for
that attribute. `region.html` gains nothing and changes nothing for this.

**Why**: the region is the one component that deliberately knows nothing about chart types, and a
second backend would otherwise have to agree with ECharts about an attribute name on it. Pointing
the other way also makes the relationship readable in the rendered output, where an id convention
would leave it invisible from both ends.

**ADR:** none — it is a wiring choice inside one namespace, and nothing downstream inherits it.

## D2 — the drawing module owns nothing the region already owns

**Decided**: `echarts-chart.js` subscribes to `mvp-chart-region:state` and
`mvp-chart-region:resize`. It runs no library poll, no height check and no resize observer of its
own.

**Why**: the previous feature shipped those two events describing itself as "the contract being
designed before there is a consumer for it". A second copy of the waiting logic would be a second
thing to keep in step, and the two would disagree the first time either changed.

**ADR:** none — it applies the rule ADR 0001 already set for the browser module.

## D3 — the built options object is compared whole, not checked for absences

**Decided**: the test for "no appearance decision from this package" asserts the entire options
object equals the dictionary a person would write by hand, rather than asserting that a list of
appearance keys is absent.

**Why**: an absence list only catches the keys somebody thought to list, and the failure mode being
guarded against is a key nobody meant to add. A whole-object comparison is also the only honest
reading of the requirement that a chart drawn through this package asks ECharts for the same thing
as one drawn directly.

**ADR:** none — a testing choice local to this feature.

## D4 — the design review's two findings, and what they changed

**Decided**: both accepted, both applied as plan edits before any code was written.

**The package reports nothing when data is written as text.** The plan carried a refusal over from
the sketch branch, where writing `values="12,14,15"` raised with a message naming the fix. The
specification's clarifications had already removed exactly that guard, and the edge case for values
that are not numbers says this feature passes what it was given and the outcome is ECharts'. A
string now travels into the options object as it arrived and the chart does not draw. What survives
from the sketch is only the rule that the package never reads data out of text.

**Every new Python module gets the test module that mirrors its path.** This feature is the first
to put Python under `mvp_charts/`, so `tests/test_echarts/test_options.py` and
`tests/test_templatetags/test_mvp_charts.py` are new. `pyproject.toml`'s non-mirror declaration
covers `tests/test_components/`, whose subject is the Cotton templates, and it stays exactly as it
is — Article X calls declaring a path whose subject is a Python module a review failure, and
leaning on that declaration to skip unit tests for a real module would have been one.

**ADR:** none — the first is an application of a ruling already in the specification, and the second
applies Article X as written.

## D5 — the payload's escaping is reproduced, not called through `json_script`

**Decided**: `EChartsChart` builds its payload with `json.dumps(..., cls=DjangoJSONEncoder).translate(...)`,
using the same three escapes `django.utils.html.json_script` applies (`<`, `>`, `&`), rather than
calling `json_script` itself.

**Why**: D1 fixed the markup as a `<script>` tag carrying `data-mvp-echarts-options-for` alongside
its `id` and `type`. `json_script` renders the whole tag from a fixed template with no way to add an
attribute, so producing that exact markup means building the tag in `line.html` and handing it only
the escaped JSON. The three sequences it escapes are documented Django behaviour, not a private
implementation detail, so reproducing them is a small, stable duplication rather than a coupling to
something that could change under this package unannounced.

**Revisit if**: Django adds a public, attribute-carrying variant of `json_script` — at which point
calling through directly removes the duplication.

**ADR:** none — a wiring choice inside one namespace, in the spirit of D1.

## D6 — scenario 4 (a chart beside a bare region) is shown on the demo's own line page

**Decided**: `demo/templates/demo/line.html` carries a second example, a line chart next to a bare
`<c-echarts.region>`, rather than a dedicated probe page under `tests/templates/probe/`.

**Why**: T007 needs a page carrying both a line chart and a bare region to demonstrate acceptance
scenario 4 (neither reads nor changes the other's state) in a browser. The probe pages under
`tests/` exist for situations no page a reader would visit should have to contort itself into
(no charting library, one delivery route); a chart beside an empty region is not that — it is an
ordinary page a project might actually build, so it belongs in the demo rather than behind a
test-only route, and it costs the reader nothing extra: the section is two examples on one page
they were already going to visit.

**Revisit if**: a later story needs its own dedicated probe for chart/region independence under
conditions the demo page cannot represent (e.g. a specific failure state).

**ADR:** none — a demo-content choice local to this task.

## D7 — the FR-010 test-replacement exception covered seven test methods and one fixture, not two

**Decided**: US2's brief authorised replacing "the two assertions in `test_region.py` that state the
superseded behaviour." Implementing T010 correctly required replacing seven pre-existing test
methods there (`test_missing_name_names_it_and_renders_no_region`,
`test_missing_description_names_it_and_renders_no_region`,
`test_empty_string_name_is_treated_as_missing`, `test_empty_string_description_is_treated_as_missing`,
`test_all_three_missing_names_all_three`, and `TestTranslatedMessages`'s two tests), plus repointing
the `tests/locale/de` fixture catalog from the removed "has no name" string to the surviving "has no
id" one.

**Why**: `<c-vars id="" name="" description="" />` gives every attribute the caller does not pass the
same empty default as one passed `=""` — the component cannot tell "missing" from "empty" apart, which
this same file's own design note under FR-009 already records. Once the missing-name and
missing-description branches leave `region.html`, every pre-existing assertion that exercised either
state — whichever of the two ways it was spelled — asserted the identical superseded behaviour: an
alert appears and no figure renders. Replacing only two of them would have left five failing tests in
a file with an explicit, narrow, two-assertion exception; leaving the tree red was not an option either.
Each replacement touches only the name/description assertions in its test, states the new rule, and
names FR-010 in its own words, exactly as the exception's replacement was worded to require.

**ADR:** none — a scope clarification of an exception already granted for this task, not a new design
decision.

## D8 — the demo's region page and two of its tests are left broken by FR-010, not fixed here

**Decided**: T010's `region.html` change breaks three pre-existing tests outside `test_region.py`:
`tests/test_demo.py::TestChartRegionPage::test_it_shows_seven_independent_regions`,
`tests/test_demo.py::TestTheStatesAreShownOnThatPage::test_it_shows_the_missing_attribute_state`, and
`tests/test_components/test_region_e2e.py::TestTheReportingRegionIsExcludedOnPurpose::test_the_page_carries_one_region_reporting_no_height`.
None is touched.

**Why**: `demo/templates/demo/chart_region.html`'s "No description" example
(`id="open-tickets-no-description"`) exists to demonstrate FS-001's missing-description alert, and its
wrapper (`<div class="mt-3">`) was never given a height, because a region that never rendered had no
height to need. FR-010 makes that region render for the first time, into a wrapper with no height, so
it now reports its own `no-height` state — collateral, not deliberate: the demo page no longer has
anything true to say about a missing description, and its wrapper needs a real height regardless.
Fixing this means rewriting that page's "When it cannot draw" section and the two test files, none of
which is `test_region.py`, `region.html`, the line demo page, README or CHANGELOG — the brief's US2
scope names none of them, and "do not work outside T009, T010 and T011" is explicit. Reported to Forge
as a concern rather than fixed under this story's authorisation.

**Revisit if**: Forge schedules the follow-up — likely replacing the "No description" example with one
showing an unnamed, undescribed chart drawing correctly (mirroring T011's line-page addition), with a
resolved height on its wrapper, and updating both tests to match.

**ADR:** none — a same-repository follow-up, not an architecture decision.

## D9 — the demo's superseded failing state is replaced by the one that survived, not removed

**Decided**: D8's three broken tests are closed at their source. `demo/templates/demo/chart_region.html`
loses the "No description" example and gains a "No id" one — a region given a name and a description
and no id, in the same slot, with the same prose shape. `tests/test_demo.py` follows: the state test
now asserts the missing-id alert, and the region-count test keeps its count and gets a docstring that
says what the six regions now are.

**Why**: FR-010 removed one of the three states that section demonstrates and left the other two
untouched, so the section's claim — every state a region can be in is shown, not described — became
false in exactly one slot. Dropping the slot would have left the surviving required attribute
undemonstrated on the page that exists to demonstrate it; the id is still the author's to give and a
region missing one is still reported, and that is now the only attribute of which either is true.
Putting an unnamed, undescribed chart there instead, as D8 anticipated, would have shown a working
chart inside a section about charts that cannot draw, and T011 already shows that chart on the line
page where it belongs. The e2e failure needed no separate fix: it timed out because the superseded
example rendered a region into a wrapper with no height, and it passes once that example is gone.

**ADR:** none — documentation collateral of a requirement already specified, nothing downstream
inherits it.

## D10 — T013's file list names the merge; carrying it to the tag and the component is read as included

**Decided**: T013 in `tasks.md` names `mvp_charts/echarts/options.py`, the README and the CHANGELOG.
It does not separately list `mvp_charts/templatetags/mvp_charts.py` or
`mvp_charts/templates/cotton/echarts/line.html`, both of which T013's own commit also touches: the
tag gained an `options` parameter and calls `Merge` when it is given; the component gained an
`options=""` c-var and passes it to the tag.

**Why**: T012's given/when/then is explicit that "an `options` attribute written on the tag" reaches
ECharts, and T012's tests (`TestOptionsAttribute` in `test_line.py`, the new browser assertion in
`test_line_e2e.py`) exercise exactly that path — through the rendered tag, not through `Merge` called
directly. A merge that exists in `options.py` but is never invoked from the tag would leave every one
of those tests red, which is that a merge object built and never wired in is not what T012 or the
acceptance scenarios describe. T012a already covers `Merge` in isolation; T013 is where it is asked
to do the work FR-012 names. Both files stayed inside the two-line change the wiring needed — a new
parameter and a conditional call in the tag, a new c-var and one more `=` in the template — no
appearance decision, no unrelated edit to either file.

**ADR:** none — plumbing implied by the story's own acceptance criteria, not an architecture
decision.
