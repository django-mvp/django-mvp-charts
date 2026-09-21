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
    region: { width: region.offsetWidth, height: region.offsetHeight },
    wrapper: {
      width: region.parentElement.clientWidth,
      height: region.parentElement.clientHeight,
    },
  })
)
"""


@pytest.fixture
def chart_region_measurements(chromium_or_skip, live_server, page):
    """Every region on the demo's chart region page, measured."""
    page.goto(f"{live_server.url}/chart-region/")
    return page.evaluate(MEASURE_REGIONS)


class TestRegionFillsItsWrapper:
    """T007: the region's box is its wrapper's box, measured rather than asserted."""

    def test_every_region_on_the_page_was_measured(self, chart_region_measurements):
        """Guards the rest of the class against passing on an empty page.

        Every assertion below is over a list. A page that failed to render its
        regions would give an empty one, and every ``all()`` over it would be
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
