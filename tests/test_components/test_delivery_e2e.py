"""How the charting library reaches a region, measured in a browser.

The promise is that a region reads one global and never asks which route put
it there, so a project can load the library any way it likes and change its
mind without touching a setting. That is a claim about a running page, and
these tests put the same region on two pages that differ only in how the
library arrives.

What is deliberately not tested here: whether a public CDN is reachable. The
tag that loads the library belongs to the project, not to this package, and
fetching a third-party file during a test run would make the suite fail for
reasons that say nothing about anything here.
"""

import pytest

#: How the library comes to exist on the page, and nothing else differs.
#:
#: `separate-file` is a script tag fetching a file, which is what both a
#: public copy and a built bundle look like to a page. `inline-bundle` is an
#: assignment in the document, which is what a project inlining its bundle
#: looks like.
DELIVERY_ROUTES = ["separate-file", "inline-bundle"]

REGION_STATE = """
() => {
  const region = document.querySelector('[data-mvp-chart-region]');
  return region ? region.dataset.mvpChartRegionState : null;
}
"""


@pytest.fixture
def delivery_page(chromium, live_server, page):
    """Open a probe page for one delivery route and wait for the region to settle."""

    def open_route(route):
        page.goto(f"{live_server.url}/probe/delivery/{route}/")
        page.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'ready'",
            timeout=5000,
        )
        return page

    return open_route


class TestEitherRouteWorks:
    """T010: a region uses whatever supplies the library, with no setting either way."""

    @pytest.mark.parametrize("route", DELIVERY_ROUTES)
    def test_the_region_resolves_the_library(self, delivery_page, route):
        assert delivery_page(route).evaluate(REGION_STATE) == "ready"

    @pytest.mark.parametrize("route", DELIVERY_ROUTES)
    def test_the_library_is_reachable_from_the_page(self, delivery_page, route):
        assert delivery_page(route).evaluate("() => Boolean(window.echarts)")

    def test_the_two_pages_differ_only_in_how_the_library_arrived(self, delivery_page):
        """The point of the story, stated as an assertion.

        Same component, same markup, same absence of configuration — the only
        difference between these two pages is the route, and the region ends
        in the same state either way.
        """
        markup = {}
        for route in DELIVERY_ROUTES:
            page = delivery_page(route)
            markup[route] = page.evaluate(
                "() => document.querySelector('[data-mvp-chart-region]').outerHTML"
            )
        assert markup[DELIVERY_ROUTES[0]] == markup[DELIVERY_ROUTES[1]]


class TestALateBundleIsNotAFault:
    """T014: a library that arrives after the page does is ordinary, not an error."""

    def test_a_region_resolves_when_the_library_turns_up_later(
        self, chromium, live_server, page
    ):
        """A deferred or asynchronously loaded bundle is a normal project.

        The region must still be waiting when the page settles, and must
        resolve on its own once the library appears, without the page being
        touched again.
        """
        page.goto(f"{live_server.url}/probe/delivery/none/")
        assert page.evaluate(REGION_STATE) == "waiting"
        page.evaluate("() => { window.echarts = { version: 'late' }; }")
        page.wait_for_function(
            "() => document.querySelector('[data-mvp-chart-region]')"
            "?.dataset.mvpChartRegionState === 'ready'",
            timeout=5000,
        )
        assert page.evaluate(REGION_STATE) == "ready"


class TestNoThirdPartyOriginIsContacted:
    """A region fetches nothing, so whatever a page loads, the project asked for it.

    The probe page loads the package's module and a stand-in for the charting
    library, both from its own origin. A region reaching for a script of its
    own — the thing Article XII forbids — would show up here as an origin
    nobody in the template named.
    """

    def test_a_rendered_region_contacts_no_other_origin(
        self, chromium, live_server, page
    ):
        requested = []
        page.on("request", lambda request: requested.append(request.url))
        page.goto(f"{live_server.url}/probe/delivery/separate-file/")
        offsite = [url for url in requested if not url.startswith(live_server.url)]
        assert offsite == []
