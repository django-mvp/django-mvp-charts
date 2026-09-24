"""The demo project's pages, and the charts they draw.

Every chart on these pages is built here, in Python, the way a real view
builds one. The templates do nothing but place them.

Each chart has a builder function of its own rather than a few lines inside
``get_context_data``, so a page can show the code that built the chart beside
the chart itself. ``source_of`` reads it back off the function, which is what
stops the two saying different things: the listing on the page is the code
that ran, and a chart changed here changes what the page shows about it.
"""

import inspect
from datetime import date
from decimal import Decimal

from mvp.views import MVPTemplateView
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Pie, Scatter

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]


def source_of(builder):
    """The builder's own source, ready to put in a code block."""
    return inspect.getsource(builder).rstrip()


def revenue():
    """A line chart, the one the overview places."""
    return (
        Line().add_xaxis(MONTHS).add_yaxis("Revenue", [820, 932, 901, 934, 1290, 1330])
    )


def revenue_and_costs():
    """Two series on one line chart."""
    return (
        Line()
        .add_xaxis(MONTHS)
        .add_yaxis("Revenue", [820, 932, 901, 934, 1290, 1330])
        .add_yaxis("Costs", [620, 664, 701, 690, 810, 845])
    )


def orders_by_region():
    """A bar chart of four categories."""
    return (
        Bar()
        .add_xaxis(["North", "South", "East", "West"])
        .add_yaxis("Orders", [154, 121, 98, 187])
    )


def accounts_by_plan():
    """A pie chart, whose data is pairs rather than two axes."""
    return Pie().add("Plan", [("Free", 620), ("Team", 240), ("Enterprise", 86)])


def response_time():
    """A scatter chart, whose x axis is numbers rather than labels."""
    return (
        Scatter()
        .add_xaxis([12, 18, 24, 31, 37, 44, 52])
        .add_yaxis("Response time", [140, 162, 155, 210, 228, 301, 356])
    )


def conversion_rate():
    """Every appearance decision on this chart is made here, not on the tag."""
    return (
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


def invoiced():
    """The types a real view produces rather than the ones a demo would pick:
    dates, a Decimal out of a money column, and a gap in the data."""
    return (
        Line()
        .add_xaxis([date(2026, 1, 1), date(2026, 2, 1), date(2026, 3, 1)])
        .add_yaxis("Invoiced", [Decimal("1420.50"), None, Decimal("1683.75")])
    )


def signups():
    """Built for SVG, which is chosen here like any other option. The
    tooltip's wording is set by the page's own script once the chart is
    drawn, because a JavaScript function cannot travel in the options."""
    return (
        Line(init_opts=opts.InitOpts(renderer="svg"))
        .add_xaxis(["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6"])
        .add_yaxis("Sign-ups", [40, 52, 49, 61, 70, 84])
    )


class OverviewView(MVPTemplateView):
    """What this package is, and how a chart gets onto a page."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "Charts built in Python, placed with one Cotton component"
    breadcrumbs = [{"text": "Overview"}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["revenue"] = revenue()
        return context


class ChartTypesView(MVPTemplateView):
    """One component, four chart types, each built in the view."""

    template_name = "demo/chart_types.html"
    page_title = "Chart types"
    page_subtitle = "One component places whatever pyecharts can build"
    breadcrumbs = [{"text": "Chart types"}]

    builders = {
        "line": revenue_and_costs,
        "bar": orders_by_region,
        "pie": accounts_by_plan,
        "scatter": response_time,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for name, builder in self.builders.items():
            context[name] = builder()
        context["source"] = {
            name: source_of(builder) for name, builder in self.builders.items()
        }
        return context


class ChartOptionsView(MVPTemplateView):
    """Every ECharts option, reached in Python rather than through the tag."""

    template_name = "demo/chart_options.html"
    page_title = "Options"
    page_subtitle = "The whole option surface, set where the chart is built"
    breadcrumbs = [{"text": "Options"}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["styled"] = conversion_rate()
        context["awkward"] = invoiced()
        context["signups"] = signups()
        context["source"] = {
            "styled": source_of(conversion_rate),
            "awkward": source_of(invoiced),
            "signups": source_of(signups),
        }
        return context
