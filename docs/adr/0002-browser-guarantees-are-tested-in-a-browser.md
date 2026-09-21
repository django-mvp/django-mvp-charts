# ADR 0002 — Guarantees whose subject is the browser are tested in a browser, and skip where there is none

**Status:** accepted

## Decision

The behaviour that exists only in a running page — a region filling its wrapper, the wait for a
charting library, the height check, the resize contract — is tested with Playwright against real
pages, and measured rather than inspected.

Those tests skip where no browser is installed. That currently includes continuous integration, and
the gap is stated in the pull request and tracked as an issue rather than left to be discovered.

## Why

None of it can be reached from rendered output. A class name in markup says a rule was asked for,
never that it applied; the presence of a script tag says nothing about what it did. The package's
central promise is that a region ends up exactly the size of the element around it, and the only
honest evidence for that is a measured box.

The cost is a browser in the test environment. The shared test workflow already supports installing
one — it takes a single input — but this repository's workflow does not pass it, and this project's
automation does not write to `.github/workflows/**` at all, deliberately: a token that can rewrite
the workflows can disable the checks gating its own changes.

So the choice was between writing the tests now and having them run everywhere once one line lands,
or not writing them and leaving the behaviour unproven anywhere. The first is better, on one
condition: the gap has to be visible. A skipped browser test that reads as a pass is how this goes
wrong quietly, which is why the skip names its reason on every run.

An alternative was weighed and rejected: asserting the sizing from computed styles in a headless DOM
without layout. It reports the rule that was asked for, not the box that resulted, which is the
distinction this decision exists to keep.

## Revisit if

The workflow gains the line. The skip then becomes an error on CI rather than a skip, matching what
django-mvp already does, and a missing browser stops being an acceptable state anywhere.
