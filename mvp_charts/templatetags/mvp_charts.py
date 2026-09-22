"""Template tags chart regions and chart types share on one page.

Grouped on one class per Article XI: the per-request identity a region needs and
the once-per-page asset tags a page needs are both facts about the same subject —
what this request has already rendered — so they live together.
"""

from decimal import Decimal
from typing import Any

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.templatetags.static import static
from django.utils.html import format_html, json_script
from django.utils.safestring import SafeString

from mvp_charts import versions
from mvp_charts.config import MVP_CHARTS_CONFIG
from mvp_charts.echarts.options import CHART_TYPES, Chart

register = template.Library()


class ChartJSONEncoder(DjangoJSONEncoder):
    """Django's encoder, except that a Decimal comes out as a number.

    Django writes a Decimal as a string, which is right for a REST payload and
    wrong for a chart: a value axis given "12.45" plots a category called
    "12.45" rather than a point at 12.45, and the chart is subtly wrong rather
    than visibly broken. Money and measurements are the two things most likely
    to reach a chart as Decimals, so this is the ordinary case, not an edge.

    Dates, times and UUIDs keep Django's own handling, which is already what a
    chart wants.
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


class ChartRegionAssets:
    """Per-request identity and asset bookkeeping for one page's charts."""

    #: What a region needs in the browser, whether or not anything draws in it.
    region_module = "mvp_charts/js/chart-region.js"

    #: What draws with ECharts. Requested only by a region that has a chart, so
    #: a page using regions alone still asks for nothing it does not use.
    echarts_module = "mvp_charts/js/echarts.js"

    def __init__(self) -> None:
        self.region_count = 0
        self.emitted: set[str] = set()

    def next_region_id(self) -> str:
        """The next id in this request's sequence: `mvp-chart-region-1`, then `-2`, …"""
        self.region_count += 1
        return f"mvp-chart-region-{self.region_count}"

    def module_tag(self, path: str) -> SafeString:
        """A module's script tag the first time it is asked for, then nothing.

        Five regions on a page need the module once, not five times, and a page
        carrying no region at all must not request it — which is what makes
        installing this package cost a page that uses nothing from it nothing at
        all. Each component asks as it renders, so both follow from the same
        call rather than from anyone remembering a rule.
        """
        if path in self.emitted:
            return SafeString("")
        self.emitted.add(path)
        return format_html('<script defer src="{}"></script>', static(path))

    @classmethod
    def for_request(cls, request) -> "ChartRegionAssets":
        """The one instance for this request, created on first use."""
        assets = getattr(request, "mvp_chart_region_assets", None)
        if assets is None:
            assets = cls()
            request.mvp_chart_region_assets = assets
        return assets


class RenderedChart:
    """What a chart component hands to its own template.

    One object rather than five loose context variables, because the id, the
    script that carries the options and the element that reads them all have to
    agree with each other, and agreeing is easier when one thing decides them.
    """

    def __init__(self, chart: Chart, region_id: str) -> None:
        self.chart = chart
        self.id = region_id
        self.script_id = f"{region_id}-options"

    @property
    def name(self) -> str:
        return self.chart.name

    @property
    def description(self) -> str:
        return self.chart.description

    @property
    def script(self) -> SafeString:
        """The options, as a JSON script element the browser reads.

        `json_script` rather than an attribute or an inline assignment: it is
        Django's own answer to putting data in a page, it escapes the characters
        that can end a script element early, and it keeps a chart's
        configuration out of the markup where a long series would drown it.

        `DjangoJSONEncoder` is what lets a view pass the values it actually has
        — dates, times, decimals — without converting them first.

        The renderer rides along beside the options rather than being read in
        the browser, because it is an argument to `echarts.init` and not one of
        the options at all. It is a project setting, so every chart on a page
        carries the same answer.
        """
        payload: dict[str, Any] = {
            "renderer": MVP_CHARTS_CONFIG["echarts"]["renderer"],
            "options": self.chart.options(),
        }
        return json_script(payload, self.script_id, encoder=ChartJSONEncoder)


@register.simple_tag(takes_context=True)
def chart_region_id(context):
    """The next per-request region id, for a region the author did not name one for."""
    return ChartRegionAssets.for_request(context.request).next_region_id()


@register.simple_tag
def echarts_cdn():
    """Where `<c-echarts.cdn />` loads ECharts from, and the hash it must match.

    A template cannot read a Python constant, and these three values have to
    agree with each other — a URL whose version no longer matches its hash is a
    script the browser silently refuses. Handing the template one object from
    one source keeps them from drifting apart in the markup.

    Standalone rather than a method on `ChartRegionAssets`: this is a fact about
    the package, identical on every request, and has nothing to do with the
    regions on this page.
    """
    return {
        "url": versions.ECHARTS_CDN_URL,
        "integrity": versions.ECHARTS_CDN_INTEGRITY,
        "version": versions.ECHARTS_CDN_VERSION,
    }


@register.simple_tag(takes_context=True)
def chart_region_assets(context):
    """The region module's script tag, once per request, for the first region."""
    assets = ChartRegionAssets.for_request(context.request)
    return assets.module_tag(assets.region_module)


@register.simple_tag(takes_context=True)
def echarts_assets(context):
    """The drawing module's script tag, once per request, for the first chart."""
    assets = ChartRegionAssets.for_request(context.request)
    return assets.module_tag(assets.echarts_module)


@register.simple_tag(takes_context=True)
def echarts_chart(context, chart_type, **attrs):
    """Build one chart from the attributes written on its component tag.

    The component templates are four thin wrappers over this, which is what
    keeps the vocabulary identical across them: there is one place where a
    `config` object and a tag attribute are reconciled, and one place where the
    id the region uses and the id the script carries are decided.
    """
    region_id = (
        attrs.pop("id", "")
        or ChartRegionAssets.for_request(context.request).next_region_id()
    )
    chart = CHART_TYPES[chart_type].build(**attrs)
    return RenderedChart(chart, region_id)
