from django.urls import path

from demo.views import (
    BarChartView,
    ChartRegionNoLibraryView,
    ChartRegionView,
    LineChartView,
    OverviewView,
    PieChartView,
    ScatterChartView,
)

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("chart-region/", ChartRegionView.as_view(), name="chart_region"),
    # Framed by the page above rather than visited. See ChartRegionNoLibraryView.
    path(
        "chart-region/no-library/",
        ChartRegionNoLibraryView.as_view(),
        name="chart_region_no_library",
    ),
    path("charts/line/", LineChartView.as_view(), name="line_chart"),
    path("charts/bar/", BarChartView.as_view(), name="bar_chart"),
    path("charts/pie/", PieChartView.as_view(), name="pie_chart"),
    path("charts/scatter/", ScatterChartView.as_view(), name="scatter_chart"),
]
