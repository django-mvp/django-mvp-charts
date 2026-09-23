"""The demo project's pages, and the charts they draw.

Every chart on these pages is built here, in Python, the way a real view
builds one. The templates do nothing but place them.
"""

from datetime import date
from decimal import Decimal

from mvp.views import MVPTemplateView
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, Scatter

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]


class OverviewView(MVPTemplateView):
    """What this package is, and how a chart gets onto a page."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "Charts built in Python, placed with one Cotton component"
    breadcrumbs = [{"text": "Overview"}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["revenue"] = (
            Line()
            .add_xaxis(MONTHS)
            .add_yaxis("Revenue", [820, 932, 901, 934, 1290, 1330])
        )
        return context


class ChartTypesView(MVPTemplateView):
    """One component, four chart types, each built in the view."""

    template_name = "demo/chart_types.html"
    page_title = "Chart types"
    page_subtitle = "One component places whatever pyecharts can build"
    breadcrumbs = [{"text": "Chart types"}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["line"] = (
            Line()
            .add_xaxis(MONTHS)
            .add_yaxis("Revenue", [820, 932, 901, 934, 1290, 1330])
            .add_yaxis("Costs", [620, 664, 701, 690, 810, 845])
        )
        context["bar"] = (
            Bar()
            .add_xaxis(["North", "South", "East", "West"])
            .add_yaxis("Orders", [154, 121, 98, 187])
        )
        context["pie"] = Pie().add(
            "Plan",
            [("Free", 620), ("Team", 240), ("Enterprise", 86)],
        )
        context["scatter"] = (
            Scatter()
            .add_xaxis([12, 18, 24, 31, 37, 44, 52])
            .add_yaxis("Response time", [140, 162, 155, 210, 228, 301, 356])
        )
        return context


class ChartOptionsView(MVPTemplateView):
    """Every ECharts option, reached in Python rather than through the tag."""

    template_name = "demo/chart_options.html"
    page_title = "Options"
    page_subtitle = "The whole option surface, set where the chart is built"
    breadcrumbs = [{"text": "Options"}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["styled"] = (
            Line()
            .add_xaxis(MONTHS)
            .add_yaxis(
                "Conversion rate",
                [2.1, 2.4, 2.2, 2.8, 3.1, 3.4],
                is_smooth=True,
                linestyle_opts=opts.LineStyleOpts(width=3, color="#7c3aed"),
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Conversion rate", subtitle="Per cent"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(formatter="{value}%")
                ),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
            )
        )
        # The types a real view produces rather than the ones a demo would
        # pick: dates, a Decimal out of a money column, and a gap in the data.
        context["awkward"] = (
            Line()
            .add_xaxis([date(2026, 1, 1), date(2026, 2, 1), date(2026, 3, 1)])
            .add_yaxis("Invoiced", [Decimal("1420.50"), None, Decimal("1683.75")])
        )
        return context
