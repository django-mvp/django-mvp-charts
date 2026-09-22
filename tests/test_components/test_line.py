"""Tests for <c-echarts.line>, the rendered-output contract.

Compiles Cotton source directly, as ``test_region.py`` does, so this file
covers what the tag renders as markup: the options payload built from the
values and labels an author writes on the tag, and the id it is given.
``tests/test_echarts/test_options.py`` covers the options object itself;
``test_line_e2e.py`` covers what only a real browser can measure.
"""

import json
import re

from .test_region import render

LINE = (
    '<c-echarts.line id="revenue" name="Revenue" description="Revenue by month."'
    ' :values="values" :labels="labels" />'
)


def payload(html):
    """The JSON the component's options script carries, parsed back."""
    script = re.search(
        r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.S
    )
    assert script is not None, "no options script in the rendered output"
    return json.loads(script.group(1))


class TestOptionsPayload:
    """FR-002, FR-004: the options object carries exactly what was written."""

    def test_values_and_labels_render_in_the_order_written(self):
        html = render(LINE, values=[12, 14, 15], labels=["Jan", "Feb", "Mar"])
        assert payload(html) == {
            "xAxis": {"type": "category", "data": ["Jan", "Feb", "Mar"]},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "data": [12, 14, 15]}],
        }

    def test_values_without_labels_drop_xaxis_data_and_keep_order(self):
        html = render(
            '<c-echarts.line id="revenue" name="Revenue" description="Revenue by month."'
            ' :values="values" />',
            values=[12, 14, 15],
        )
        options = payload(html)
        assert "data" not in options["xAxis"]
        assert options["series"][0]["data"] == [12, 14, 15]

    def test_none_a_float_and_a_zero_survive_unchanged(self):
        """FR-004: nothing reordered, dropped, combined, rounded or filled in."""
        html = render(LINE, values=[None, 1.5, 0], labels=["Jan", "Feb", "Mar"])
        assert payload(html)["series"][0]["data"] == [None, 1.5, 0]


class TestNoAuthoredScript:
    """FR-001: the template has no JavaScript, only the options data."""

    def test_every_script_tag_is_the_json_payload(self):
        html = render(LINE, values=[12, 14, 15], labels=["Jan", "Feb", "Mar"])
        tags = re.findall(r"<script[^>]*>", html)
        assert tags
        assert all('type="application/json"' in tag for tag in tags)


class TestOptionalNameAndDescription:
    """US2, FR-008/FR-010: a line chart with an id and values, nothing else, still draws."""

    def test_a_chart_with_only_an_id_and_values_draws_with_no_missing_message(self):
        html = render(
            '<c-echarts.line id="revenue" :values="values" />', values=[12, 14, 15]
        )
        assert 'role="alert"' not in html
        assert "has no name" not in html
        assert "has no description" not in html
        assert payload(html)["series"][0]["data"] == [12, 14, 15]

    def test_the_surface_carries_no_role_and_no_aria_label_without_a_name(self):
        html = render(
            '<c-echarts.line id="revenue" :values="values" />', values=[12, 14, 15]
        )
        surface = re.search(
            r"<div[^>]*data-mvp-chart-region-surface[^>]*>", html
        ).group(0)
        assert "role=" not in surface
        assert "aria-label" not in surface

    def test_no_figcaption_without_a_description(self):
        html = render(
            '<c-echarts.line id="revenue" :values="values" />', values=[12, 14, 15]
        )
        assert "<figcaption" not in html


class TestOptionsAttribute:
    """FR-012 … FR-014: an `options` attribute deep-merges over the built object.

    The merge itself is exercised directly in
    ``tests/test_echarts/test_options.py``; this class covers it reaching
    ECharts through the rendered tag.
    """

    def test_options_wins_on_every_key_it_names(self):
        html = render(
            '<c-echarts.line id="revenue" :values="values" :labels="labels"'
            ' :options="options" />',
            values=[12, 14, 15],
            labels=["Jan", "Feb", "Mar"],
            options={"yAxis": {"type": "log"}},
        )
        assert payload(html)["yAxis"] == {"type": "log"}

    def test_a_mapping_in_options_merges_recursively(self):
        html = render(
            '<c-echarts.line id="revenue" :values="values" :labels="labels"'
            ' :options="options" />',
            values=[12, 14, 15],
            labels=["Jan", "Feb", "Mar"],
            options={"xAxis": {"axisLine": {"show": False}}},
        )
        assert payload(html)["xAxis"] == {
            "type": "category",
            "data": ["Jan", "Feb", "Mar"],
            "axisLine": {"show": False},
        }

    def test_a_list_in_options_replaces_a_list_rather_than_merging(self):
        html = render(
            '<c-echarts.line id="revenue" :values="values" :options="options" />',
            values=[12, 14, 15],
            options={"color": ["purple"]},
        )
        assert payload(html)["color"] == ["purple"]

    def test_series_in_options_merges_entry_by_entry_and_keeps_the_data(self):
        html = render(
            '<c-echarts.line id="revenue" :values="values" :options="options" />',
            values=[12, 14, 15],
            options={"series": [{"lineStyle": {"color": "#7c3aed"}}]},
        )
        series = payload(html)["series"][0]
        assert series["data"] == [12, 14, 15]
        assert series["lineStyle"] == {"color": "#7c3aed"}

    def test_a_key_this_package_has_never_heard_of_arrives_unchanged(self):
        html = render(
            '<c-echarts.line id="revenue" :values="values" :options="options" />',
            values=[12, 14, 15],
            options={"toolbox": {"feature": {"saveAsImage": {}}}},
        )
        assert payload(html)["toolbox"] == {"feature": {"saveAsImage": {}}}

    def test_no_options_attribute_leaves_the_built_object_untouched(self):
        html = render(LINE, values=[12, 14, 15], labels=["Jan", "Feb", "Mar"])
        assert payload(html) == {
            "xAxis": {"type": "category", "data": ["Jan", "Feb", "Mar"]},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "data": [12, 14, 15]}],
        }


class TestNoAppearanceOfItsOwn:
    """FR-013, FR-014, SC-004: values alone build exactly what ECharts needs.

    No colour, width, marker, legend, grid, axis line, animation or typeface
    - every key present traces to the values and labels written, and nothing
    else.
    """

    def test_the_built_object_is_byte_for_byte_the_dictionary_and_nothing_more(self):
        html = render(
            '<c-echarts.line id="revenue" :values="values" />', values=[12, 14, 15]
        )
        assert payload(html) == {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "data": [12, 14, 15]}],
        }


class TestMissingId:
    """FR-006: a missing id renders the region's own message, and no script."""

    MISSING_ID = (
        '<c-echarts.line name="Revenue" description="Revenue by month."'
        ' :values="values" />'
    )

    def test_a_missing_id_renders_the_regions_missing_id_message(self):
        html = render(self.MISSING_ID, values=[12, 14, 15])
        alert = re.search(r'<div[^>]*role="alert"[^>]*>(.*?)</div>', html, re.S)
        assert alert is not None
        assert "id" in alert.group(1).lower()

    def test_a_missing_id_renders_no_options_script(self):
        html = render(self.MISSING_ID, values=[12, 14, 15])
        assert "<script" not in html
