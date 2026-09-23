"""Shared fixtures for the test suite."""

import os

import pytest
from django import template as dj_template
from django.template import Context
from django.urls import reverse
from django_cotton.compiler_regex import CottonCompiler


@pytest.fixture(scope="session")
def chromium():
    """A working chromium, or a decision about what its absence means.

    Two of this package's guarantees exist only in a browser: that a chart is
    actually drawn from the options the server sent, and that it follows the
    size of its box. Neither can be asserted from rendered markup, so they are
    measured in a real one.

    On a contributor's machine a missing browser is a setup step nobody has
    run yet, and skipping says so without blocking unrelated work. On CI it is
    a hole in the suite: a checks page cannot tell a skipped test from a
    passing one, so these would report green while asserting nothing. There,
    the absence fails.
    """
    from playwright.sync_api import Error, sync_playwright

    try:
        with sync_playwright() as playwright:
            playwright.chromium.launch().close()
    except (Error, ImportError) as exc:  # pragma: no cover - environment probe
        unavailable = f"no chromium available to measure the page with: {exc}"
        if os.environ.get("CI"):
            pytest.fail(
                f"{unavailable}\n\nThe tests workflow installs chromium "
                "through the shared workflow's `install-playwright` input. "
                "Reaching this means that input was dropped or its install "
                "step did not run.",
                pytrace=False,
            )
        pytest.skip(unavailable)


@pytest.fixture(scope="session")
def render():
    """Compile a Cotton source string and render it.

    No request is involved. The component reads nothing off one, which is what
    lets it render anywhere a template does, including a page assembled
    outside the request cycle.
    """
    compiler = CottonCompiler()

    def render_source(source, **context):
        return dj_template.Template(compiler.process(source)).render(Context(context))

    return render_source


@pytest.fixture
def overview_page(client, db):
    """The demo project's overview page, rendered, as a string."""
    return client.get(reverse("overview")).content.decode()


@pytest.fixture
def chart_types_page(client, db):
    """The demo project's chart types page, rendered, as a string."""
    return client.get(reverse("chart_types")).content.decode()


@pytest.fixture
def chart_options_page(client, db):
    """The demo project's options page, rendered, as a string."""
    return client.get(reverse("chart_options")).content.decode()


@pytest.fixture
def sidebar_navigation(overview_page):
    """Just the sidebar's navigation list, cut out of the rendered page.

    Cut to the *matching* close rather than the first one. A section with
    pages under it nests a list inside the outer one, so stopping at the first
    ``</ul>`` silently returns the navigation up to the first section and
    drops everything after it — which would make an assertion about what the
    sidebar holds pass by not looking at most of it.
    """
    start = overview_page.index('aria-label="Main navigation"')
    start = overview_page.rindex("<ul", 0, start)
    depth, cursor = 0, start
    while True:
        opened = overview_page.find("<ul", cursor)
        closed = overview_page.index("</ul>", cursor)
        if opened != -1 and opened < closed:
            depth += 1
            cursor = opened + 3
            continue
        depth -= 1
        cursor = closed + len("</ul>")
        if depth == 0:
            return overview_page[start:cursor]
