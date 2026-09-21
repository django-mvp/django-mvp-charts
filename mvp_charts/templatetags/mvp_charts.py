"""Template tags chart regions share on one page.

Grouped on one class per Article XI: the per-request identity a region needs
and the once-per-page asset tag it will need in US2 are both facts about the
same subject — the regions on this request — so they live together even
though this story only needs the first of the two.
"""

from django import template

register = template.Library()


class ChartRegionAssets:
    """Per-request identity for the chart regions on one page."""

    def __init__(self) -> None:
        self.region_count = 0

    def next_region_id(self) -> str:
        """The next id in this request's sequence: `mvp-chart-region-1`, then `-2`, …"""
        self.region_count += 1
        return f"mvp-chart-region-{self.region_count}"

    @classmethod
    def for_request(cls, request) -> "ChartRegionAssets":
        """The one instance for this request, created on first use."""
        assets = getattr(request, "mvp_chart_region_assets", None)
        if assets is None:
            assets = cls()
            request.mvp_chart_region_assets = assets
        return assets


@register.simple_tag(takes_context=True)
def chart_region_id(context):
    """The next per-request region id, for a region the author did not name one for."""
    return ChartRegionAssets.for_request(context.request).next_region_id()
