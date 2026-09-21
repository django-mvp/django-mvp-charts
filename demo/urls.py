from django.urls import path

from demo.views import ChartRegionFailuresView, ChartRegionView, OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("chart-region/", ChartRegionView.as_view(), name="chart_region"),
    path(
        "chart-region/failures/",
        ChartRegionFailuresView.as_view(),
        name="chart_region_failures",
    ),
]
