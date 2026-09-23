"""Tests for `{% chart_options %}`, mirroring `mvp_charts/templatetags/mvp_charts.py`.

Calls the tag function directly rather than through a template — Django's
``simple_tag`` decorator leaves the function itself callable, and that is
enough to cover what the tag produces, without a Cotton compile step.
"""

import json

import pytest
from pyecharts import options as opts
from pyecharts.charts import Bar, Line
from pyecharts.commons.utils import JsCode

from mvp_charts.templatetags.mvp_charts import callback_option_name, chart_options


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


def chart_with_a_callback(**tooltip_kwargs):
    """A chart whose tooltip formatter is a JavaScript function."""
    return (
        Line()
        .add_xaxis(["Jan"])
        .add_yaxis(
            "Revenue",
            [12],
            tooltip_opts=opts.TooltipOpts(
                formatter=JsCode("function(p){return p.name;}"), **tooltip_kwargs
            ),
        )
    )


class TestChartOptionsRejectsJavaScriptCallbacks:
    """A chart carrying a `JsCode` is refused here, not in the browser.

    `dump_options()` writes such a function into the document unquoted, which
    is no longer JSON. The page reads the payload with `JSON.parse`, so what
    reached the reader was a figure that never stopped waiting and one line in
    a console nobody was watching.
    """

    def test_a_chart_carrying_a_callback_is_refused(self):
        with pytest.raises(ValueError):
            chart_options(chart_with_a_callback())

    def test_nothing_that_is_returned_is_ever_unparseable(self):
        """The guarantee the refusal buys: a payload out of here is JSON.

        Without it a callback reaches `JSON.parse` as bare function text and
        throws there, which is the defect this class exists for.
        """
        try:
            rendered = chart_options(chart_with_a_callback())
        except ValueError:
            return
        json.loads(rendered)

    def test_the_refusal_names_the_option_the_callback_sits_on(self):
        """A chart with forty options should not have to be bisected by hand."""
        with pytest.raises(ValueError, match="formatter"):
            chart_options(chart_with_a_callback())

    def test_the_refusal_points_at_the_route_that_does_work(self):
        """Writing it against the chart instance, per the README."""
        with pytest.raises(ValueError, match="getInstanceByDom"):
            chart_options(chart_with_a_callback())

    def test_it_names_whichever_option_carries_the_callback(self):
        """Not only the ones called `formatter`."""
        chart = (
            Bar()
            .add_xaxis(["Jan"])
            .add_yaxis(
                "Revenue",
                [12],
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode("function(){return 1;}")
                ),
            )
        )
        with pytest.raises(ValueError, match="color"):
            chart_options(chart)

    def test_a_chart_without_a_callback_is_untouched_by_the_check(self):
        chart = Line().add_xaxis(["Jan"]).add_yaxis("Revenue", [12])
        assert json.loads(chart_options(chart)) == json.loads(chart.dump_options())


class TestCallbackOptionName:
    """Reading the option off the two serialisations of one chart."""

    def test_it_reads_the_key_immediately_before_the_divergence(self):
        assert (
            callback_option_name(
                '{"formatter": fn, "x": 1}', '{"formatter": "fn", "x": 1}'
            )
            == "formatter"
        )

    def test_it_returns_nothing_when_no_key_precedes_the_divergence(self):
        """The caller says "one of its options" rather than inventing a name."""
        assert callback_option_name("[1]", "[2]") is None

    def test_it_returns_nothing_when_the_two_agree(self):
        assert callback_option_name('{"a": 1}', '{"a": 1}') is None
