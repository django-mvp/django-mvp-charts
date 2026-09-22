"""What a line chart does in a real browser.

The rendered-output tests beside this file assert what the server sends: the
options object the component built. They cannot assert that ECharts actually
drew from it, and they cannot measure a canvas at all. Every test here reads a
live ECharts instance back, or measures the page, and asserts what it finds.
Follows the shape of ``test_region_e2e.py``.
"""

import pytest

READ_LINE_STYLE_COLOR = """
(elementId) => {
  const surface = document
    .getElementById(elementId)
    .querySelector('[data-mvp-chart-region-surface]');
  const chart = echarts.getInstanceByDom(surface);
  if (!chart) { return null; }
  return chart.getOption().series[0].lineStyle.color;
}
"""

READ_CHART = """
(elementId) => {
  const surface = document
    .getElementById(elementId)
    .querySelector('[data-mvp-chart-region-surface]');
  const chart = echarts.getInstanceByDom(surface);
  if (!chart) { return null; }
  const option = chart.getOption();
  return { series: option.series[0].data, categories: option.xAxis[0].data };
}
"""

REGION_STATE = """
(elementId) => document.getElementById(elementId)?.dataset.mvpChartRegionState
"""

MEASURE = """
(elementId) => {
  const region = document.getElementById(elementId);
  return {
    region: { width: region.offsetWidth, height: region.offsetHeight },
    wrapper: {
      width: region.parentElement.clientWidth,
      height: region.parentElement.clientHeight,
    },
  };
}
"""


@pytest.fixture
def line_page(chromium, live_server, page):
    """The demo's line chart page, with every region on it settled."""
    page.goto(f"{live_server.url}/line/")
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('[data-mvp-chart-region]'))"
        ".every((r) => r.dataset.mvpChartRegionState)",
        timeout=5000,
    )
    page.wait_for_function(
        "() => Boolean(echarts.getInstanceByDom("
        "document.querySelector('#monthly-revenue [data-mvp-chart-region-surface]')))",
        timeout=5000,
    )
    return page


class TestALineIsDrawn:
    """T007: the values and labels an author wrote reach a real ECharts instance."""

    def test_the_series_data_matches_what_was_written_in_order(self, line_page):
        result = line_page.evaluate(READ_CHART, "monthly-revenue")
        assert result is not None
        assert result["series"] == [
            820,
            932,
            901,
            934,
            1290,
            1330,
            1320,
            1250,
            1400,
            1520,
            1600,
            1710,
        ]

    def test_the_category_values_match_what_was_written_in_order(self, line_page):
        result = line_page.evaluate(READ_CHART, "monthly-revenue")
        assert result["categories"] == [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]


class TestAChartAndABareRegionAreIndependent:
    """US1 scenario 4: a chart and a bare region on one page, neither touching the other."""

    def test_the_line_chart_draws(self, line_page):
        assert line_page.evaluate(READ_CHART, "signups-line") is not None

    def test_the_bare_region_draws_nothing(self, line_page):
        assert line_page.evaluate(READ_CHART, "open-tickets-region") is None

    def test_both_regions_reach_the_ready_state(self, line_page):
        assert line_page.evaluate(REGION_STATE, "signups-line") == "ready"
        assert line_page.evaluate(REGION_STATE, "open-tickets-region") == "ready"


class TestAnAuthorSuppliedColourReachesTheLiveInstance:
    """FR-015: an option this component does not name, read back off a real chart."""

    def test_the_colour_written_on_the_tag_is_the_colour_echarts_drew_with(
        self, line_page
    ):
        result = line_page.evaluate(READ_LINE_STYLE_COLOR, "conversion-rate")
        assert result == "#7c3aed"


class TestTheChartKeepsFillingItsWrapper:
    """FR-005, US1 scenario 5: a line chart holds its shape like any region."""

    def test_the_chart_fills_its_wrapper_before_any_resize(self, line_page):
        measured = line_page.evaluate(MEASURE, "monthly-revenue")
        assert measured["region"] == measured["wrapper"]

    def test_a_window_resize_leaves_it_filling_its_wrapper(self, line_page):
        line_page.set_viewport_size({"width": 700, "height": 900})
        line_page.wait_for_timeout(200)
        measured = line_page.evaluate(MEASURE, "monthly-revenue")
        assert measured["region"] == measured["wrapper"]

    def test_the_viewport_change_really_changed_the_layout(self, line_page):
        """Otherwise the test above would pass by resizing nothing."""
        before = line_page.evaluate(MEASURE, "monthly-revenue")["wrapper"]["width"]
        line_page.set_viewport_size({"width": 700, "height": 900})
        line_page.wait_for_timeout(200)
        after = line_page.evaluate(MEASURE, "monthly-revenue")["wrapper"]["width"]
        assert after != before
