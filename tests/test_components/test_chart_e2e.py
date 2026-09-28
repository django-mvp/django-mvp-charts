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
    page.goto(f"{live_server.url}/chart-types/")
    page.wait_for_function(CHARTS_DRAWN, timeout=10000)
    return page


class TestAChartIsDrawn:
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
        chart = drawn_page.evaluate(READ_CHART, element_id)
        assert chart is not None
        assert chart["type"] == expected_type

    def test_a_canvas_is_actually_painted(self, drawn_page):
        box = drawn_page.evaluate(
            "() => document.querySelector('#revenue-and-costs canvas')"
            ".getBoundingClientRect()"
        )
        assert box["width"] > 100
        assert box["height"] > 100


class TestAChartFollowsItsBox:
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
    def test_a_chart_in_a_collapsed_panel_draws_when_the_panel_opens(self, sizing_page):
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
        page, warnings = sizing_page
        page.set_viewport_size({"width": 700, "height": 900})
        page.set_viewport_size({"width": 1100, "height": 900})
        page.wait_for_timeout(300)
        assert len([t for t in warnings if "never-has-height" in t]) == 1


class TestAChartSizedByItsRatio:
    def test_the_height_is_the_width_divided_by_the_ratio(self, sizing_page):
        page, _ = sizing_page
        assert page.evaluate(MEASURE, "sized-by-its-ratio") == {
            "width": 400,
            "height": 200,
        }

    def test_the_ratio_holds_when_the_width_changes(self, sizing_page):
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
        page, warnings = sizing_page
        assert not any("sized-by-its-ratio" in text for text in warnings)


class TestThePlaceholder:
    @pytest.fixture
    def waiting_page(self, chromium, live_server, page):
        page.goto(f"{live_server.url}/probe/placeholder/")
        page.wait_for_function("() => document.readyState === 'complete'", timeout=5000)
        return page

    def test_it_sits_in_the_middle_of_the_figure(self, waiting_page):
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
        box = waiting_page.evaluate(
            "() => document.querySelector('#waiting .loading').getBoundingClientRect()"
        )
        assert box["width"] > 0
        assert box["height"] > 0
        assert box["width"] < 400
        assert box["height"] < 200

    def test_it_stays_while_there_is_no_chart_to_replace_it(self, waiting_page):
        assert (
            waiting_page.locator("#waiting [data-mvp-chart-placeholder]").count() == 1
        )

    def test_it_is_gone_once_the_chart_is_drawn(self, drawn_page):
        assert drawn_page.locator("[data-mvp-chart-placeholder]").count() == 0
        assert drawn_page.locator("[data-mvp-chart]").count() > 0


class TestWithNoChartingLibrary:
    @pytest.fixture
    def no_library_page(self, chromium, live_server, page):
        messages = []
        page.on("console", lambda message: messages.append(message))
        page.goto(f"{live_server.url}/probe/no-library/")
        page.wait_for_function("() => document.readyState === 'complete'", timeout=5000)
        return page, messages

    def test_it_says_so_in_the_console(self, no_library_page):
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


@pytest.fixture
def renderer_page(chromium, live_server, page):
    page.goto(f"{live_server.url}/probe/renderer/")
    page.wait_for_function(CHARTS_DRAWN, timeout=10000)
    return page


class TestTheRendererTheChartNamed:
    def test_a_chart_built_for_svg_is_drawn_as_svg(self, renderer_page):
        figure = renderer_page.locator("#drawn-as-svg")
        assert figure.locator("svg").count() == 1
        assert figure.locator("canvas").count() == 0

    def test_a_chart_that_named_none_is_still_drawn_to_a_canvas(self, renderer_page):
        figure = renderer_page.locator("#drawn-to-canvas")
        assert figure.locator("canvas").count() >= 1
        assert figure.locator("svg").count() == 0


class TestTheDrawnEvent:
    def test_each_figure_announces_its_chart_once(self, renderer_page):
        counts = renderer_page.evaluate(
            "() => Object.fromEntries(Object.entries(window.drawnCharts)"
            ".map(([id, charts]) => [id, charts.length]))"
        )
        assert counts == {"drawn-as-svg": 1, "drawn-to-canvas": 1}

    def test_it_carries_the_instance_echarts_holds(self, renderer_page):
        same = renderer_page.evaluate(
            "() => window.drawnCharts['drawn-as-svg'][0] === echarts.getInstanceByDom("
            "document.querySelector('#drawn-as-svg [data-mvp-chart-surface]'))"
        )
        assert same is True

    def test_the_chart_is_ready_to_be_changed_when_it_arrives(self, renderer_page):
        title = renderer_page.evaluate(
            "() => { const chart = window.drawnCharts['drawn-to-canvas'][0];"
            " chart.setOption({ title: { text: 'Set from the page' } });"
            " return chart.getOption().title[0].text; }"
        )
        assert title == "Set from the page"

    def test_drawing_again_does_not_announce_again(self, renderer_page):
        renderer_page.evaluate("() => window.mvpCharts.draw()")
        counts = renderer_page.evaluate(
            "() => window.drawnCharts['drawn-as-svg'].length"
        )
        assert counts == 1


