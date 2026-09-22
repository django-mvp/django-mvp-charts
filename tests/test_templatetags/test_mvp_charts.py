"""Tests for `{% echarts_chart %}`, mirroring `mvp_charts/templatetags/mvp_charts.py`.

Calls the tag function directly rather than through a template — Django's
``simple_tag`` decorator leaves the function itself callable, and that is
enough to cover what the tag builds, without a Cotton compile step.
"""

import json

from mvp_charts.echarts.options import Line
from mvp_charts.templatetags.mvp_charts import echarts_chart


class TestEChartsChart:
    """The tag returns an id, a derived options-script id and a JSON payload."""

    def test_the_tag_returns_the_id_it_was_given(self):
        chart = echarts_chart(
            element_id="revenue", values=[12, 14, 15], labels=["Jan", "Feb", "Mar"]
        )
        assert chart.id == "revenue"

    def test_the_options_script_id_is_derived_from_the_chart_id(self):
        chart = echarts_chart(
            element_id="revenue", values=[12, 14, 15], labels=["Jan", "Feb", "Mar"]
        )
        assert chart.options_id == "revenue-options"

    def test_the_payload_parses_back_to_the_object_line_built(self):
        chart = echarts_chart(
            element_id="revenue", values=[12, 14, 15], labels=["Jan", "Feb", "Mar"]
        )
        assert (
            json.loads(chart.payload)
            == Line([12, 14, 15], ["Jan", "Feb", "Mar"]).options()
        )

    def test_a_tag_called_without_an_id_returns_no_payload(self):
        assert echarts_chart(values=[12, 14, 15]) is None
