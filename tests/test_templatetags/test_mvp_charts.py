"""Tests for `{% chart_options %}`, mirroring `mvp_charts/templatetags/mvp_charts.py`.

Calls the tag function directly rather than through a template — Django's
``simple_tag`` decorator leaves the function itself callable, and that is
enough to cover what the tag produces, without a Cotton compile step.
"""

import json

from pyecharts.charts import Line

from mvp_charts.templatetags.mvp_charts import chart_options


class TestChartOptions:
    """The chart's own options, escaped for a script element and nothing else."""

    def test_it_returns_what_the_chart_dumped(self):
        chart = Line().add_xaxis(["Jan"]).add_yaxis("Revenue", [12])
        assert json.loads(chart_options(chart)) == json.loads(chart.dump_options())

    def test_it_neither_adds_a_key_nor_removes_one(self):
        """The package builds no options of its own and filters none away."""
        chart = Line().add_xaxis(["Jan"]).add_yaxis("Revenue", [12])
        assert set(json.loads(chart_options(chart))) == set(
            json.loads(chart.dump_options())
        )

    def test_the_three_sequences_that_end_a_script_early_are_escaped(self):
        """`<`, `>` and `&`, the same three `json_script` escapes.

        pyecharts escapes none of them, so without this a label carrying
        `</script>` closes the element it is sitting in.
        """
        chart = Line().add_xaxis(["a</script>&b"]).add_yaxis("s", [1])
        rendered = chart_options(chart)
        assert "<" not in rendered
        assert ">" not in rendered
        assert "&" not in rendered
        assert json.loads(rendered)["xAxis"][0]["data"] == ["a</script>&b"]

    def test_the_output_is_marked_safe_so_django_does_not_escape_it_again(self):
        """Double-escaping produces `&amp;quot;`, and the JSON stops parsing."""
        chart = Line().add_xaxis(["Jan"]).add_yaxis("Revenue", [12])
        assert hasattr(chart_options(chart), "__html__")
