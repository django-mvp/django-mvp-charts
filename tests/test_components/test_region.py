"""Tests for <c-echarts.region>, the rendered-output contract.

Compiles Cotton source directly rather than going through a view, so this
file covers what the tag renders as markup: placement, per-request identity,
the missing-attribute guard and translation. tests/test_demo.py covers it as
the demo project actually serves it, and test_region_e2e.py covers what only
a real browser can measure.
"""

import re
from pathlib import Path

from django import template as dj_template
from django.template import RequestContext
from django.test import RequestFactory, override_settings
from django.utils import translation
from django_cotton.compiler_regex import CottonCompiler

compiler = CottonCompiler()
rf = RequestFactory()


def render(source, request=None, **context):
    """Compile a Cotton source string and render it against a request-backed context.

    A request-backed context is what the region's id generation needs: it
    comes from a `takes_context=True` tag that reads `context.request`.
    """
    request = request or rf.get("/")
    return dj_template.Template(compiler.process(source)).render(
        RequestContext(request, context)
    )


REGION = '<c-echarts.region name="{name}" description="{description}" />'
A_REGION = REGION.format(
    name="Monthly revenue", description="Revenue by month, in EUR."
)


class TestChartRegion:
    """A region fills its wrapper and carries its name and text alternative."""

    def test_the_region_is_a_figure_carrying_the_sizing_classes(self):
        html = render(A_REGION)
        figure = re.search(r"<figure[^>]*>", html)
        assert figure is not None
        assert "data-mvp-chart-region" in figure.group(0)
        assert re.search(r'class="relative h-full w-full"', figure.group(0))

    def test_the_drawing_surface_carries_the_accessible_name(self):
        html = render(A_REGION)
        surface = re.search(r"<div[^>]*data-mvp-chart-region-surface[^>]*>", html)
        assert surface is not None
        assert 'role="img"' in surface.group(0)
        assert 'aria-label="Monthly revenue"' in surface.group(0)

    def test_the_figcaption_carries_the_description_as_reachable_text(self):
        html = render(A_REGION)
        figcaption = re.search(
            r'<figcaption[^>]*class="sr-only"[^>]*>(.*?)</figcaption>', html
        )
        assert figcaption is not None
        assert figcaption.group(1).strip() == "Revenue by month, in EUR."

    def test_the_figure_and_the_surface_share_one_identity(self):
        """The figure's id, the surface's aria-describedby and the figcaption's id agree.

        The exact id scheme is not this test's subject (TestChartRegionIdentity
        below covers that) — this only proves the three elements are wired to
        each other consistently, whatever the id turns out to be.
        """
        html = render(A_REGION)
        figure_id = re.search(r'<figure id="([^"]+)"', html).group(1)
        surface = re.search(
            r"<div[^>]*data-mvp-chart-region-surface[^>]*>", html
        ).group(0)
        figcaption_id = re.search(r'<figcaption id="([^"]+)"', html).group(1)
        assert f'aria-describedby="{figure_id}-description"' in surface
        assert figcaption_id == f"{figure_id}-description"

    def test_the_author_writes_no_javascript_and_none_is_inlined(self):
        """The page author writes none, and the package inlines none.

        This began as "no script tag at all", which was the same claim while
        the region had no module to load. It has one now — the library check,
        the height check and the resize contract exist only in a browser — so
        the claim is restated at the level it was always about: whatever the
        region needs arrives as one external module, never as script written
        into the markup, and never as a per-region component that would tie
        the package to a framework's registration lifecycle.
        """
        html = render(A_REGION)
        assert "x-data" not in html
        scripts = re.findall(r"<script[^>]*>(.*?)</script>", html, re.S)
        assert len(scripts) == 1
        assert scripts[0].strip() == ""
        assert 'src="' in re.search(r"<script[^>]*>", html).group(0)


