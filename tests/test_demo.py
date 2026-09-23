"""The demo project, which is where the component gets looked at as it lands.

It is tested for the same reason ``test_app.py`` tests the template directory:
everything here fails quietly. A Cotton component that cannot be resolved
renders as empty output, a Tailwind class the packaged stylesheet does not emit
does nothing, and a navigation entry whose URL will not resolve is dropped from
the sidebar. None of that raises, so none of it shows up anywhere except in a
browser.
"""

import json
import re
from pathlib import Path

import pytest
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse


def payloads(page):
    """Every options script on the page, parsed back."""
    return [
        json.loads(script)
        for script in re.findall(
            r'<script type="application/json" data-mvp-chart-options>(.*?)</script>',
            page,
            re.S,
        )
    ]


class TestOverviewPage:
    """The page a reader lands on, and the shell it is drawn inside."""

    def test_page_is_served(self, client, db):
        assert client.get("/").status_code == 200

    def test_page_is_drawn_inside_the_application_shell(self, overview_page):
        """The sidebar and the header, not a hand-rolled document.

        The breadcrumb trail is the header's, drawn from what the view
        declares, so its presence says the header is there and reading the
        page rather than merely that some markup rendered.
        """
        assert "<aside" in overview_page
        assert 'aria-label="Main navigation"' in overview_page
        assert 'aria-label="Breadcrumbs"' in overview_page
        assert '<span class="mvp-breadcrumb-text">Overview</span>' in overview_page

    def test_title_names_the_page_and_the_site(self, overview_page):
        title = re.search(r"<title>(.*?)</title>", overview_page, re.S).group(1)
        assert " ".join(title.split()) == "Overview | django-mvp-charts"

    def test_page_heading_is_the_page_title(self, overview_page):
        assert re.search(r"<h1[^>]*>\s*Overview\s*</h1>", overview_page)

    def test_page_shows_the_view_code_that_builds_a_chart(self, overview_page):
        """The half of the story that is not in the template.

        The whole point of the design this page documents is that a chart is
        built in Python, so a page showing only the tag would describe half an
        API.
        """
        assert "from pyecharts.charts import Line" in overview_page
        assert "get_context_data" in overview_page

    def test_page_shows_the_tag_that_places_it(self, overview_page):
        assert "&lt;c-chart" in overview_page

    def test_page_draws_the_chart_it_documents(self, overview_page):
        assert payloads(overview_page)


class TestSidebarMenu:
    """What the navigation holds, which is exactly the pages that exist."""

    def test_it_holds_exactly_the_pages_that_exist(self, sidebar_navigation):
        """The list below is the one place that says what the navigation holds.

        A page added without a thought about where it belongs stops here.
        """
        assert re.findall(r'href="([^"]*)"', sidebar_navigation) == [
            "/",
            "/chart-types/",
            "/options/",
        ]

    def test_no_section_is_drawn_with_nothing_under_it(self, overview_page):
        """A container added before it has children renders as a dead control.

        django-mvp draws a navigation node from its leaf template until it has
        children, so a section declared while its page list is empty reaches
        the page as a button carrying ``href="None"``.
        """
        assert 'href="None"' not in overview_page


class TestDocumentationSurface:
    """``{% show_code %}`` and the template it renders its examples through."""

    def test_the_display_template_is_the_packaged_one(self):
        """django-mvp ships the surface alongside the tag from 0.24.0.

        This project supplied its own while the package had none. What is
        checked now is that it no longer does: ``demo`` comes first in
        ``INSTALLED_APPS``, so a file of that name under ``demo/templates/``
        would shadow the packaged surface and leave the demo showing an older
        one after every other project had moved on.
        """
        try:
            origin = get_template("cotton/documentation.html").origin.name
        except TemplateDoesNotExist:  # pragma: no cover - the failure message
            pytest.fail(
                "cotton/documentation.html is missing, so {% show_code %} "
                "raises instead of rendering"
            )
        assert "/demo/templates/" not in Path(origin).as_posix(), (
            f"{{% show_code %}} is rendering through {origin}, which shadows "
            "the one django-mvp ships"
        )

    def test_the_example_shows_its_cotton_source(self, overview_page):
        assert "&lt;c-chart :chart=&quot;revenue&quot;" in overview_page

    def test_the_example_shows_the_html_it_rendered_to(self, overview_page):
        """Attributes come back alphabetised, which is the prettifier's doing."""
        assert "&lt;figure" in overview_page
        assert "id=&quot;revenue&quot;" in overview_page
        assert "data-mvp-chart-surface" in overview_page

    def test_the_html_is_prettified(self, overview_page):
        """The tag falls back to raw output when BeautifulSoup is absent.

        It does so silently, and raw Cotton output already carries line breaks
        and indentation of its own, so neither of those tells the two apart.
        What does is that the prettifier puts every closing tag on a line of
        its own, where the raw output keeps ``<span>text</span>`` inline.
        """
        panes = re.findall(
            r"<pre[^>]*><code[^>]*>(.*?)</code></pre>", overview_page, re.S
        )
        # The rendered-HTML pane is the one showing the markup the component
        # produced, rather than the source panes showing what was written.
        rendered = [pane for pane in panes if "&lt;figure" in pane]
        assert len(rendered) == 1, "expected exactly one rendered-HTML pane"
        assert re.search(r"\n\s*&lt;/figure&gt;", rendered[0])


