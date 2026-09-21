"""Shared fixtures for the test suite."""

import pytest
from django.urls import reverse


@pytest.fixture(scope="session")
def chromium_or_skip():
    """Skip rather than fail where no browser is installed.

    Three of this feature's guarantees exist only in a browser: whether the
    charting library arrived, whether the wrapper resolved to a usable height,
    and what size that wrapper is now. None can be asserted from rendered
    markup, so they are measured in a real one.

    Installing that browser on CI is a line in a workflow file, which is
    outside what this project's automation may change. Until it is added these
    tests skip there and run locally, and a skip says so out loud where a
    missing test would not.
    """
    from playwright.sync_api import Error, sync_playwright

    try:
        with sync_playwright() as playwright:
            playwright.chromium.launch().close()
    except (Error, ImportError) as exc:  # pragma: no cover - environment probe
        pytest.skip(f"no chromium available to measure the page with: {exc}")


@pytest.fixture
def overview_page(client, db):
    """The demo project's overview page, rendered, as a string."""
    return client.get(reverse("overview")).content.decode()


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


@pytest.fixture
def chart_region_page(client, db):
    """The demo project's chart region page, rendered, as a string."""
    return client.get(reverse("chart_region")).content.decode()
