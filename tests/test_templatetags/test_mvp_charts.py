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
