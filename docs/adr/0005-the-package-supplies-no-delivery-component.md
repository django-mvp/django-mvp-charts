# ADR 0005 — The package supplies no delivery component, and names no version, hash or origin

**Status:** accepted
**Amends:** [ADR 0003](0003-window-echarts-is-the-delivery-contract.md)

## Decision

`<c-echarts.cdn />` is removed, with the template tag behind it and the pinned version, integrity
hash and CDN URL it carried. `mvp_charts.versions` keeps one constant: the range of ECharts versions
the `echarts` namespace is known to render against.

The project writes its own script tag for the charting library, as it already writes one for this
package's module. The documentation shows a tag worth copying and says what makes it safe.

The package now has no template tag library at all, and no shipped template names a remote origin —
asserted over every template in the distribution, with no exception for any of them.

## Why

ADR 0003 settled that `window.echarts` is the whole contract and that nothing declares which route
supplied it. The delivery component was the development half of that: one line a project placed in
its own base template, rendering a script tag this package had pinned and hashed.

The owner's ruling, extending the one recorded in ADR 0004: a project that supplies its own script
tags supplies this one too.

**A component wrapping a URL and a hash is not something a developer needs written for them.** It
renders four attributes. The documentation has to explain all four anyway, because a project that
bundles ECharts needs to know what it is replacing.

**Holding the version and the hash made this package a party to a decision it does not take.** A
project pinning a different version, serving ECharts from its own origin, or running it from a
bundle got nothing from the component and could not change what it rendered. The only projects it
fitted were the ones that wanted exactly the version this package happened to have pinned — and
keeping that pin current, re-hashing it on every bump, was upkeep paid for by a package that ships
no JavaScript.

**It was also the one hole in Article XII.** "No shipped template names a remote origin" had to be
written as "no shipped template except this one", and a rule with an exception is a rule that has to
be re-argued every time something new is added. It is now unconditional.

**What this costs.** A developer setting up for the first time copies four attributes out of the
README instead of writing one tag. That is the cost, it is paid once, and what they get for it is a
line they can read, move, re-pin or replace.

## Revisit if

Nothing foreseeable. A second backend states its own supported range beside this one and supplies no
delivery component either.
