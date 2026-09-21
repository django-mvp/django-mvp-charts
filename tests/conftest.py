"""Shared fixtures for the test suite."""

import pytest
from django.urls import reverse


@pytest.fixture
def overview_page(client, db):
    """The demo project's overview page, rendered, as a string."""
    return client.get(reverse("overview")).content.decode()


@pytest.fixture
def sidebar_navigation(overview_page):
    """Just the sidebar's navigation list, cut out of the rendered page."""
    start = overview_page.index('aria-label="Main navigation"')
    return overview_page[start : overview_page.index("</ul>", start)]
