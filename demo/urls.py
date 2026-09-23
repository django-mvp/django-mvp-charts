from django.urls import include, path

from demo.views import (
    ChartRegionNoLibraryView,
    ChartRegionView,
    LineChartView,
    OverviewView,
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
    path("line/", LineChartView.as_view(), name="line_chart"),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
