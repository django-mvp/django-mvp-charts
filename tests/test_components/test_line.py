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
