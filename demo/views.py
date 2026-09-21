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
    page_subtitle = "The space a chart draws into, sized by the element around it"
    breadcrumbs = [{"text": "Charts"}, {"text": "Chart region"}]
