"""The demo project, which is where the component gets looked at as it lands.

It is tested for the same reason ``test_app.py`` tests the template directory:
everything here fails quietly. A Cotton component that cannot be resolved
renders as empty output, a Tailwind class the packaged stylesheet does not emit
does nothing, and a navigation entry whose URL will not resolve is dropped from
the sidebar. None of that raises, so none of it shows up anywhere except in a
browser.
"""

import ast
import json
import re
from pathlib import Path

import pytest
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse
from django.utils.html import escape

from demo.views import (
    ChartTypesView,
    conversion_rate,
    invoiced,
    orders_by_channel,
    signups,
    source_of,
)
from tests.urls import COLOURED_PATTERNS


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
    def test_page_is_served(self, client, db):
        assert client.get("/").status_code == 200

    def test_page_is_drawn_inside_the_application_shell(self, overview_page):
        assert "<aside" in overview_page
        assert 'aria-label="Main navigation"' in overview_page
        assert 'aria-label="Breadcrumbs"' in overview_page

    def test_page_shows_the_tag_that_places_it(self, overview_page):
        assert "&lt;c-chart" in overview_page

    def test_page_draws_the_chart_it_documents(self, overview_page):
        assert payloads(overview_page)


class TestSidebarMenu:
    def test_it_holds_exactly_the_pages_that_exist(self, sidebar_navigation):
        assert re.findall(r'href="([^"]*)"', sidebar_navigation) == [
            "/",
            "/chart-types/",
            "/options/",
        ]

    def test_no_section_is_drawn_with_nothing_under_it(self, overview_page):
        assert 'href="None"' not in overview_page


class TestDocumentationSurface:
    def test_the_display_template_is_the_packaged_one(self):
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
        assert "&lt;figure" in overview_page
        assert "id=&quot;revenue&quot;" in overview_page
        assert "data-mvp-chart-surface" in overview_page

    def test_the_html_is_prettified(self, overview_page):
        panes = re.findall(
            r"<pre[^>]*><code[^>]*>(.*?)</code></pre>", overview_page, re.S
        )
        # The rendered-HTML pane is the one showing the markup the component
        # produced, rather than the source panes showing what was written.
        rendered = [pane for pane in panes if "&lt;figure" in pane]
        assert len(rendered) == 1, "expected exactly one rendered-HTML pane"
        assert re.search(r"\n\s*&lt;/figure&gt;", rendered[0])


class TestChartTypesPage:
    def test_the_page_is_served(self, client, db):
        assert client.get(reverse("chart_types")).status_code == 200

    def test_it_draws_one_of_every_type_it_claims(self, chart_types_page):
        drawn = {options["series"][0]["type"] for options in payloads(chart_types_page)}
        assert drawn == {"line", "bar", "pie", "scatter"}

    def test_every_chart_shows_the_code_that_built_it(self, chart_types_page):
        for builder in ChartTypesView.builders.values():
            assert escape(source_of(builder)) in chart_types_page, (
                f"{builder.__name__} is not listed on the page it builds a chart for"
            )

    def test_every_chart_describes_its_own_caption(self, chart_types_page):
        pairs = re.findall(
            r'<figure id="([^"]+)".*?aria-describedby="([^"]+)"',
            chart_types_page,
            re.S,
        )
        assert len(pairs) >= 4
        assert all(described == f"{chart}-description" for chart, described in pairs)


class TestChartOptionsPage:
    def test_the_page_is_served(self, client, db):
        assert client.get(reverse("chart_options")).status_code == 200

    def test_both_listings_are_the_code_that_ran(self, chart_options_page):
        for builder in (conversion_rate, invoiced):
            assert escape(source_of(builder)) in chart_options_page, (
                f"{builder.__name__} is not listed on the page it builds a chart for"
            )

    def test_the_styled_chart_carries_options_no_attribute_names(
        self, chart_options_page
    ):
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


class TestAChartReachedFromThePage:
    def test_the_listing_is_the_builder_that_ran(self, chart_options_page):
        assert escape(source_of(signups)) in chart_options_page

    def test_the_listener_runs_on_the_page_it_is_shown_on(self, chart_options_page):
        listener = get_template("demo/signups_formatter.html").template.source.strip()
        assert listener in chart_options_page
        assert escape(listener) in chart_options_page


class TestPatternsBesideColour:
    @staticmethod
    def patterned(page):
        return [
            options
            for options in payloads(page)
            if options.get("aria", {}).get("enabled") is True
        ]

    def test_the_listing_is_the_builder_that_ran(self, chart_options_page):
        assert escape(source_of(orders_by_channel)) in chart_options_page

    def test_the_chart_turns_patterns_on_and_the_generated_description_off(
        self, chart_options_page
    ):
        (options,) = self.patterned(chart_options_page)
        assert options["aria"]["label"]["enabled"] is False
        assert options["aria"]["decal"]["show"] is True

    def test_the_chart_leaves_ECharts_choice_of_pattern_per_series_alone(
        self, chart_options_page
    ):
        (options,) = self.patterned(chart_options_page)
        assert "decals" not in options["aria"]["decal"]

    def test_the_chart_has_two_series(self, chart_options_page):
        (options,) = self.patterned(chart_options_page)
        assert [series["name"] for series in options["series"]] == [
            "Online",
            "In store",
        ]

    def test_its_placement_carries_a_name_and_a_description(self, chart_options_page):
        assert re.search(
            r'<figure id="orders-by-channel".*?role="img" aria-label="[^"]+"',
            chart_options_page,
            re.S,
        )
        assert re.search(
            r'<p id="orders-by-channel-description"[^>]*>\s*\S', chart_options_page
        )

    def test_every_other_chart_arrives_with_nothing_turned_on(
        self, overview_page, chart_types_page, chart_options_page
    ):
        others = [
            options
            for page in (overview_page, chart_types_page, chart_options_page)
            for options in payloads(page)
            if options not in self.patterned(page)
        ]
        assert others
        assert all(options["aria"] == {"enabled": False} for options in others)


class TestDocumentedExample:
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


class TestTheReadmeShowsThePatternedChart:
    @staticmethod
    def readme():
        return (Path(settings.BASE_DIR) / "README.md").read_text()

    def test_the_python_block_is_the_builder_the_demo_runs(self):
        blocks = [
            block
            for block in re.findall(r"```python\n(.*?)\n```", self.readme(), re.S)
            if "def orders_by_channel" in block
        ]
        assert len(blocks) == 1, "the README does not show orders_by_channel once"
        assert " ".join(blocks[0].split()) == " ".join(
            source_of(orders_by_channel).split()
        )

    def test_the_colour_example_is_the_call_the_browser_tests_measure(self):
        (fragment,) = [
            block
            for block in re.findall(r"```python\n(.*?)\n```", self.readme(), re.S)
            if block.startswith("aria_opts=")
        ]
        assert (
            ast.literal_eval(fragment.removeprefix("aria_opts=")) == COLOURED_PATTERNS
        )


class TestTheDemoLoadsTheLibraryItself:
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
        real_tags = re.findall(r"<script[^>]*mvp-charts\.js", chart_types_page)
        assert len(real_tags) == 1
