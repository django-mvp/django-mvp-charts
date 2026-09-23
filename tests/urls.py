from django.urls import include, path
from django.views.generic import TemplateView
from pyecharts.charts import Line

# The demo project's routes, behind a urlconf of the suite's own so a route
# that exists only to exercise a component has somewhere to go.


class NoLibraryProbe(TemplateView):
    """One chart on a page that never loads a charting library.

    A page built to put the component in one exact situation a browser test
    needs, which no page a reader would visit should have to contort itself
    into.
    """

    template_name = "probe/no_library.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chart"] = Line().add_xaxis(["a", "b"]).add_yaxis("s", [1, 2])
        return context


urlpatterns = [
    path("probe/no-library/", NoLibraryProbe.as_view(), name="probe_no_library"),
    path("", include("demo.urls")),
]
