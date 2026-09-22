"""Tests for <c-echarts.region>, the rendered-output contract.

Compiles Cotton source directly rather than going through a view, so this
file covers what the tag renders as markup: placement, the identity the
author gives it, the missing-attribute guard and translation.
tests/test_demo.py covers it as the demo project actually serves it, and
test_region_e2e.py covers what only a real browser can measure.
"""

import html as html_module
import re
from pathlib import Path

from django import template as dj_template
from django.template import Context
from django.test import override_settings
from django.utils import translation
from django_cotton.compiler_regex import CottonCompiler

compiler = CottonCompiler()


def render(source, **context):
    """Compile a Cotton source string and render it.

    No request is involved. A region reads nothing off one, which is what
    lets it render anywhere a template does, including a page assembled
    outside the request cycle.
    """
    return dj_template.Template(compiler.process(source)).render(Context(context))


REGION = '<c-echarts.region id="{id}" name="{name}" description="{description}" />'
A_REGION = REGION.format(
    id="revenue", name="Monthly revenue", description="Revenue by month, in EUR."
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

        Three elements have to be wired to each other for a screen reader to
        read the caption as this chart's description, and the author supplies
        the id all three are built from.
        """
        html = render(A_REGION)
        figure_id = re.search(r'<figure id="([^"]+)"', html).group(1)
        surface = re.search(
            r"<div[^>]*data-mvp-chart-region-surface[^>]*>", html
        ).group(0)
        figcaption_id = re.search(r'<figcaption id="([^"]+)"', html).group(1)
        assert figure_id == "revenue"
        assert f'aria-describedby="{figure_id}-description"' in surface
        assert figcaption_id == f"{figure_id}-description"

    def test_the_region_renders_no_script_at_all(self):
        """Neither inline script nor a tag fetching one.

        The region is markup. Everything it needs in the browser is in
        chart-region.js, which the project loads from its own base template
        alongside the charting library — so the project decides which pages
        pay for it, and where in the document it goes. A region that emitted
        its own tag would be taking both of those decisions back.
        """
        html = render(A_REGION)
        assert "x-data" not in html
        assert "<script" not in html
        assert "chart-region.js" not in html


class TestChartRegionIdentity:
    """The author names each region, and the region uses that name verbatim."""

    def test_the_id_is_used_exactly_as_given(self):
        html = render(A_REGION)
        assert '<figure id="revenue"' in html

    def test_each_regions_description_is_associated_with_that_region_and_no_other(self):
        html = render(
            REGION.format(id="revenue", name="Revenue", description="Revenue by month.")
            + REGION.format(
                id="signups", name="Signups", description="New signups by week."
            )
        )
        figure_ids = re.findall(r'<figure id="([^"]+)"', html)
        surfaces = re.findall(r"<div[^>]*data-mvp-chart-region-surface[^>]*>", html)
        assert figure_ids == ["revenue", "signups"]
        assert len(surfaces) == 2
        for figure_id, surface in zip(figure_ids, surfaces, strict=True):
            assert f'aria-describedby="{figure_id}-description"' in surface


class TestHeight:
    """Issue #32: a region can be given its height directly.

    A second sizing mode, not a replacement for the first: given a height,
    the figure carries it and needs no wrapper; given none, the figure fills
    its parent exactly as before.
    """

    def test_a_given_height_is_carried_on_the_figure_itself(self):
        html = render('<c-echarts.region id="revenue" height="320px" />')
        figure = re.search(r"<figure[^>]*>", html).group(0)
        assert 'style="height: 320px"' in figure

    def test_no_height_still_fills_its_parent_exactly_as_before(self):
        html = render(A_REGION)
        figure = re.search(r"<figure[^>]*>", html).group(0)
        assert re.search(r'class="relative h-full w-full"', figure)
        assert "style=" not in figure

    def test_an_empty_string_height_is_treated_as_not_given(self):
        html = render('<c-echarts.region id="revenue" height="" />')
        figure = re.search(r"<figure[^>]*>", html).group(0)
        assert re.search(r'class="relative h-full w-full"', figure)
        assert "style=" not in figure


class TestSlotContent:
    """Issue #33: a region takes slot content and renders it inside the figure.

    The mechanism a chart type composes on top of, not anything specific to
    one charting library: the region renders whatever its caller puts between
    its open and close tags, after the drawing surface, and knows nothing
    about what that content is.
    """

    def test_slot_content_is_rendered_inside_the_figure_after_the_surface(self):
        html = render(
            '<c-echarts.region id="revenue">'
            '<mark id="caller-content">payload</mark>'
            "</c-echarts.region>"
        )
        figure = re.search(r"<figure[^>]*>(.*)</figure>", html, re.S).group(1)
        assert '<mark id="caller-content">payload</mark>' in figure
        surface_at = figure.index("data-mvp-chart-region-surface")
        content_at = figure.index('id="caller-content"')
        assert content_at > surface_at


class TestMissingAttributes:
    """A missing id replaces the region rather than degrading it.

    FR-010 supersedes FS-001's rule that a missing name or a missing text
    alternative does the same: those two branches are gone from
    region.html, so a region that carries only an id now renders. The id
    stays the one thing whose absence is still reported.
    """

    def test_missing_id_names_it_and_renders_no_region(self):
        html = render(
            '<c-echarts.region name="Revenue" description="Revenue by month." />'
        )
        alert = re.search(r'<div[^>]*role="alert"[^>]*>(.*?)</div>', html, re.S)
        assert alert is not None
        assert "id" in alert.group(1).lower()
        assert "<figure" not in html

    def test_missing_name_no_longer_blocks_the_region_fr_010(self):
        html = render(
            '<c-echarts.region id="revenue" description="Revenue by month." />'
        )
        assert 'role="alert"' not in html
        assert '<figure id="revenue"' in html

    def test_missing_description_no_longer_blocks_the_region_fr_010(self):
        html = render('<c-echarts.region id="revenue" name="Revenue" />')
        assert 'role="alert"' not in html
        assert '<figure id="revenue"' in html

    def test_empty_string_id_is_treated_as_missing(self):
        html = render(
            '<c-echarts.region id="" name="Revenue" description="Revenue by month." />'
        )
        assert 'role="alert"' in html
        assert "<figure" not in html

    def test_empty_string_name_is_treated_as_not_given_fr_010(self):
        html = render(
            '<c-echarts.region id="revenue" name="" description="Revenue by month." />'
        )
        assert 'role="alert"' not in html
        assert '<figure id="revenue"' in html

    def test_empty_string_description_is_treated_as_not_given_fr_010(self):
        html = render('<c-echarts.region id="revenue" name="Revenue" description="" />')
        assert 'role="alert"' not in html
        assert '<figure id="revenue"' in html

    def test_all_three_missing_names_only_the_id_fr_010(self):
        html = render("<c-echarts.region />")
        alert = re.search(r'<div[^>]*role="alert"[^>]*>(.*?)</div>', html, re.S)
        assert alert is not None
        message = alert.group(1).lower()
        assert "id" in message
        assert "name" not in message
        assert "description" not in message


class TestOptionalNameAndDescription:
    """US2: a region with only an id renders, per FR-008, FR-009 and FR-010.

    The previous feature made an accessible name and a text alternative a
    condition of the region rendering at all. This feature keeps both
    available and worth giving, and stops requiring either.
    """

    def test_a_region_with_only_an_id_renders_with_no_missing_message(self):
        html = render('<c-echarts.region id="revenue" />')
        assert 'role="alert"' not in html
        assert "has no name" not in html
        assert "has no description" not in html
        assert '<figure id="revenue"' in html

    def test_the_surface_carries_no_role_and_no_aria_label_without_a_name(self):
        html = render(
            '<c-echarts.region id="revenue" description="Revenue by month." />'
        )
        surface = re.search(
            r"<div[^>]*data-mvp-chart-region-surface[^>]*>", html
        ).group(0)
        assert "role=" not in surface
        assert "aria-label" not in surface

    def test_no_figcaption_without_a_description(self):
        html = render('<c-echarts.region id="revenue" name="Revenue" />')
        assert "<figcaption" not in html

    def test_name_and_description_are_still_carried_exactly_when_given(self):
        """FR-009: giving both still works precisely as the previous feature specified."""
        html = render(A_REGION)
        surface = re.search(
            r"<div[^>]*data-mvp-chart-region-surface[^>]*>", html
        ).group(0)
        assert 'role="img"' in surface
        assert 'aria-label="Monthly revenue"' in surface
        figcaption = re.search(
            r'<figcaption[^>]*class="sr-only"[^>]*>(.*?)</figcaption>', html
        )
        assert figcaption is not None
        assert figcaption.group(1).strip() == "Revenue by month, in EUR."

    def test_an_empty_name_is_not_carried_as_an_empty_attribute(self):
        html = render(
            '<c-echarts.region id="revenue" name="" description="Revenue by month." />'
        )
        surface = re.search(
            r"<div[^>]*data-mvp-chart-region-surface[^>]*>", html
        ).group(0)
        assert "aria-label" not in surface

    def test_an_empty_description_is_not_carried_as_an_empty_figcaption(self):
        html = render('<c-echarts.region id="revenue" name="Revenue" description="" />')
        assert "<figcaption" not in html

    def test_a_missing_id_is_still_reported_when_name_and_description_are_given(self):
        html = render(
            '<c-echarts.region name="Revenue" description="Revenue by month." />'
        )
        alert = re.search(r'<div[^>]*role="alert"[^>]*>(.*?)</div>', html, re.S)
        assert alert is not None
        assert "id" in alert.group(1).lower()


FIXTURE_LOCALE = Path(__file__).resolve().parent.parent / "locale"


class TestTranslatedMessages:
    """Every message the region can render is wrapped for translation.

    The package ships only a base English catalog (T004's `Implement`), so
    this test brings its own fixture catalog under `tests/locale/` rather
    than requiring a real second language to ship. It proves the wrapping
    and the catalog mechanics; the fixture is not distributed.

    FR-010 removes the missing-name message this fixture catalog used to
    translate, so the fixture and these tests exercise the message that
    survives — the missing-id one — instead.
    """

    @override_settings(LOCALE_PATHS=[FIXTURE_LOCALE])
    def test_a_translated_message_is_shown_under_its_language(self):
        with translation.override("de"):
            html = render(
                '<c-echarts.region name="Revenue" description="Revenue by month." />'
            )
        assert "Diese Diagrammfläche hat keine ID." in html
        assert "This chart region has no id." not in html

    def test_the_english_source_string_shows_with_no_translation_active(self):
        html = render(
            '<c-echarts.region name="Revenue" description="Revenue by month." />'
        )
        assert "This chart region has no id." in html


class TestFailureMessages:
    """T013: both messages ship with the region, in the page, in the catalog.

    The module decides *when* a region cannot draw. What it then says is
    server-rendered and travels with the markup, so the wording, the
    translation and the presence of both are asserted on every run rather
    than only where a browser is installed.
    """

    def test_the_region_carries_both_messages(self):
        figure = re.search(r"<figure[^>]*>", render(A_REGION)).group(0)
        assert "data-mvp-chart-region-missing-library=" in figure
        assert "data-mvp-chart-region-no-height=" in figure

    def test_the_missing_library_message_names_both_ways_to_supply_it(self):
        """A message that only says what is wrong leaves the reader stuck.

        Neither route is a thing this package supplies, so the message names
        what the reader has to do rather than a component they could place.
        """
        message = self.message(render(A_REGION), "missing-library")
        assert "your own base template" in message
        assert "window.echarts" in message

    def test_the_no_height_message_says_where_the_height_belongs(self):
        message = self.message(render(A_REGION), "no-height")
        assert "element around this chart" in message
        assert "takes its size from its wrapper" in message

    def test_neither_message_is_empty(self):
        for attribute in ("missing-library", "no-height"):
            assert len(self.message(render(A_REGION), attribute)) > 40

    def test_the_messages_are_translated(self):
        """They go through the package's catalog, like every other string here."""
        with (
            override_settings(LOCALE_PATHS=[FIXTURE_LOCALE]),
            translation.override("de"),
        ):
            message = self.message(render(A_REGION), "missing-library")
        assert message.startswith("Keine Diagrammbibliothek")

    @staticmethod
    def message(html, attribute):
        """One message, read off the figure and unescaped."""
        raw = re.search(rf'data-mvp-chart-region-{attribute}="([^"]*)"', html).group(1)
        return html_module.unescape(raw)
