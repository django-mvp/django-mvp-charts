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


MEASURE = """
(id) => {
  const figure = document.getElementById(id);
  const chart = echarts.getInstanceByDom(
    figure.querySelector('[data-mvp-chart-surface]'));
  return { width: chart.getWidth(), height: chart.getHeight() };
}
"""


@pytest.fixture
def sizing_page(chromium, live_server, page):
    """The probe page of awkward boxes, with anything drawable drawn."""
    warnings = []
    page.on(
        "console",
        lambda message: message.type == "warning" and warnings.append(message.text),
    )
    page.goto(f"{live_server.url}/probe/sizing/")
    page.wait_for_function(CHARTS_DRAWN, timeout=10000)
    page.wait_for_timeout(200)
    return page, warnings


class TestAChartThatHasNoBoxYet:
    """A chart is not always drawable at first paint, and not always at fault."""

    def test_a_chart_in_a_collapsed_panel_draws_when_the_panel_opens(self, sizing_page):
        """0x0 at load, a real box once revealed, and no complaint either way.

        A panel that is closed is the page working as designed. The old
        `IntersectionObserver` existed to tell this apart from a mistake; the
        resize observer now does it by arithmetic, because a hidden element
        measures zero on both axes and a mis-sized one does not.
        """
        page, warnings = sizing_page
        assert page.evaluate(MEASURE, "in-collapsed-panel") == {
            "width": 0,
            "height": 0,
        }
        assert not any("in-collapsed-panel" in text for text in warnings)

        page.evaluate(
            "() => document.getElementById('collapsed').classList.add('open')"
        )
        page.wait_for_function(
            "() => echarts.getInstanceByDom(document.querySelector"
            "('#in-collapsed-panel [data-mvp-chart-surface]')).getHeight() > 0",
            timeout=5000,
        )
        assert page.evaluate(MEASURE, "in-collapsed-panel")["height"] == 300
        assert not any("in-collapsed-panel" in text for text in warnings)

    def test_a_wrapper_that_resolves_to_no_height_is_reported(self, sizing_page):
        """The one failure that otherwise leaves no trace anywhere.

        The options are right, ECharts initialised, nothing threw, and the
        reader sees blank page. Width without height is what separates it
        from the collapsed panel above, and the console is where it is said.
        """
        page, warnings = sizing_page
        measured = page.evaluate(MEASURE, "never-has-height")
        assert measured["width"] > 0
        assert measured["height"] == 0
        assert any(
            "never-has-height" in text and "no height" in text for text in warnings
        )

    def test_a_chart_with_a_box_is_not_reported(self, sizing_page):
        page, warnings = sizing_page
        assert page.evaluate(MEASURE, "control")["height"] == 300
        assert not any("control" in text for text in warnings)

    def test_it_is_said_once_rather_than_on_every_resize(self, sizing_page):
        """The check runs on every resize, and a stream of identical warnings
        is how a console stops being read."""
        page, warnings = sizing_page
        page.set_viewport_size({"width": 700, "height": 900})
        page.set_viewport_size({"width": 1100, "height": 900})
        page.wait_for_timeout(300)
        assert len([t for t in warnings if "never-has-height" in t]) == 1


class TestAChartSizedByItsRatio:
    """A ratio is a height the figure works out from the width it was given.

    Measured rather than asserted against the style attribute, because the
    attribute proves a string reached the markup and says nothing about the
    box the browser gave the chart.
    """

    def test_the_height_is_the_width_divided_by_the_ratio(self, sizing_page):
        page, _ = sizing_page
        assert page.evaluate(MEASURE, "sized-by-its-ratio") == {
            "width": 400,
            "height": 200,
        }

    def test_the_ratio_holds_when_the_width_changes(self, sizing_page):
        """The point of the ratio: the chart keeps its shape at any width."""
        page, _ = sizing_page
        page.evaluate(
            "() => { document.getElementById('sized-by-its-ratio')"
            ".parentElement.style.width = '600px'; }"
        )
        page.wait_for_function(
            "() => echarts.getInstanceByDom(document.querySelector"
            "('#sized-by-its-ratio [data-mvp-chart-surface]')).getWidth() === 600",
            timeout=5000,
        )
        assert page.evaluate(MEASURE, "sized-by-its-ratio")["height"] == 300

    def test_a_ratio_is_a_way_out_of_the_wrapper_with_no_height(self, sizing_page):
        """Same wrapper as the chart that cannot draw, and nothing to report."""
        page, warnings = sizing_page
        assert not any("sized-by-its-ratio" in text for text in warnings)


class TestThePlaceholder:
    """What stands in the figure until the chart is drawn into it."""

    @pytest.fixture
    def waiting_page(self, chromium, live_server, page):
        """A figure holding its placeholder, because no library ever arrives."""
        page.goto(f"{live_server.url}/probe/placeholder/")
        page.wait_for_function("() => document.readyState === 'complete'", timeout=5000)
        return page

    def test_it_sits_in_the_middle_of_the_figure(self, waiting_page):
        """Centred with nothing around it to do the centring.

        Measured rather than read off a class list, because the classes that
        put an element in the middle of its figure only do so while it has a
        size of its own for the automatic margins to divide up — and a class
        list looks identical either way.
        """
        centres = waiting_page.evaluate(
            "() => { const figure = document.getElementById('waiting');"
            " const spinner = figure"
            ".querySelector('[data-mvp-chart-placeholder]');"
            " const f = figure.getBoundingClientRect();"
            " const s = spinner.getBoundingClientRect();"
            " return { figure: [f.width, f.height],"
            "  spinner: [s.width, s.height],"
            "  offset: [s.left - f.left + s.width / 2 - f.width / 2,"
            "           s.top - f.top + s.height / 2 - f.height / 2] };"
            " }"
        )
        assert centres["figure"] == [400, 200]
        assert centres["offset"] == [0, 0]

    def test_the_spinner_is_drawn_rather_than_only_classed(self, waiting_page):
        """`loading` is a class daisyUI has to have built for it to spin.

        An element carrying a class the stylesheet never emitted is an empty
        inline span with no box at all, and the markup looks identical either
        way — which is why this measures instead of reading the class back.
        """
        box = waiting_page.evaluate(
            "() => document.querySelector('#waiting .loading').getBoundingClientRect()"
        )
        assert box["width"] > 0
        assert box["height"] > 0
        assert box["width"] < 400
        assert box["height"] < 200

    def test_it_stays_while_there_is_no_chart_to_replace_it(self, waiting_page):
        """A figure that goes empty and stays empty is the worse of the two."""
        assert (
            waiting_page.locator("#waiting [data-mvp-chart-placeholder]").count() == 1
        )

    def test_it_is_gone_once_the_chart_is_drawn(self, drawn_page):
        """Every chart on that page asks for one, and none of them still has it."""
        assert drawn_page.locator("[data-mvp-chart-placeholder]").count() == 0
        assert drawn_page.locator("[data-mvp-chart]").count() > 0


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
