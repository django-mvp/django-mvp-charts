"""The demo project, which is where the components get looked at as they land.

It is tested for the same reason ``test_app.py`` tests the template directory:
everything here fails quietly. A Cotton component that cannot be resolved
renders as empty output, a Tailwind class the packaged stylesheet does not emit
does nothing, and a navigation entry whose URL will not resolve is dropped from
the sidebar. None of that raises, so none of it shows up anywhere except in a
browser.
"""

import re

import pytest
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse


class TestOverviewPage:
    """The page a reader lands on, and the shell it is drawn inside."""

    def test_page_is_served(self, client, db):
        assert client.get("/").status_code == 200

    def test_page_is_drawn_inside_the_application_shell(self, overview_page):
        """The sidebar and the header, not a hand-rolled document.

        The breadcrumb trail is the header's, drawn from what the view
        declares, so its presence says the header is there and reading the
        page rather than merely that some markup rendered.
        """
        assert "<aside" in overview_page
        assert 'aria-label="Main navigation"' in overview_page
        assert 'aria-label="Breadcrumbs"' in overview_page
        assert '<span class="mvp-breadcrumb-text">Overview</span>' in overview_page

    def test_title_names_the_page_and_the_site(self, overview_page):
        title = re.search(r"<title>(.*?)</title>", overview_page, re.S).group(1)
        assert " ".join(title.split()) == "Overview | django-mvp-charts"

    def test_page_heading_is_the_page_title(self, overview_page):
        assert re.search(r"<h1[^>]*>\s*Overview\s*</h1>", overview_page)

    def test_page_explains_what_the_package_is(self, overview_page):
        """The one thing the page exists to do."""
        assert "&lt;c-echarts.line&gt;" in overview_page
        assert "Apache ECharts" in overview_page


class TestSidebarMenu:
    """What the navigation holds, which is exactly the pages that exist."""

    def test_the_overview_page_is_linked(self, sidebar_navigation):
        assert "<span>Overview</span>" in sidebar_navigation
        assert 'href="/"' in sidebar_navigation

    def test_the_charts_section_holds_exactly_the_chart_pages(self, sidebar_navigation):
        """The sidebar holds the pages that exist and nothing else.

        One chart page exists, so the Charts section holds one entry. This
        started out asserting the sidebar held only Overview, which was the
        same claim while ``CHART_PAGES`` was empty.
        """
        assert "Charts</span>" in sidebar_navigation
        assert "<span>Chart region</span>" in sidebar_navigation
        assert re.findall(r'href="([^"]*)"', sidebar_navigation) == [
            "/",
            "/chart-region/",
        ]

    def test_no_section_is_drawn_with_nothing_under_it(self, overview_page):
        """A container added before it has children renders as a dead control.

        django-mvp draws a navigation node from its leaf template until it has
        children, so a section declared while its page list is empty reaches
        the page as a button carrying ``href="None"``. This is what keeps that
        from being reintroduced without anyone noticing — it is why the Charts
        section is conditional on holding a page, and it stays true now that
        it holds one.
        """
        assert 'href="None"' not in overview_page


class TestDocumentationSurface:
    """``{% show_code %}`` and the template it renders its examples through."""

    def test_the_tag_has_a_display_template(self):
        """django-mvp ships the tag but not the template it renders through.

        A project that calls the tag without supplying one gets
        ``TemplateDoesNotExist`` at render time, so this repo provides its own
        under ``demo/templates/``. Reported upstream.
        """
        try:
            get_template("cotton/documentation.html")
        except TemplateDoesNotExist:  # pragma: no cover - the failure message
            pytest.fail(
                "cotton/documentation.html is missing, so {% show_code %} "
                "raises instead of rendering"
            )

    def test_the_example_shows_the_live_component(self, overview_page):
        assert '<h2 class="card-title">' in overview_page

    def test_the_example_shows_its_cotton_source(self, overview_page):
        assert "&lt;c-card title=&quot;Monthly revenue&quot;" in overview_page

    def test_the_example_shows_the_html_it_rendered_to(self, overview_page):
        assert "&lt;div class=&quot;card bg-base-100" in overview_page

    def test_the_html_is_prettified(self, overview_page):
        """The tag falls back to raw output when BeautifulSoup is absent.

        It does so silently, and raw Cotton output already carries line breaks
        and indentation of its own, so neither of those tells the two apart.
        What does is that the prettifier puts every closing tag on a line of
        its own, where the raw output keeps ``<span>text</span>`` inline.
        """
        panes = re.findall(r"<pre[^>]*><code>(.*?)</code></pre>", overview_page, re.S)
        assert len(panes) == 2
        html_pane = panes[1]
        assert re.search(r"\n\s*&lt;/span&gt;", html_pane)


class TestChartRegionPage:
    """T005: the demo shows a placed region, and the Charts section appears."""

    def test_the_page_is_served(self, client, db):
        assert client.get(reverse("chart_region")).status_code == 200

    def test_it_shows_a_region_inside_a_wrapper_with_a_visible_height(
        self, chart_region_page
    ):
        """The height is on the wrapper, and the reader can see that it is.

        It has to be visible twice: in the live example, where the browser
        needs it to give the region anything to fill, and in the source pane
        beside it, where a reader copying the example needs to see that the
        wrapper is carrying it. A region has no height of its own, so an
        example that hid the wrapper's would not be copyable.
        """
        assert "data-mvp-chart-region" in chart_region_page
        assert "height: 320px" in chart_region_page
        shown_source = re.sub(r"&quot;|&#39;", '"', chart_region_page)
        assert "height: 320px" in shown_source

    def test_it_shows_five_independent_regions(self, chart_region_page):
        ids = re.findall(r'<figure id="([^"]+)"', chart_region_page)
        assert len(ids) == 5
        assert len(set(ids)) == 5

    def test_every_region_describes_its_own_caption(self, chart_region_page):
        """Independence is what the ids are for, so assert what they buy.

        Five distinct ids prove nothing on their own: the failure this guards
        against is two regions on a page pointing at one caption, which counts
        the same and reads wrong to anyone using a screen reader.
        """
        pairs = re.findall(
            r'<figure id="([^"]+)".*?aria-describedby="([^"]+)"',
            chart_region_page,
            re.S,
        )
        assert len(pairs) == 5
        assert all(described == f"{region}-description" for region, described in pairs)

    def test_the_charts_section_carries_an_entry_for_the_page(self, chart_region_page):
        assert "Charts</span>" in chart_region_page
        assert 'href="/chart-region/"' in chart_region_page
        assert "Chart region</span>" in chart_region_page
