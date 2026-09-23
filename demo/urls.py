from django.urls import include, path

from demo.views import ChartOptionsView, ChartTypesView, OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("chart-types/", ChartTypesView.as_view(), name="chart_types"),
    path("options/", ChartOptionsView.as_view(), name="chart_options"),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
