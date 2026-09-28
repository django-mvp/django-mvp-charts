"""Shared fixtures for the test suite."""

import os

import pytest
from django import template as dj_template
from django.template import Context
from django.urls import reverse
from django_cotton.compiler_regex import CottonCompiler


@pytest.fixture(scope="session")
def chromium():
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
    compiler = CottonCompiler()

    def render_source(source, **context):
        return dj_template.Template(compiler.process(source)).render(Context(context))

    return render_source


@pytest.fixture
def overview_page(client, db):
    return client.get(reverse("overview")).content.decode()


@pytest.fixture
def chart_types_page(client, db):
    return client.get(reverse("chart_types")).content.decode()


@pytest.fixture
def chart_options_page(client, db):
    return client.get(reverse("chart_options")).content.decode()


@pytest.fixture
def sidebar_navigation(overview_page):
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
