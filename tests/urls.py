from django.urls import include, path
from django.views.generic import TemplateView
from mvp.views import MVPTemplateView
from pyecharts import options as opts
from pyecharts.charts import Bar, Line

# The demo project's routes, behind a urlconf of the suite's own so a route
# that exists only to exercise a component has somewhere to go.
#
# The probe routes below are that: pages built to put the component in one
# exact situation a browser test needs, which no page a reader would visit
# should have to contort itself into.


def a_chart():
    return Line().add_xaxis(["a", "b"]).add_yaxis("s", [1, 2])


class NoLibraryProbe(TemplateView):
    """One chart on a page that never loads a charting library."""

    template_name = "probe/no_library.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chart"] = a_chart()
        return context


class SizingProbe(MVPTemplateView):
    """Charts in boxes that are not drawable when the page loads.

    On the application shell rather than a bare document, because every case
    here is about what the CSS resolves to, and django-mvp's stylesheet is
    what makes the component's own sizing classes mean anything.
    """

    template_name = "probe/sizing.html"
    page_title = "Sizing"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chart"] = a_chart()
        return context


class PlaceholderProbe(MVPTemplateView):
    """A chart holding its placeholder, because no library ever arrives.

    The state a reader sees for as long as the library takes to load, held
    still so it can be measured.
    """

    template_name = "probe/placeholder.html"
    page_title = "Placeholder"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["chart"] = a_chart()
        return context


class RendererProbe(MVPTemplateView):
    """Two charts that differ only in the renderer they were built with."""

    template_name = "probe/renderer.html"
    page_title = "Renderer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["svg_chart"] = (
            Line(init_opts=opts.InitOpts(renderer="svg"))
            .add_xaxis(["a", "b"])
            .add_yaxis("s", [1, 2])
        )
        context["canvas_chart"] = a_chart()
        return context


class PatternsProbe(MVPTemplateView):
    """Charts built with the documented call that turns decal patterns on."""

    template_name = "probe/patterns.html"
    page_title = "Patterns"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patterned_bar"] = (
            Bar(
                init_opts=opts.InitOpts(
                    aria_opts={
                        "enabled": True,
                        "label": {"enabled": False},
                        "decal": {"show": True},
                    }
                )
            )
            .add_xaxis(["North", "South", "East", "West"])
            .add_yaxis("Online", [154, 121, 98, 187])
            .add_yaxis("In store", [132, 140, 76, 96])
        )
        return context


urlpatterns = [
    path("probe/no-library/", NoLibraryProbe.as_view(), name="probe_no_library"),
    path("probe/sizing/", SizingProbe.as_view(), name="probe_sizing"),
    path("probe/placeholder/", PlaceholderProbe.as_view(), name="probe_placeholder"),
    path("probe/renderer/", RendererProbe.as_view(), name="probe_renderer"),
    path("probe/patterns/", PatternsProbe.as_view(), name="probe_patterns"),
    path("", include("demo.urls")),
]
