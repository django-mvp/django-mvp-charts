"""What a chart region does in a real browser.

The rendered-output tests beside this file assert what the server sends. They
cannot assert the thing this feature is actually about: that the region ends up
occupying its wrapper's box, exactly, on a real page with a real layout engine.
A class name in the markup says a rule was asked for, never that it applied.

Every test here measures the page and asserts numbers.
"""

import pytest

#: Each region's own box, and the inner box of the element wrapping it.
#:
#: ``offsetWidth`` is the region's border box, and the region carries no border
#: or padding, so it is the space the region occupies. ``clientWidth`` is the
#: wrapper's box inside its own border, which is the space the region was
#: given. Equal means the region fills its wrapper with nothing clipped and
#: nothing left over, which is the claim; comparing the two elements'
#: ``getBoundingClientRect`` would instead fail by the wrapper's border width
#: and prove nothing about the region.
MEASURE_REGIONS = """
() => Array.from(document.querySelectorAll('[data-mvp-chart-region]')).map(
  (region) => ({
    id: region.id,
    state: region.dataset.mvpChartRegionState,
    region: { width: region.offsetWidth, height: region.offsetHeight },
    wrapper: {
      width: region.parentElement.clientWidth,
      height: region.parentElement.clientHeight,
    },
  })
)
"""


@pytest.fixture
def chart_region_measurements(chromium, live_server, page):
    """The regions on the demo's chart region page that can draw, measured.

    The page also carries a region whose wrapper deliberately resolves to no
    height, to show what that state looks like. It is excluded here: it is
    reporting rather than drawing, and it is given a readable minimum height
    to say so, which is the one case where a region is *not* its wrapper.
    `TestTheReportingRegionIsExcludedOnPurpose` asserts it is really there,
    so this filter cannot quietly empty the list.
    """
    page.goto(f"{live_server.url}/chart-region/")
    page.wait_for_function(
        "() => Array.from(document.querySelectorAll('[data-mvp-chart-region]'))"
        ".every((r) => r.dataset.mvpChartRegionState)",
        timeout=5000,
    )
    measured = page.evaluate(MEASURE_REGIONS)
    return [m for m in measured if m["state"] == "ready"]


class TestRegionFillsItsWrapper:
    """T007: the region's box is its wrapper's box, measured rather than asserted."""

    def test_every_drawable_region_on_the_page_was_measured(
        self, chart_region_measurements
    ):
        """Guards the rest of the class against passing on an empty page.

        Every assertion below is over a list. A page that failed to render its
        regions would give an empty one, and every loop over it would be
        vacuously true.
        """
        assert len(chart_region_measurements) == 5

    def test_each_region_is_exactly_its_wrapper(self, chart_region_measurements):
        for measured in chart_region_measurements:
            assert measured["region"] == measured["wrapper"], measured["id"]

    def test_the_wrappers_are_genuinely_different_sizes(
        self, chart_region_measurements
    ):
        """Five regions that happened to be identical would prove much less.

        The page sizes its wrappers at five different heights on purpose, so
        the measurement above holds across sizes rather than at one of them.
        """
        heights = {m["wrapper"]["height"] for m in chart_region_measurements}
        assert len(heights) == 5

    def test_no_region_has_collapsed(self, chart_region_measurements):
        """A region matching a wrapper that is itself nothing is not a pass."""
        for measured in chart_region_measurements:
            assert measured["region"]["height"] > 0, measured["id"]
            assert measured["region"]["width"] > 0, measured["id"]


#: The demo's wrappers carry a one-pixel border on every side, so a wrapper
#: styled to 420px gives the region 418px to fill. The region filling its
#: wrapper's *inner* box is the contract, and this is what turns that into a
#: number a test can assert.
WRAPPER_BORDER = 2

RESIZE_FIRST_WRAPPER = (
    "() => {{ document.querySelector('[data-mvp-chart-region]')"
    ".parentElement.style.height = '{height}px'; }}"
)

#: Record every resize event a region dispatches, so a test can count them as
#: well as read the last one. Installed before the size is changed.
RECORD_RESIZES = """
() => {
  window.__resizes = [];
  document.querySelectorAll('[data-mvp-chart-region]').forEach((region) => {
    region.addEventListener('mvp-chart-region:resize', (event) => {
      window.__resizes.push({ id: region.id, ...event.detail });
    });
  });
}
"""


