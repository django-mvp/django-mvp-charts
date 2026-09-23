"""Tests for `{% echarts_chart %}`, mirroring `mvp_charts/templatetags/mvp_charts.py`.

Calls the tag function directly rather than through a template — Django's
``simple_tag`` decorator leaves the function itself callable, and that is
enough to cover what the tag builds, without a Cotton compile step.
"""

import json

from mvp_charts.echarts.options import Line
from mvp_charts.templatetags.mvp_charts import echarts_chart


class TestEChartsChart:
    """The tag returns an id and a JSON payload.

    Issue #33 removes the second generated id: the payload now nests inside
    its region's figure instead of sitting beside it and being matched back
    by id, so there is no options-script id to derive.
    """

    def test_the_tag_returns_the_id_it_was_given(self):
        chart = echarts_chart(
            element_id="revenue", values=[12, 14, 15], labels=["Jan", "Feb", "Mar"]
        )
        assert chart.id == "revenue"

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
