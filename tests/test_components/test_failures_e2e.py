"""What a region does when it cannot draw, measured in a browser.

The wording of both messages is server-rendered and asserted without a
browser, in test_region.py. What only a browser can show is *when* each one
appears, and — for the height check — that a region tells a setup mistake
apart from a panel the reader closed. Those two states measure identically
and mean opposite things.
"""

import pytest

MESSAGE_TEXT = """
() => {
  const surface = document.querySelector('[data-mvp-chart-region-surface]');
  return surface ? surface.textContent.trim() : null;
}
"""

REGION_STATE = """
() => {
  const region = document.querySelector('[data-mvp-chart-region]');
  return region ? region.dataset.mvpChartRegionState : null;
}
"""


@pytest.fixture
def failure_page(chromium_or_skip, live_server, page):
    """Open a probe page for one failure case."""

    def open_case(case):
        page.goto(f"{live_server.url}/probe/failures/{case}/")
        return page

    return open_case


class TestMissingLibrary:
    """T013: a library that never arrives is reported in the page."""

    def test_the_region_waits_before_it_judges(self, failure_page):
        """A bundle still loading must not be accused of not existing."""
        page = failure_page("no-library")
        assert page.evaluate(REGION_STATE) == "waiting"
        assert page.evaluate(MESSAGE_TEXT) == ""

    def test_it_reports_once_waiting_is_no_longer_reasonable(self, failure_page):
        page = failure_page("no-library")
        page.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'missing-library'",
            timeout=15000,
        )
        assert "No charting library" in page.evaluate(MESSAGE_TEXT)

    def test_the_message_names_both_ways_to_supply_the_library(self, failure_page):
        """In the page, where someone looking at the blank can read it."""
        page = failure_page("no-library")
        page.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'missing-library'",
            timeout=15000,
        )
        message = page.evaluate(MESSAGE_TEXT)
        assert "c-echarts.cdn" in message
        assert "window.echarts" in message


class TestNoResolvedHeight:
    """T015: a wrapper that gives a region no height is reported, readably."""

    def test_it_is_reported(self, failure_page):
        page = failure_page("no-height")
        page.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'no-height'",
            timeout=5000,
        )
        assert "No height to fill" in page.evaluate(MESSAGE_TEXT)

    def test_the_region_takes_enough_room_for_the_message_to_be_read(
        self, failure_page
    ):
        """A message inside a box of no height is the blank it replaced."""
        page = failure_page("no-height")
        page.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'no-height'",
            timeout=5000,
        )
        height = page.evaluate(
            "() => document.querySelector('[data-mvp-chart-region]')"
            ".getBoundingClientRect().height"
        )
        assert height >= 48

    def test_the_message_is_actually_visible(self, failure_page):
        page = failure_page("no-height")
        page.wait_for_selector(
            "[data-mvp-chart-region-surface] p", state="visible", timeout=5000
        )


class TestHeightIsJudgedAtFirstVisibility:
    """T016, T021: hidden is not a mistake, and neither is a panel closing."""

    def test_a_region_hidden_at_load_is_not_reported(self, failure_page):
        """A collapsed panel or an unselected tab is an ordinary page."""
        page = failure_page("hidden-then-revealed")
        page.wait_for_timeout(300)
        assert page.evaluate(REGION_STATE) != "no-height"

    def test_it_is_judged_when_it_is_revealed(self, failure_page):
        page = failure_page("hidden-then-revealed")
        page.evaluate("() => { document.getElementById('panel').style.display = ''; }")
        page.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'ready'",
            timeout=5000,
        )
        assert page.evaluate(MESSAGE_TEXT) == ""

    def test_a_region_that_loses_its_height_later_reports_nothing(self, failure_page):
        """The page working as designed, not a setup mistake.

        Without this distinction, surviving a collapsing panel and reporting a
        collapsed region contradict each other.
        """
        page = failure_page("collapses-later")
        page.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'ready'",
            timeout=5000,
        )
        page.evaluate(
            "() => { document.getElementById('panel').style.height = '0px'; }"
        )
        page.wait_for_timeout(300)
        assert page.evaluate(REGION_STATE) == "ready"
        assert page.evaluate(MESSAGE_TEXT) == ""

    def test_it_recovers_when_the_space_comes_back(self, failure_page):
        page = failure_page("collapses-later")
        page.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'ready'",
            timeout=5000,
        )
        page.evaluate(
            "() => { document.getElementById('panel').style.height = '0px'; }"
        )
        page.wait_for_timeout(200)
        page.evaluate(
            "() => { document.getElementById('panel').style.height = '240px'; }"
        )
        page.wait_for_timeout(200)
        height = page.evaluate(
            "() => document.querySelector('[data-mvp-chart-region]')"
            ".getBoundingClientRect().height"
        )
        assert height == 240