class TestTheDemosChartReachedFromThePage:
    @pytest.fixture
    def options_page(self, chromium, live_server, page):
        page.goto(f"{live_server.url}/options/")
        page.wait_for_function(CHARTS_DRAWN, timeout=10000)
        return page

    def test_it_is_drawn_as_svg(self, options_page):
        assert options_page.locator("#signups svg").count() == 1
        assert options_page.locator("#signups canvas").count() == 0

    def test_its_tooltip_is_the_function_the_page_set(self, options_page):
        text = options_page.evaluate(
            "() => { const chart = echarts.getInstanceByDom(document.querySelector"
            "('#signups [data-mvp-chart-surface]'));"
            " return chart.getOption().tooltip[0].formatter"
            "({ name: 'Week 1', value: 40 }); }"
        )
        assert text == "Week 1: 40 sign-ups"


BOXES = """
(id) => {
  const box = (el) => { const r = el.getBoundingClientRect();
    return { top: r.top, bottom: r.bottom, height: r.height }; };
  const figure = document.getElementById(id);
  return {
    figure: box(figure),
    caption: box(figure.querySelector('figcaption')),
    chart: echarts.getInstanceByDom(
      figure.querySelector('[data-mvp-chart-surface]')).getHeight(),
  };
}
"""


class TestACaptionedFigure:
    def test_a_height_is_the_charts_and_the_caption_adds_to_it(self, sizing_page):
        page, _ = sizing_page
        boxes = page.evaluate(BOXES, "captioned")
        assert boxes["chart"] == 300
        assert boxes["caption"]["height"] > 0
        assert boxes["caption"]["bottom"] <= boxes["figure"]["bottom"]
        assert boxes["figure"]["height"] > 300

    def test_a_ratio_is_the_charts_however_long_the_caption(self, sizing_page):
        page, _ = sizing_page
        assert page.evaluate(MEASURE, "captioned-by-ratio") == {
            "width": 400,
            "height": 200,
        }

    def test_in_a_box_the_page_sized_the_chart_takes_what_is_left(self, sizing_page):
        page, _ = sizing_page
        boxes = page.evaluate(BOXES, "captioned-filling")
        assert boxes["figure"]["height"] == 300
        assert 0 < boxes["chart"] < 300
        assert boxes["caption"]["bottom"] <= boxes["figure"]["bottom"]

    def test_there_a_caption_that_grows_takes_its_room_from_the_chart(
        self, sizing_page
    ):
        page, _ = sizing_page
        before = page.evaluate(BOXES, "captioned-filling")["chart"]
        page.evaluate(
            "() => { document.querySelector('#captioned-filling figcaption')"
            ".textContent = 'A caption long enough to wrap onto a second line"
            " and then a third, because the figure is only four hundred pixels"
            " wide.'; }"
        )
        page.wait_for_function(
            "(was) => echarts.getInstanceByDom(document.querySelector"
            "('#captioned-filling [data-mvp-chart-surface]')).getHeight() < was",
            arg=before,
            timeout=5000,
        )
        assert page.evaluate(BOXES, "captioned-filling")["chart"] < before

    def test_a_caption_does_not_hide_a_chart_with_no_height(self, sizing_page):
        page, warnings = sizing_page
        assert page.evaluate(MEASURE, "captioned-with-no-height")["height"] == 0
        assert any(
            "captioned-with-no-height" in text and "no height" in text
            for text in warnings
        )


