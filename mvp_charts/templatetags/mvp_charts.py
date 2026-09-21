"""Template tags chart regions share on one page.

Grouped on one class per Article XI: the per-request identity a region needs
and the once-per-page asset tag it will need in US2 are both facts about the
same subject — the regions on this request — so they live together even
though this story only needs the first of the two.
"""

from django import template
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import SafeString

from mvp_charts import versions

register = template.Library()


class ChartRegionAssets:
    """Per-request identity for the chart regions on one page."""

    #: The package's own module, which every region on a page shares.
    module_path = "mvp_charts/js/chart-region.js"

    def __init__(self) -> None:
        self.region_count = 0
        self.module_emitted = False

    def next_region_id(self) -> str:
        """The next id in this request's sequence: `mvp-chart-region-1`, then `-2`, …"""
        self.region_count += 1
        return f"mvp-chart-region-{self.region_count}"

    def module_tag(self) -> SafeString:
        """The module's script tag the first time it is asked for, then nothing.

        Five regions on a page need the module once, not five times, and a
        page carrying no region at all must not request it — which is what
        makes installing this package cost a page that uses nothing from it
        nothing at all. The region asks for this as it renders, so both follow
        from the same call rather than from anyone remembering a rule.
        """
        if self.module_emitted:
            return SafeString("")
        self.module_emitted = True
        return format_html('<script defer src="{}"></script>', static(self.module_path))

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


@register.simple_tag
def echarts_cdn():
    """Where `<c-echarts.cdn />` loads ECharts from, and the hash it must match.

    A template cannot read a Python constant, and these three values have to
    agree with each other — a URL whose version no longer matches its hash is
    a script the browser silently refuses. Handing the template one object
    from one source keeps them from drifting apart in the markup.

    Standalone rather than a method on `ChartRegionAssets`: this is a fact
    about the package, identical on every request, and has nothing to do with
    the regions on this page.
    """
    return {
        "url": versions.ECHARTS_CDN_URL,
        "integrity": versions.ECHARTS_CDN_INTEGRITY,
        "version": versions.ECHARTS_CDN_VERSION,
    }


@register.simple_tag(takes_context=True)
def chart_region_assets(context):
    """The module's script tag, once per request, for the first region that asks."""
    return ChartRegionAssets.for_request(context.request).module_tag()
