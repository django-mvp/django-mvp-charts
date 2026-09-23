"""The template tag `<c-chart>` uses to carry a chart's options into the page."""

from django import template
from django.utils.safestring import mark_safe
from pyecharts.charts.base import Base

register = template.Library()

#: The three character sequences that can end a `<script>` element early, or
#: smuggle a line/paragraph separator past a browser's line-comment JS parsing
#: — the same three sequences `django.utils.html.json_script` escapes.
#:
#: pyecharts escapes none of them. A chart label read out of the database and
#: containing `</script>` reaches `dump_options()`'s output verbatim, so this
#: is what stands between a page's data and its structure.
SCRIPT_SAFE_ESCAPES = {
    ord("<"): "\\u003C",
    ord(">"): "\\u003E",
    ord("&"): "\\u0026",
}


@register.simple_tag
def chart_options(chart: Base) -> str:
    """A chart's options, as JSON that is safe inside a `<script>` element.

    The chart builds its own options and serialises its own values, including
    the dates, times, decimals and missing values a Django view produces. This
    package adds nothing to what it returns and takes nothing away.
    """
    # The annotated local is what narrows `dump_options`'s `Any` — pyecharts
    # ships no type information — to `str`; returning the call directly is a
    # mypy `no-any-return`.
    options: str = chart.dump_options()
    return mark_safe(options.translate(SCRIPT_SAFE_ESCAPES))  # noqa: S308
