from django.views.generic import TemplateView
from mvp.views import MVPTemplateView


class OverviewView(MVPTemplateView):
    """What this package is, and where the chart pages will appear."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "Charts as Cotton components, one namespace per charting library"
    breadcrumbs = [{"text": "Overview"}]


class ChartRegionView(MVPTemplateView):
    """Placing a chart region, and several of them on one page."""

    template_name = "demo/chart_region.html"
    page_title = "Chart region"
    page_subtitle = (
        "The space a chart draws into, and how it behaves when nothing draws"
    )
    breadcrumbs = [{"text": "Chart region"}]


class ChartRegionNoLibraryView(TemplateView):
    """One region on a page with no charting library, for the frame above.

    Not in the navigation and not a page anyone visits. The check for the
    library reads a global, so it is a fact about the whole document — the
    only way to show that state beside a working one is to put it in a
    document of its own and embed it.
    """

    template_name = "demo/chart_region_no_library.html"
