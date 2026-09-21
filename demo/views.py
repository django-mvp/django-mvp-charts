from mvp.views import MVPTemplateView


class OverviewView(MVPTemplateView):
    """What this package is, and where the chart pages will appear."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "Charts as Cotton components, one namespace per charting library"
    breadcrumbs = [{"text": "Overview"}]
