"""What `<c-chart>` does in a real browser.

The rendered-output tests beside this file assert what the server sends. They
cannot assert that ECharts drew from it, and they cannot measure a canvas at
all. Every test here reads a live ECharts instance back, or measures the page.
"""

import pytest

READ_CHART = """
(elementId) => {
  const surface = document
    .getElementById(elementId)
    .querySelector('[data-mvp-chart-surface]');
  const chart = echarts.getInstanceByDom(surface);
  if (!chart) { return null; }
  const option = chart.getOption();
  return {
    type: option.series[0].type,
    data: option.series[0].data,
    width: chart.getWidth(),
  };
}
"""

CHARTS_DRAWN = """
() => Array.from(document.querySelectorAll('[data-mvp-chart]'))
  .every((figure) => Boolean(echarts.getInstanceByDom(
    figure.querySelector('[data-mvp-chart-surface]'))))
"""


@pytest.fixture
def drawn_page(chromium, live_server, page):
    """The demo's chart types page, with every chart on it drawn."""
    page.goto(f"{live_server.url}/chart-types/")
    page.wait_for_function(CHARTS_DRAWN, timeout=10000)
    return page


class TestAChartIsDrawn:
    """The options the server sent reached ECharts and became a chart."""

    def test_the_chart_holds_the_values_the_view_gave_it(self, drawn_page):
        chart = drawn_page.evaluate(READ_CHART, "revenue-and-costs")
        assert chart is not None, "ECharts never initialised on the drawing surface"
        assert chart["type"] == "line"
        assert [point[1] for point in chart["data"]] == [
            820,
            932,
            901,
            934,
            1290,
            1330,
        ]

    @pytest.mark.parametrize(
        ("element_id", "expected_type"),
        [
            ("orders-by-region", "bar"),
            ("accounts-by-plan", "pie"),
            ("response-time", "scatter"),
        ],
    )
    def test_every_chart_type_on_the_page_draws(
        self, drawn_page, element_id, expected_type
    ):
        """One component, and each chart drawn as the class the view built."""
        chart = drawn_page.evaluate(READ_CHART, element_id)
        assert chart is not None
        assert chart["type"] == expected_type

    def test_a_canvas_is_actually_painted(self, drawn_page):
        """An ECharts instance with a zero-sized canvas draws nothing.

        The instance existing is not the same claim as the chart occupying
        the box it was given, and the second is what a reader sees.
        """
        box = drawn_page.evaluate(
            "() => document.querySelector('#revenue-and-costs canvas')"
            ".getBoundingClientRect()"
        )
        assert box["width"] > 100
        assert box["height"] > 100


class TestAChartFollowsItsBox:
    """A page is not a fixed rectangle, and a chart is redrawn when its box moves."""

    def test_a_narrower_window_narrows_the_chart(self, drawn_page):
        before = drawn_page.evaluate(READ_CHART, "revenue-and-costs")["width"]
        drawn_page.set_viewport_size({"width": 640, "height": 900})
        drawn_page.wait_for_function(
            "(was) => echarts.getInstanceByDom(document.querySelector"
            "('#revenue-and-costs [data-mvp-chart-surface]')).getWidth() < was",
            arg=before,
            timeout=5000,
        )
        after = drawn_page.evaluate(READ_CHART, "revenue-and-costs")["width"]
        assert after < before


class TestWithNoChartingLibrary:
    """The one failure the package reports, and where it reports it."""

    @pytest.fixture
    def no_library_page(self, chromium, live_server, page):
        messages = []
        page.on("console", lambda message: messages.append(message))
        page.goto(f"{live_server.url}/probe/no-library/")
        page.wait_for_function("() => document.readyState === 'complete'", timeout=5000)
        return page, messages

    def test_it_says_so_in_the_console(self, no_library_page):
        """In the console, not in the page.

        What a project shows its readers when something is broken is the
        project's decision, and a message drawn into the page takes it away.
        """
        _, messages = no_library_page
        errors = [m.text for m in messages if m.type == "error"]
        assert any("window.echarts is not loaded" in text for text in errors)

    def test_the_page_around_it_is_left_standing(self, no_library_page):
        page, _ = no_library_page
        assert page.locator("#page-still-works").is_visible()

    def test_nothing_is_drawn_into_the_page(self, no_library_page):
        page, _ = no_library_page
        assert page.locator("#unrenderable canvas").count() == 0
        assert page.locator("#unrenderable").inner_text().strip() == ""