class TestHoldsItsShape:
    """T019-T022: the region tracks its wrapper through everything a page does."""

    @pytest.fixture
    def page_with_regions(self, chromium, live_server, page):
        page.goto(f"{live_server.url}/chart-region/")
        page.wait_for_selector("[data-mvp-chart-region]", timeout=5000)
        page.evaluate(RECORD_RESIZES)
        return page

    @staticmethod
    def measure(page):
        return page.evaluate(MEASURE_REGIONS)

    def test_a_window_resize_leaves_every_region_filling_its_wrapper(
        self, page_with_regions
    ):
        page_with_regions.set_viewport_size({"width": 700, "height": 900})
        page_with_regions.wait_for_timeout(200)
        for measured in self.measure(page_with_regions):
            assert measured["region"] == measured["wrapper"], measured["id"]

    def test_the_viewport_change_really_changed_the_layout(self, page_with_regions):
        """Otherwise the test above would pass by resizing nothing."""
        before = self.measure(page_with_regions)[0]["wrapper"]["width"]
        page_with_regions.set_viewport_size({"width": 700, "height": 900})
        page_with_regions.wait_for_timeout(200)
        after = self.measure(page_with_regions)[0]["wrapper"]["width"]
        assert after != before

    def test_a_wrapper_resized_without_the_window_changing_is_followed(
        self, page_with_regions
    ):
        """No window change, so nothing but the wrapper told the region."""
        before = self.measure(page_with_regions)[0]["region"]["height"]
        page_with_regions.evaluate(RESIZE_FIRST_WRAPPER.format(height=420))
        page_with_regions.wait_for_timeout(200)
        first = self.measure(page_with_regions)[0]
        assert first["region"]["height"] != before
        assert first["region"] == first["wrapper"]
        assert first["region"]["height"] == 420 - WRAPPER_BORDER

    def test_the_resize_event_carries_the_new_box(self, page_with_regions):
        """The contract a chart type will subscribe to, before one exists."""
        settled = 420 - WRAPPER_BORDER
        page_with_regions.evaluate(RESIZE_FIRST_WRAPPER.format(height=420))
        page_with_regions.wait_for_function(
            f"() => window.__resizes.some((r) => r.height === {settled})",
            timeout=5000,
        )
        last = page_with_regions.evaluate("() => window.__resizes.pop()")
        assert last["height"] == settled
        assert last["width"] > 0
        assert last["id"] == self.measure(page_with_regions)[0]["id"]

    def test_only_the_region_that_changed_reports(self, page_with_regions):
        """Five regions on the page, one resized, four silent."""
        page_with_regions.evaluate("() => { window.__resizes.length = 0; }")
        page_with_regions.evaluate(RESIZE_FIRST_WRAPPER.format(height=420))
        page_with_regions.wait_for_function(
            "() => window.__resizes.length > 0", timeout=5000
        )
        page_with_regions.wait_for_timeout(200)
        reporters = page_with_regions.evaluate(
            "() => [...new Set(window.__resizes.map((r) => r.id))]"
        )
        assert len(reporters) == 1

    def test_a_burst_of_changes_settles_once_at_the_final_size(self, page_with_regions):
        """A drag-resize must not queue one redraw per event.

        Thirty size changes inside a few frames; the region reports far fewer
        times than that and ends at the last size, not at one it passed
        through on the way.

        What this does *not* prove is that the package is what coalesces
        them. It was written against a hand-rolled batching layer, and it
        passed unchanged when that layer was deleted, because
        ``ResizeObserver`` already delivers at most one callback per frame.
        The requirement is the browser's to keep; this is what would notice
        if a future change started doing the work per event instead.
        """
        page_with_regions.evaluate("() => { window.__resizes.length = 0; }")
        page_with_regions.evaluate(
            """() => {
              const wrapper = document.querySelector('[data-mvp-chart-region]')
                .parentElement;
              for (let height = 200; height < 500; height += 10) {
                wrapper.style.height = height + 'px';
              }
            }"""
        )
        page_with_regions.wait_for_timeout(400)
        settled = 490 - WRAPPER_BORDER
        reported = page_with_regions.evaluate("() => window.__resizes")
        assert 0 < len(reported) <= 5
        assert reported[-1]["height"] == settled
        assert self.measure(page_with_regions)[0]["region"]["height"] == settled


class TestTheReportingRegionIsExcludedOnPurpose:
    """The page's deliberate no-height region, which the filter above drops.

    Without this, a change that stopped that region reporting would silently
    shrink what the measurements cover instead of failing anything.
    """

    def test_the_page_carries_one_region_reporting_no_height(
        self, chromium, live_server, page
    ):
        page.goto(f"{live_server.url}/chart-region/")
        page.wait_for_function(
            "() => Array.from(document.querySelectorAll('[data-mvp-chart-region]'))"
            ".filter((r) => r.dataset.mvpChartRegionState === 'no-height')"
            ".length === 1",
            timeout=5000,
        )

    def test_it_takes_enough_room_for_its_message_to_be_read(
        self, chromium, live_server, page
    ):
        page.goto(f"{live_server.url}/chart-region/")
        page.wait_for_function(
            "() => Array.from(document.querySelectorAll('[data-mvp-chart-region]'))"
            ".some((r) => r.dataset.mvpChartRegionState === 'no-height')",
            timeout=5000,
        )
        height = page.evaluate(
            "() => Array.from(document.querySelectorAll('[data-mvp-chart-region]'))"
            ".find((r) => r.dataset.mvpChartRegionState === 'no-height')"
            ".getBoundingClientRect().height"
        )
        assert height >= 48