# What ECharts drew, not what it was sent. A bar's pattern is an overlay element
# reached through its data; a legend icon's is in ZRender's display list.
READ_PATTERNS = """
(elementId) => {
  const surface = document
    .getElementById(elementId)
    .querySelector('[data-mvp-chart-surface]');
  const chart = echarts.getInstanceByDom(surface);
  const tile = (element) => {
    const fill = element && element.style && element.style.fill;
    return fill && fill.image ? fill.image.toDataURL() : null;
  };
  const overlay = (bar) => tile(bar && bar._decalEl);
  const model = chart.getModel();
  const series = model.getSeriesByType('bar').map((seriesModel) => {
    const data = seriesModel.getData();
    const bars = [];
    for (let i = 0; i < data.count(); i++) {
      bars.push(overlay(data.getItemGraphicEl(i)));
    }
    return { name: seriesModel.name, bars };
  });
  const drawn = chart.getZr().storage.getDisplayList();
  const surfaceElement = surface;
  return {
    series,
    patterned: drawn.map(tile).filter(Boolean),
    label: surfaceElement.getAttribute('aria-label'),
    describedby: surfaceElement.getAttribute('aria-describedby'),
    descriptionText: (
      document.getElementById(surfaceElement.getAttribute('aria-describedby')) || {}
    ).textContent,
  };
}
"""


# The same read for the marks other than bars. Each mark is asked for its own
# pattern, wherever ECharts put it: a fill of its own, or an overlay element.
READ_MARKS = """
(elementId) => {
  const surface = document
    .getElementById(elementId)
    .querySelector('[data-mvp-chart-surface]');
  const chart = echarts.getInstanceByDom(surface);
  const model = chart.getModel();
  const tile = (element) => {
    const fill = element && element.style && element.style.fill;
    return fill && fill.image ? fill.image.toDataURL() : null;
  };
  const pattern = (element) => tile(element) || tile(element && element._decalEl);
  const patternOf = (element) => {
    if (!element) return null;
    if (element.childCount) {
      for (let i = 0; i < element.childCount(); i++) {
        const found = patternOf(element.childAt(i));
        if (found) return found;
      }
    }
    return pattern(element);
  };
  const slices = model.getSeriesByType('pie').flatMap((seriesModel) => {
    const data = seriesModel.getData();
    return Array.from({ length: data.count() }, (_, i) =>
      patternOf(data.getItemGraphicEl(i)));
  });
  const areas = model.getSeriesByType('line').map((seriesModel) => {
    const area = chart.getViewOfSeriesModel(seriesModel)._polygon;
    return {
      name: seriesModel.name,
      drawn: Boolean(area),
      pattern: pattern(area),
      opacity: area ? area.style.opacity : null,
    };
  });
  const symbols = model.getSeriesByType('scatter').map((seriesModel) => {
    const data = seriesModel.getData();
    const marks = [];
    for (let i = 0; i < data.count(); i++) {
      const el = data.getItemGraphicEl(i);
      if (el) marks.push(patternOf(el));
    }
    return { name: seriesModel.name, marks };
  });
  const legend = chart
    .getZr()
    .storage.getDisplayList()
    .map(tile)
    .filter(Boolean);
  return {
    slices,
    areas,
    symbols,
    legend,
    label: surface.getAttribute('aria-label'),
  };
}
"""

# Colour is the most opaque pixel, because a circle's edge blends into the
# transparent pixels around it. Shape ignores colour, so two tiles differing
# only in colour share a shape.
READ_TILE = """
(dataUrl) => new Promise((resolve) => {
  const image = new Image();
  image.onload = () => {
    const canvas = document.createElement('canvas');
    canvas.width = image.width;
    canvas.height = image.height;
    const context = canvas.getContext('2d');
    context.drawImage(image, 0, 0);
    const pixels = context.getImageData(0, 0, canvas.width, canvas.height).data;
    let best = null;
    let shape = '';
    for (let i = 0; i < pixels.length; i += 4) {
      if (pixels[i + 3] > 0 && (!best || pixels[i + 3] > best[3])) {
        best = [pixels[i], pixels[i + 1], pixels[i + 2], pixels[i + 3]];
      }
      shape += pixels[i + 3] > 127 ? '1' : '0';
    }
    resolve({ colour: best && best.slice(0, 3), shape });
  };
  image.src = dataUrl;
})
"""


@pytest.fixture
def patterns_page(chromium, live_server, page):
    page.goto(f"{live_server.url}/probe/patterns/")
    page.wait_for_function(CHARTS_DRAWN, timeout=10000)
    return page


