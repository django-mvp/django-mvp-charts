# Decisions — 001, a chart region and the library that draws into it

Rationale behind the specification that is too long to carry inside it, plus every ambiguity resolved
without asking the repository owner. The specification stands alone. This file records why it reads
the way it does.

## A region has no size of its own

**Decided**: the region expands to fill its wrapper, and the host project is responsible for giving
it a wrapper with a height. There is no default height, no minimum height, and no aspect ratio.

**Why**: this is the owner's ruling, and it is the right one for a package built on a layout system
the project already has. A default height is a number invented by a library and applied to every page
that forgets to choose, and it is wrong on most of them. It also removes the project's ability to make
a chart share a grid row with anything else.

**The consequence it creates, and the guard for it**: a box that fills its parent, placed in a parent
sized by its own content, resolves to nothing. That is the single most common way this design fails
in practice, and it fails invisibly: no error, no message, an empty area nobody can account for.
Which is precisely the outcome the roadmap item exists to prevent. So the zero-height case is treated
exactly like the missing library: the region says what is wrong, in the page, in words the reader can
act on. The guard is what makes a no-default-height design safe to ship, and the two are one decision
rather than two.

A fallback height was considered as the alternative guard and rejected. It would make the mistake
invisible again by rendering something plausible, and a chart at a size nobody chose is harder to
diagnose than an honest message, not easier.

## The development delivery is included, not injected

**Decided**: the package ships the means to load the library during development, and the project
includes it deliberately in its own base template. A region never loads a third-party script itself.

**Why**: two requirements pull against each other here. The roadmap item wants the library present
during development without a build pipeline. Article XII forbids a component injecting a script tag
pointing at a third-party origin on a reader's behalf, and states that installing this package gains a
project no external origin it did not already have.

Both hold if the choice belongs to the project rather than to the component. A project that wants the
quick path adds one line to its own template, which is a choice it made and can see. A project that
bundles the library omits that line. Nothing in the package reaches out on its own, nothing branches
on a setting, and a page carrying no regions loads nothing extra.

This also keeps the promise that no declaration is required either way. The included line is the
development delivery itself, not a statement about which delivery is in use. A region uses whatever
it finds in front of it and never asks which route it came by. The founding notes left this question
deliberately open until the first component existed. This is the first component, so it is settled
here.

## A missing library is not decided at first render

**Decided**: a region that finds no library does not report it immediately. It reports only once
waiting has stopped being a reasonable explanation.

**Why**: a bundle can load after the markup does, which is normal in a project doing nothing unusual.
A region that judged at its first instant would accuse correctly-configured projects of a fault they
do not have, and the resulting message would be worse than no message, because it would send someone
to fix something that is not broken. The requirement is therefore about the state the page settles
in, rather than the state it starts in.

The specification deliberately does not say how long a region waits or how it detects arrival. That is
implementation work, and naming a mechanism here would settle it before anyone has looked at the
options.

## Losing a height later is not a failure

**Decided**: the zero-height report covers a region that never had a usable height. A region that
rendered correctly and later loses its height, because a panel collapsed or a tab hid it, reports
nothing, and recovers when the space returns.

**Why**: the two states look identical when measured and mean opposite things. The first is a setup
mistake, and someone needs to be told. The second is the page working as designed, and telling anyone
about it would turn a normal interaction into a stream of false alarms. Without this distinction the
requirement to survive a collapsing panel and the requirement to report a collapsed region contradict
each other.

## The accessible name and text alternative start here

**Decided**: the region carries both, the template author supplies both, and a missing or empty value
is reported rather than filled in.

**Why**: Article XV requires them on every packaged component and forbids silently defaulting either
to the empty string. The region is the component being placed, so it is the component that carries
them. Deferring the obligation to the first chart type would mean changing the region's surface later
instead of extending it, and would ship an interim version of the package that cannot be used by
someone who cannot see it.

Reporting a missing value rather than accepting it is what the constitution's wording requires: a
silently empty name is the failure it names. It also puts the accessibility obligation in the same
category as the other two failures this feature handles, so there is one way a region says something
is wrong rather than three.

## Priority order

P1 is placing a region, because nothing else has a subject without it and it is the only part a
template author touches directly. P2 is getting the library to the browser, because a region with
nothing to draw into it is inert, though it is demonstrable on its own. P3 is the failure reporting,
which needs both of the above to exist before it has anything to report, and which is where this
feature pays back the risk its own sizing decision creates. P4 is surviving change, last because a
region has to exist and be fillable before it can be made to hold its shape.

Every story is independently demonstrable. P1 needs no charting library at all.

## What this feature does not settle

Named deliberately, so a later reader does not mistake silence for an oversight:

- Which charting library version the namespace claims to render against. The specification requires
  that a range is stated. Picking it is work for the implementation, when there is something to test
  it against.
- What an empty region looks like. It is a legitimate state for as long as this package ships no chart
  type, and it should read as deliberate rather than broken, but the specification does not prescribe
  its appearance.
- How a region is identified among its siblings. Independence is the requirement. The mechanism is
  implementation work.
