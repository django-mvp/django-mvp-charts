from django.urls import path

from demo.views import ChartRegionNoLibraryView, ChartRegionView, OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("chart-region/", ChartRegionView.as_view(), name="chart_region"),
    # Framed by the page above rather than visited. See ChartRegionNoLibraryView.
    path(
        "chart-region/no-library/",
        ChartRegionNoLibraryView.as_view(),
        name="chart_region_no_library",
    ),
]
