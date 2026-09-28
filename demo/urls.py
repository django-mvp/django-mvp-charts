"""URL routes for the demo project."""

from django.urls import include, path

from demo.views import ChartOptionsView, ChartTypesView, OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("chart-types/", ChartTypesView.as_view(), name="chart_types"),
    path("options/", ChartOptionsView.as_view(), name="chart_options"),
    path("__reload__/", include("django_browser_reload.urls")),
]
