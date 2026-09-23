"""Tests for `<c-chart>`, the rendered-output contract.

Compiles Cotton source directly, so this file covers what the component sends
to the browser: the figure, the accessible name and text alternative, the
sizing, and the options payload. ``test_chart_e2e.py`` covers what only a real
browser can measure.
"""

import json
import re
from datetime import date
from decimal import Decimal

import pytest
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, Scatter

A_CHART = (
    '<c-chart :chart="chart" id="revenue" name="Revenue" description="By month." />'
)


@pytest.fixture
def line():
    return Line().add_xaxis(["Jan", "Feb", "Mar"]).add_yaxis("Revenue", [12, 14, 15])


def payload(html):
    """The JSON the options script carries, parsed back."""
    script = re.search(
        r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.S
    )
    assert script is not None, "no options script in the rendered output"
    return json.loads(script.group(1))


class TestTheFigure:
    """What the component renders around the chart."""

    def test_the_figure_carries_the_id_it_was_given(self, render, line):
        assert '<figure id="revenue"' in render(A_CHART, chart=line)

    def test_the_drawing_surface_is_marked_for_the_browser_module(self, render, line):
        html = render(A_CHART, chart=line)
        assert "data-mvp-chart-surface" in html

    def test_the_name_is_the_surfaces_accessible_name(self, render, line):
        html = render(A_CHART, chart=line)
        assert 'role="img"' in html
        assert 'aria-label="Revenue"' in html

    def test_the_description_is_a_caption_the_surface_points_at(self, render, line):
        html = render(A_CHART, chart=line)
        assert 'aria-describedby="revenue-description"' in html
        assert '<figcaption id="revenue-description"' in html
        assert "By month." in html

    def test_a_chart_given_no_name_renders_without_the_attribute(self, render, line):
        """Not with an empty one, which a screen reader announces as nameless."""
        html = render('<c-chart :chart="chart" id="revenue" />', chart=line)
        assert "<figure" in html
        assert "aria-label" not in html
        assert 'role="img"' not in html

    def test_a_chart_given_no_description_renders_without_a_caption(self, render, line):
        html = render('<c-chart :chart="chart" id="revenue" />', chart=line)
        assert "<figure" in html
        assert "figcaption" not in html
        assert "aria-describedby" not in html


class TestSizing:
    """A height, a ratio, or the element around it. The package invents none."""

    def test_a_height_on_the_tag_is_carried_by_the_figure(self, render, line):
        html = render(
            '<c-chart :chart="chart" id="revenue" height="320px" />', chart=line
        )
        assert 'style="height: 320px"' in html

    def test_without_one_the_figure_fills_the_element_around_it(self, render, line):
        html = render('<c-chart :chart="chart" id="revenue" />', chart=line)
        assert "style=" not in html
        assert "h-full" in html

    def test_no_size_of_any_kind_is_invented(self, render, line):
        """A chart given no size attribute gets none from here."""
        html = render('<c-chart :chart="chart" id="revenue" />', chart=line)
        assert "min-height" not in html
        assert "aspect-" not in html

    def test_a_ratio_on_the_tag_is_carried_by_the_figure(self, render, line):
        html = render(
            '<c-chart :chart="chart" id="revenue" aspect-ratio="2" />', chart=line
        )
        assert 'style="aspect-ratio: calc(2)"' in html

    def test_a_ratio_is_written_as_the_fraction_it_is(self, render, line):
        """`calc()` is what makes `16/9` a number rather than two of them."""
        html = render(
            '<c-chart :chart="chart" id="revenue" aspect-ratio="16/9" />', chart=line
        )
        assert 'style="aspect-ratio: calc(16/9)"' in html

    def test_a_figure_with_a_ratio_is_not_also_told_to_fill_its_parent(
        self, render, line
    ):
        """`h-full` would hand it a height, and the ratio would have nothing to say."""
        html = render(
            '<c-chart :chart="chart" id="revenue" aspect-ratio="2" />', chart=line
        )
        assert "h-full" not in html
        assert "w-full" in html

    def test_a_height_and_a_ratio_together_leave_the_height_in_charge(
        self, render, line
    ):
        """Both describe the same box, so one of them has to win, and it is the
        one that says what the box is rather than what shape it should be."""
        html = render(
            '<c-chart :chart="chart" id="revenue" height="320px" aspect-ratio="2" />',
            chart=line,
        )
        assert 'style="height: 320px"' in html
        assert "aspect-ratio" not in html


class TestTheOptionsPayload:
    """What the chart built, carried to the browser and nothing else."""

    def test_the_payload_is_exactly_what_the_chart_dumped(self, render, line):
        assert payload(render(A_CHART, chart=line)) == json.loads(line.dump_options())

    def test_the_series_carries_the_values_in_the_order_given(self, render, line):
        series = payload(render(A_CHART, chart=line))["series"][0]
        assert series["name"] == "Revenue"
        assert series["data"] == [["Jan", 12], ["Feb", 14], ["Mar", 15]]

    @pytest.mark.parametrize(
        ("chart", "expected_type"),
        [
            (Line().add_xaxis(["a"]).add_yaxis("s", [1]), "line"),
            (Bar().add_xaxis(["a"]).add_yaxis("s", [1]), "bar"),
            (Pie().add("s", [("a", 1)]), "pie"),
            (Scatter().add_xaxis([1]).add_yaxis("s", [2]), "scatter"),
        ],
    )
    def test_one_component_carries_every_chart_type(self, render, chart, expected_type):
        """The chart type is the class the view built, never a tag attribute."""
        html = render('<c-chart :chart="chart" id="c" />', chart=chart)
        assert payload(html)["series"][0]["type"] == expected_type

    def test_an_option_this_package_never_named_reaches_the_browser(self, render):
        """Nothing here filters, allow-lists or renames a key."""
        chart = (
            Line()
            .add_xaxis(["a"])
            .add_yaxis("s", [1])
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Revenue"),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
            )
        )
        options = payload(render('<c-chart :chart="chart" id="c" />', chart=chart))
        assert options["title"][0]["text"] == "Revenue"
        assert options["toolbox"]["show"] is True

    def test_the_types_a_view_produces_survive_the_trip(self, render):
        """Dates, decimals and a gap, none of them converted first."""
        chart = (
            Line()
            .add_xaxis([date(2026, 1, 1), date(2026, 2, 1)])
            .add_yaxis("Invoiced", [Decimal("1420.50"), None])
        )
        options = payload(render('<c-chart :chart="chart" id="c" />', chart=chart))
        assert options["series"][0]["data"] == [
            ["2026-01-01", 1420.5],
            ["2026-02-01", None],
        ]


class TestDataCannotBecomeMarkup:
    """Text out of a database has no business changing the page's structure."""

    @pytest.mark.parametrize(
        "hostile",
        [
            "</script><script>alert(1)</script>",
            "</SCRIPT ><img src=x onerror=alert(1)>",
            "<!--</script>-->",
        ],
    )
    def test_a_label_cannot_end_the_options_script_early(self, render, hostile):
        """pyecharts escapes none of these. This package is what does.

        Asserted twice, because either half alone passes while the page is
        broken: the raw sequence is gone from the markup, *and* the label
        still arrives at the chart intact.
        """
        chart = Line().add_xaxis([hostile]).add_yaxis("s", [1])
        html = render('<c-chart :chart="chart" id="c" />', chart=chart)
        body = html.split("data-mvp-chart-options>")[1].split("</script>")[0]
        assert "</script>" not in body.lower()
        assert "<" not in body
        assert payload(html)["xAxis"][0]["data"] == [hostile]