class TestChartTypesPage:
    """One component placing four chart types, each built in the view."""

    def test_the_page_is_served(self, client, db):
        assert client.get(reverse("chart_types")).status_code == 200

    def test_it_draws_one_of_every_type_it_claims(self, chart_types_page):
        """Read off the payloads rather than the prose, which can say anything."""
        drawn = {options["series"][0]["type"] for options in payloads(chart_types_page)}
        assert drawn == {"line", "bar", "pie", "scatter"}

    def test_every_chart_describes_its_own_caption(self, chart_types_page):
        """Four distinct ids prove nothing on their own.

        The failure this guards against is two charts on a page pointing at
        one caption, which counts the same and reads wrong to anyone using a
        screen reader.
        """
        pairs = re.findall(
            r'<figure id="([^"]+)".*?aria-describedby="([^"]+)"',
            chart_types_page,
            re.S,
        )
        assert len(pairs) >= 4
        assert all(described == f"{chart}-description" for chart, described in pairs)

    def test_the_charts_that_take_their_height_from_a_wrapper_have_one(
        self, chart_types_page
    ):
        """The sizing mode this page demonstrates, asserted rather than described.

        Three charts here carry no height and fill a sized element instead. A
        wrapper that lost its height would leave them invisible, with nothing
        raising anywhere.
        """
        wrappers = re.findall(
            r'<div class="[^"]*border[^"]*" style="height: 300px">\s*<figure',
            chart_types_page,
        )
        assert len(wrappers) == 3


class TestChartOptionsPage:
    """Every ECharts option reached in Python, and the awkward types."""

    def test_the_page_is_served(self, client, db):
        assert client.get(reverse("chart_options")).status_code == 200

    def test_the_styled_chart_carries_options_no_attribute_names(
        self, chart_options_page
    ):
        """The claim the page makes, read back off what it actually sent."""
        styled = next(
            options for options in payloads(chart_options_page) if "title" in options
        )
        assert styled["title"][0]["text"] == "Conversion rate"
        assert styled["toolbox"]["show"] is True
        assert styled["tooltip"]["trigger"] == "axis"
        assert styled["series"][0]["lineStyle"]["color"] == "#7c3aed"

    def test_dates_decimals_and_a_gap_all_survive(self, chart_options_page):
        invoiced = next(
            options
            for options in payloads(chart_options_page)
            if options["series"][0]["name"] == "Invoiced"
        )
        assert invoiced["series"][0]["data"] == [
            ["2026-01-01", 1420.5],
            ["2026-02-01", None],
            ["2026-03-01", 1683.75],
        ]


class TestDocumentedExample:
    """The README's example is the markup the demo actually renders.

    A documented example is only worth anything if it is exercised, so the
    README's placement example has a counterpart on the overview page, and the
    demo page rendering is what proves it works. Comparing them here is what
    stops the two drifting apart silently, which is the usual way a README
    example stops being true.
    """

    @staticmethod
    def readme_example(anchor):
        readme = (Path(settings.BASE_DIR) / "README.md").read_text()
        for block in re.findall(r"```html\n(.*?)\n```", readme, re.S):
            if anchor in block:
                return " ".join(block.split())
        return None

    @staticmethod
    def overview_template():
        return " ".join(
            (Path(settings.BASE_DIR) / "demo/templates/demo/overview.html")
            .read_text()
            .split()
        )

    def test_the_placement_example_is_the_one_the_demo_shows(self):
        example = self.readme_example('id="revenue"')
        assert example, "the README no longer carries the placement example"
        assert example in self.overview_template()


class TestTheDemoLoadsTheLibraryItself:
    """The project places the delivery; no component reaches off-site for it."""

    def test_every_page_carries_the_delivery_the_project_placed(
        self, overview_page, chart_types_page, chart_options_page
    ):
        for page in (overview_page, chart_types_page, chart_options_page):
            assert page.count("cdn.jsdelivr.net/npm/echarts@") == 1

    def test_it_is_pinned_and_integrity_checked(self, chart_types_page):
        script = re.search(r"<script[^>]*jsdelivr[^>]*>", chart_types_page).group(0)
        assert 'integrity="sha384-' in script
        assert 'crossorigin="anonymous"' in script

    def test_the_package_module_is_loaded_once_beside_it(self, chart_types_page):
        """Four charts on the page, one module."""
        real_tags = re.findall(r"<script[^>]*mvp-charts\.js", chart_types_page)
        assert len(real_tags) == 1
