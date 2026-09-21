from django.urls import include, path
from django.views.generic import TemplateView

# The demo project's routes, behind a urlconf of the suite's own so a route
# that exists only to exercise a component has somewhere to go.
#
# The probe routes below are that: pages built to put a component in one
# exact situation a browser test needs, which no page a reader would visit
# should have to contort itself into.
urlpatterns = [
    path(
        "probe/delivery/<str:route>/",
        TemplateView.as_view(template_name="probe/delivery.html"),
        name="probe_delivery",
    ),
    path(
        "probe/failures/<str:case>/",
        TemplateView.as_view(template_name="probe/failures.html"),
        name="probe_failures",
    ),
    path(
        "probe/no-region/",
        TemplateView.as_view(template_name="probe/no_region.html"),
        name="probe_no_region",
    ),
    path("", include("demo.urls")),
]