class TestDecalPatterns:
    def test_every_bar_of_each_series_carries_a_pattern(self, patterns_page):
        drawn = patterns_page.evaluate(READ_PATTERNS, "patterned-bar")
        assert [series["name"] for series in drawn["series"]] == ["Online", "In store"]
        for series in drawn["series"]:
            assert len(series["bars"]) == 4
            assert all(series["bars"]), f"{series['name']} has an unpatterned bar"

    def test_the_two_series_are_drawn_with_different_patterns(self, patterns_page):
        online, in_store = patterns_page.evaluate(READ_PATTERNS, "patterned-bar")[
            "series"
        ]
        assert len(set(online["bars"])) == 1
        assert len(set(in_store["bars"])) == 1
        assert online["bars"][0] != in_store["bars"][0]

    def test_each_legend_icon_carries_its_series_pattern(self, patterns_page):
        drawn = patterns_page.evaluate(READ_PATTERNS, "patterned-bar")
        online, in_store = (series["bars"][0] for series in drawn["series"])
        assert drawn["patterned"].count(online) == 4 + 1
        assert drawn["patterned"].count(in_store) == 4 + 1

    def test_the_surface_keeps_the_tags_name_and_description(self, patterns_page):
        drawn = patterns_page.evaluate(READ_PATTERNS, "patterned-bar")
        assert drawn["label"] == "Orders by channel"
        assert drawn["describedby"] == "patterned-bar-description"
        assert drawn["descriptionText"].strip().startswith("Orders by region")

    def test_every_pie_slice_carries_a_pattern(self, patterns_page):
        slices = patterns_page.evaluate(READ_MARKS, "patterned-pie")["slices"]
        assert len(slices) == 3
        assert all(slices)

    def test_a_pie_slice_is_not_drawn_with_its_neighbours_pattern(self, patterns_page):
        slices = patterns_page.evaluate(READ_MARKS, "patterned-pie")["slices"]
        assert len(set(slices)) == 3

    def test_the_area_under_a_plain_line_carries_a_pattern(self, patterns_page):
        areas = patterns_page.evaluate(READ_MARKS, "patterned-line")["areas"]
        assert [area["name"] for area in areas] == ["Online", "In store"]
        for area in areas:
            assert area["drawn"], f"{area['name']} has no area"
            assert area["pattern"], f"{area['name']} area is unpatterned"

    def test_the_area_under_a_plain_line_is_drawn_at_zero_opacity(self, patterns_page):
        areas = patterns_page.evaluate(READ_MARKS, "patterned-line")["areas"]
        assert [area["opacity"] for area in areas] == [0, 0]

    def test_the_area_under_a_shaded_line_carries_a_pattern(self, patterns_page):
        areas = patterns_page.evaluate(READ_MARKS, "patterned-area")["areas"]
        assert len(areas) == 2
        for area in areas:
            assert area["drawn"], f"{area['name']} has no area"
            assert area["pattern"], f"{area['name']} area is unpatterned"

    def test_the_area_under_a_shaded_line_is_visible(self, patterns_page):
        areas = patterns_page.evaluate(READ_MARKS, "patterned-area")["areas"]
        assert all(area["opacity"] > 0 for area in areas)

    def test_no_scatter_symbol_carries_a_pattern(self, patterns_page):
        symbols = patterns_page.evaluate(READ_MARKS, "patterned-scatter")["symbols"]
        assert [series["name"] for series in symbols] == ["Online", "In store"]
        for series in symbols:
            assert series["marks"], f"{series['name']} drew no symbols to read"
            assert not any(series["marks"]), f"{series['name']} has a patterned symbol"

    def test_the_scatter_legend_icons_do_carry_a_pattern(self, patterns_page):
        legend = patterns_page.evaluate(READ_MARKS, "patterned-scatter")["legend"]
        assert len(legend) == 2
        assert legend[0] != legend[1]

    def test_the_surface_is_labelled_by_echarts_and_not_by_the_tag(self, patterns_page):
        label = patterns_page.evaluate(READ_MARKS, "described-by-echarts")["label"]
        assert label
        assert label != "Orders"

    def test_each_series_draws_its_pattern_in_the_colour_its_entry_names(
        self, patterns_page
    ):
        drawn = patterns_page.evaluate(READ_PATTERNS, "coloured-patterns")
        online, in_store = (series["bars"][0] for series in drawn["series"])
        assert patterns_page.evaluate(READ_TILE, online)["colour"] == [192, 57, 43]
        assert patterns_page.evaluate(READ_TILE, in_store)["colour"] == [30, 132, 73]

    def test_the_two_series_are_drawn_with_tiles_of_different_shape(
        self, patterns_page
    ):
        drawn = patterns_page.evaluate(READ_PATTERNS, "coloured-patterns")
        online, in_store = (series["bars"][0] for series in drawn["series"])
        assert online != in_store
        online_tile = patterns_page.evaluate(READ_TILE, online)
        in_store_tile = patterns_page.evaluate(READ_TILE, in_store)
        assert online_tile["shape"] != in_store_tile["shape"]
