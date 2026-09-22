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