class TestOneFailingRegionLeavesTheOthers:
    """T017: a page does not lose its working charts to one broken one."""

    def test_the_failing_region_reports_and_the_others_do_not(self, failure_page):
        page = failure_page("mixed")
        page.evaluate("() => { window.echarts = { version: 'stand-in' }; }")
        page.wait_for_function(
            "() => document.querySelectorAll('[data-mvp-chart-region]').length === 3",
            timeout=5000,
        )
        page.wait_for_function(
            "() => Array.from(document.querySelectorAll('[data-mvp-chart-region]'))"
            ".filter((r) => r.dataset.mvpChartRegionState === 'ready').length === 2",
            timeout=5000,
        )
        states = page.evaluate(
            "() => Array.from(document.querySelectorAll('[data-mvp-chart-region]'))"
            ".map((r) => r.dataset.mvpChartRegionState)"
        )
        assert states[0] == "no-height"
        assert states[1:] == ["ready", "ready"]

    def test_the_working_regions_still_fill_their_wrappers(self, failure_page):
        page = failure_page("mixed")
        page.evaluate("() => { window.echarts = { version: 'stand-in' }; }")
        page.wait_for_function(
            "() => Array.from(document.querySelectorAll('[data-mvp-chart-region]'))"
            ".filter((r) => r.dataset.mvpChartRegionState === 'ready').length === 2",
            timeout=5000,
        )
        measured = page.evaluate(
            "() => Array.from(document.querySelectorAll('[data-mvp-chart-region]'))"
            ".slice(1).map((r) => [r.offsetHeight, r.parentElement.clientHeight])"
        )
        assert measured == [[200, 200], [160, 160]]


class TestNothingKeepsRunningAfterwards:
    """A page left open must not keep waking the browser.

    The wait for a late library is a poll, and every path out of it has to
    clear that poll. The one that did not was a region reporting no height on
    a page with no library: it never draws whatever the library does, so
    nothing was ever going to stop the timer. It is invisible in the page,
    which is why it is counted here rather than looked for.
    """

    @pytest.fixture
    def counted_timers(self, chromium_or_skip, live_server, page):
        """Count intervals that are started and never cleared."""
        page.add_init_script(
            """
            window.__liveIntervals = new Set();
            const start = window.setInterval;
            const stop = window.clearInterval;
            window.setInterval = function (...args) {
              const handle = start.apply(window, args);
              window.__liveIntervals.add(handle);
              return handle;
            };
            window.clearInterval = function (handle) {
              window.__liveIntervals.delete(handle);
              return stop.call(window, handle);
            };
            """
        )
        return page

    def test_the_library_poll_stops_when_a_region_reports_no_height(
        self, counted_timers, live_server
    ):
        """No library *and* no height: the case with nothing left to stop it.

        The height alone does not start a poll, and the library alone stops
        its own on arrival. Only a region that has both problems reaches the
        path where the timer had no owner.
        """
        counted_timers.goto(f"{live_server.url}/probe/failures/neither/")
        counted_timers.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'no-height'",
            timeout=5000,
        )
        counted_timers.wait_for_function(
            "() => window.__liveIntervals.size === 0", timeout=15000
        )

    def test_the_library_poll_stops_once_a_missing_library_is_reported(
        self, counted_timers, live_server
    ):
        counted_timers.goto(f"{live_server.url}/probe/failures/no-library/")
        counted_timers.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'missing-library'",
            timeout=15000,
        )
        assert counted_timers.evaluate("() => window.__liveIntervals.size") == 0
