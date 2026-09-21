"""Properties every template this package ships has to hold.

Not about any one component. These are the mistakes that are invisible in
review, cost nothing to check, and reach a reader's page when nobody does.
"""

import re
from pathlib import Path

import pytest

import mvp_charts

from .test_region import render

PACKAGE_TEMPLATES = Path(mvp_charts.__file__).parent / "templates"
SHIPPED = sorted(PACKAGE_TEMPLATES.rglob("*.html"))


def test_there_are_templates_to_check():
    """Guards the parametrised tests below against an empty collection."""
    assert SHIPPED


@pytest.mark.parametrize(
    "template", SHIPPED, ids=lambda path: path.relative_to(PACKAGE_TEMPLATES).as_posix()
)
def test_no_comment_spans_more_than_one_line(template):
    """`{# … #}` is single-line, and a multi-line one is served as page text.

    Django's comment tag does not span lines. Open one, write a paragraph
    across several, and everything after the first line reaches the browser
    as content — inside a component, that is an explanation of the code
    printed into the page for the reader.

    It is silent: nothing raises, the markup still renders, and the only
    symptom is text nobody wrote appearing on a page, plus an element sized
    by a paragraph that should not exist. It cost this feature an afternoon
    of a browser test insisting a region would not fill its wrapper. Use
    `{% comment %}` for anything longer than a line.
    """
    for number, line in enumerate(template.read_text().splitlines(), start=1):
        opens = line.count("{#")
        closes = line.count("#}")
        assert opens == closes, (
            f"{template.name}:{number} opens a comment it does not close on "
            f"the same line; everything after it is served as page text"
        )


@pytest.mark.parametrize(
    "template", SHIPPED, ids=lambda path: path.relative_to(PACKAGE_TEMPLATES).as_posix()
)
def test_every_user_facing_string_is_wrapped_for_translation(template):
    """Article VIII, checked rather than remembered.

    Looks for text between tags that is neither a template expression nor
    already inside a translation tag. A hard-coded string here is one no
    project can translate and one no catalog will ever list.
    """
    source = template.read_text()
    source = re.sub(
        r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", "", source, flags=re.S
    )
    source = re.sub(r"\{#.*?#\}", "", source)
    source = re.sub(
        r"\{%\s*(trans|blocktrans).*?%\}.*?(\{%\s*endblocktrans\s*%\}|$)",
        "",
        source,
        flags=re.S,
    )
    source = re.sub(r"<[^>]*>", "\n", source)
    source = re.sub(r"\{\{.*?\}\}|\{%.*?%\}", "", source, flags=re.S)
    leftover = [line.strip() for line in source.splitlines() if line.strip()]
    assert leftover == []


def test_a_rendered_region_carries_no_explanation_of_itself():
    """The end state the checks above exist to protect.

    A reader of a page should see the chart's own content and nothing about
    how the component works.
    """
    html = render('<c-echarts.region name="Revenue" description="Revenue by month." />')
    for tell in ("the module", "Article", "data attributes", "{#", "#}"):
        assert tell not in html