class TestChartRegionIdentity:
    """Several regions on one page stay independently identifiable."""

    def test_two_regions_in_one_template_get_different_ids(self):
        html = render(
            REGION.format(name="Revenue", description="Revenue by month.")
            + REGION.format(name="Signups", description="New signups by week.")
        )
        ids = re.findall(r'<figure id="([^"]+)"', html)
        assert len(ids) == 2
        assert ids[0] != ids[1]

    def test_each_regions_description_is_associated_with_that_region_and_no_other(self):
        html = render(
            REGION.format(name="Revenue", description="Revenue by month.")
            + REGION.format(name="Signups", description="New signups by week.")
        )
        figure_ids = re.findall(r'<figure id="([^"]+)"', html)
        surfaces = re.findall(r"<div[^>]*data-mvp-chart-region-surface[^>]*>", html)
        assert len(figure_ids) == len(surfaces) == 2
        for figure_id, surface in zip(figure_ids, surfaces, strict=True):
            assert f'aria-describedby="{figure_id}-description"' in surface

    def test_an_author_supplied_id_is_used_instead(self):
        html = render(
            '<c-echarts.region name="Revenue" description="Revenue by month." id="revenue-chart" />'
        )
        assert '<figure id="revenue-chart"' in html

    def test_numbering_restarts_for_a_new_request(self):
        html_a = render(A_REGION, request=rf.get("/"))
        html_b = render(A_REGION, request=rf.get("/"))
        id_a = re.search(r'<figure id="([^"]+)"', html_a).group(1)
        id_b = re.search(r'<figure id="([^"]+)"', html_b).group(1)
        assert id_a == id_b


class TestMissingAttributes:
    """A missing name or text alternative replaces the region rather than degrading it."""

    def test_missing_name_names_it_and_renders_no_region(self):
        html = render('<c-echarts.region description="Revenue by month." />')
        alert = re.search(r'<div[^>]*role="alert"[^>]*>(.*?)</div>', html, re.S)
        assert alert is not None
        assert "name" in alert.group(1).lower()
        assert "<figure" not in html

    def test_missing_description_names_it_and_renders_no_region(self):
        html = render('<c-echarts.region name="Revenue" />')
        alert = re.search(r'<div[^>]*role="alert"[^>]*>(.*?)</div>', html, re.S)
        assert alert is not None
        assert "description" in alert.group(1).lower()
        assert "<figure" not in html

    def test_empty_string_name_is_treated_as_missing(self):
        html = render('<c-echarts.region name="" description="Revenue by month." />')
        assert 'role="alert"' in html
        assert "<figure" not in html

    def test_empty_string_description_is_treated_as_missing(self):
        html = render('<c-echarts.region name="Revenue" description="" />')
        assert 'role="alert"' in html
        assert "<figure" not in html

    def test_both_missing_names_both(self):
        html = render("<c-echarts.region />")
        alert = re.search(r'<div[^>]*role="alert"[^>]*>(.*?)</div>', html, re.S)
        assert alert is not None
        assert "name" in alert.group(1).lower()
        assert "description" in alert.group(1).lower()


FIXTURE_LOCALE = Path(__file__).resolve().parent.parent / "locale"


class TestTranslatedMessages:
    """Every message the region can render is wrapped for translation.

    The package ships only a base English catalog (T004's `Implement`), so
    this test brings its own fixture catalog under `tests/locale/` rather
    than requiring a real second language to ship. It proves the wrapping
    and the catalog mechanics; the fixture is not distributed.
    """

    @override_settings(LOCALE_PATHS=[FIXTURE_LOCALE])
    def test_a_translated_message_is_shown_under_its_language(self):
        with translation.override("de"):
            html = render('<c-echarts.region description="Revenue by month." />')
        assert "Diese Diagrammfläche hat keinen Namen." in html
        assert "This chart region has no name." not in html

    def test_the_english_source_string_shows_with_no_translation_active(self):
        html = render('<c-echarts.region description="Revenue by month." />')
        assert "This chart region has no name." in html


class TestTheModuleLoadsOncePerPage:
    """T009: the package's own asset, shared by every region on a page."""

    def test_a_page_with_regions_loads_the_module(self):
        assert "chart-region.js" in render(A_REGION)

    def test_five_regions_load_it_once(self):
        """The cost of the module is per page, not per region."""
        html = render(A_REGION * 5)
        assert html.count("chart-region.js") == 1

    def test_a_page_with_no_region_asks_for_nothing(self):
        """Installing the package costs a page that uses none of it nothing."""
        html = render("<p>A page with no chart on it.</p>")
        assert "chart-region.js" not in html
        assert "mvp_charts" not in html

    def test_a_region_that_could_not_render_asks_for_nothing_either(self):
        """The guard replaces the region, so there is nothing to drive."""
        html = render('<c-echarts.region name="Revenue" />')
        assert "chart-region.js" not in html
