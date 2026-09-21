"""Tests for the per-request state chart regions share.

Renders the tag directly rather than through the component — the region's
own tests (tests/test_components/test_region.py) already cover the tag as
the component actually calls it.
"""

from django import template as dj_template
from django.template import RequestContext
from django.test import RequestFactory

rf = RequestFactory()


def render(source, request):
    return dj_template.Template(source).render(RequestContext(request))


TAG_SOURCE = "{% load mvp_charts %}{% chart_region_id %} {% chart_region_id %}"
ONE_TAG_SOURCE = "{% load mvp_charts %}{% chart_region_id %}"


class TestChartRegionId:
    """`{% chart_region_id %}` numbers regions within one request, and restarts for the next."""

    def test_ids_increment_within_one_request(self):
        first, second = render(TAG_SOURCE, rf.get("/")).split()
        assert first == "mvp-chart-region-1"
        assert second == "mvp-chart-region-2"

    def test_numbering_restarts_for_a_new_request(self):
        first_request_id = render(ONE_TAG_SOURCE, rf.get("/")).strip()
        second_request_id = render(ONE_TAG_SOURCE, rf.get("/")).strip()
        assert first_request_id == second_request_id == "mvp-chart-region-1"


ASSETS_SOURCE = (
    "{% load mvp_charts %}[{% chart_region_assets %}][{% chart_region_assets %}]"
)


class TestChartRegionAssets:
    """`{% chart_region_assets %}` emits the module once per request, not per region."""

    def test_the_first_call_emits_the_script_tag(self):
        first = render(ASSETS_SOURCE, rf.get("/")).split("][")[0]
        assert "chart-region.js" in first
        assert "<script" in first

    def test_every_later_call_in_the_same_request_emits_nothing(self):
        """Five regions on a page must not load the module five times."""
        second = render(ASSETS_SOURCE, rf.get("/")).split("][")[1]
        assert second.strip("]") == ""

    def test_a_new_request_emits_it_again(self):
        """The once-per-page rule is per page, not once per process."""
        for _ in range(2):
            assert "chart-region.js" in render(ASSETS_SOURCE, rf.get("/"))

    def test_the_module_is_deferred(self):
        """It reads the document, so it must not run before the document exists."""
        assert "defer" in render(ASSETS_SOURCE, rf.get("/"))

    def test_the_tag_is_never_the_thing_that_loads_the_charting_library(self):
        """Article XII: the package serves its own asset and nothing else."""
        emitted = render(ASSETS_SOURCE, rf.get("/"))
        assert "echarts" not in emitted.lower()
        assert "//" not in emitted.replace("<!--", "")
