"""Shared fixtures for the test suite."""

import pytest
from django.urls import reverse


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
