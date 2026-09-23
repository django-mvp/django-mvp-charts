"""The template tag `<c-chart>` uses to carry a chart's options into the page."""

import re

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


#: The last `"key":` before a given point in a serialised options document.
OPTION_KEY_BEFORE = re.compile(r'"([^"]+)"\s*:\s*$')


def callback_option_name(plain: str, quoted: str) -> str | None:
    """The option a JavaScript callback sits on, or `None` if it cannot be read.

    pyecharts serialises a `JsCode` behind a sentinel and then strips it two
    ways: one leaves the function bare, the other leaves it quoted. The two
    documents are therefore identical up to the first callback and differ at
    the quote in front of it, which puts the option carrying it immediately
    before the point where they diverge.
    """
    # `strict=False` because the two are different lengths exactly when a
    # callback is present: the quoted document carries two quotes the other
    # does not. Their common prefix is where the divergence is.
    divergence = next(
        (i for i, (a, b) in enumerate(zip(plain, quoted, strict=False)) if a != b),
        None,
    )
    if divergence is None:
        return None
    key = OPTION_KEY_BEFORE.search(quoted[:divergence])
    return key.group(1) if key else None


@register.simple_tag
def chart_options(chart: Base) -> str:
    """A chart's options, as JSON that is safe inside a `<script>` element.

    The chart builds its own options and serialises its own values, including
    the dates, times, decimals and missing values a Django view produces. This
    package adds nothing to what it returns and takes nothing away.

    Raises `ValueError` if the chart carries a JavaScript callback, which
    cannot travel to the browser as data. See the README.
    """
    # The annotated locals are what narrow pyecharts' `Any` — it ships no type
    # information — to `str`; returning a call directly is a mypy
    # `no-any-return`.
    #
    # The two serialisations differ only where a chart carries a callback, so
    # comparing them is what detects one. The quoted form is the one returned
    # because it is valid JSON in every case, including any the check misses.
    quoted: str = chart.dump_options_with_quotes()
    plain: str = chart.dump_options()
    if plain != quoted:
        name = callback_option_name(plain, quoted)
        option = f"`{name}`" if name else "one of its options"
        raise ValueError(
            f"This chart carries a JavaScript callback on {option}. The options "
            "travel to the browser as JSON and a function cannot be written into "
            "JSON, so a chart naming one is refused here rather than sent as a "
            "document the page cannot parse. Remove it, or write it in your own "
            "JavaScript against the chart instance that echarts.getInstanceByDom() "
            "returns for the figure's drawing surface."
        )
    return mark_safe(quoted.translate(SCRIPT_SAFE_ESCAPES))  # noqa: S308
