from django.urls import path

from demo.views import ChartRegionView, OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("chart-region/", ChartRegionView.as_view(), name="chart_region"),
]
