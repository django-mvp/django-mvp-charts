"""The template tag `<c-chart>` uses to carry a chart's options into the page."""

import re

from django import template
from django.utils.safestring import mark_safe
from pyecharts.charts.base import Base

register = template.Library()

#: The characters `django.utils.html.json_script` escapes so data cannot end a
#: `<script>` element early. pyecharts escapes none of them, so a label holding
#: `</script>` would otherwise reach the page verbatim.
SCRIPT_SAFE_ESCAPES = {
    ord("<"): "\\u003C",
    ord(">"): "\\u003E",
    ord("&"): "\\u0026",
}


#: The last `"key":` before a given point in a serialised options document.
OPTION_KEY_BEFORE = re.compile(r'"([^"]+)"\s*:\s*$')


def callback_option_name(plain: str, quoted: str) -> str | None:
    """Name the option a JavaScript callback sits on.

    pyecharts serialises a `JsCode` behind a sentinel and strips it two ways:
    one leaves the function bare, the other quoted. The two documents match up
    to the first callback and differ at the quote in front of it, so the option
    carrying it is the last key before the point where they diverge.

    Args:
        plain: The chart's options from `dump_options()`.
        quoted: The same options from `dump_options_with_quotes()`.

    Returns:
        The option's key, or `None` when the documents agree or no key precedes
        the divergence.
    """
    # The quoted document is longer exactly when a callback is present, so the
    # divergence lies within their common prefix.
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
    """Render a chart's options as JSON that is safe inside a `<script>` element.

    The chart builds its own options and serialises its own values, including
    the dates, times, decimals and missing values a Django view produces. This
    package adds nothing to what it returns and takes nothing away.

    Args:
        chart: The pyecharts chart to serialise.

    Returns:
        The chart's options as JSON, marked safe for the template.

    Raises:
        ValueError: The chart carries a JavaScript callback, which cannot
            travel to the browser as data.
    """
    # Annotated locals narrow pyecharts' untyped `Any` to `str` for mypy. The
    # quoted form is returned because it is valid JSON even where the
    # callback check below misses one.
    quoted: str = chart.dump_options_with_quotes()
    plain: str = chart.dump_options()
    if plain != quoted:
        name = callback_option_name(plain, quoted)
        cause = (
            f"This chart carries a JavaScript callback on `{name}`."
            if name
            else (
                "This chart's options did not serialise as JSON, which a "
                "JavaScript callback in one of them would explain."
            )
        )
        raise ValueError(
            f"{cause} The options travel to the browser as JSON and a function "
            "cannot be written into JSON, so this is refused here rather than "
            "sent as a document the page cannot parse. Remove the callback, or "
            "set it from your own JavaScript on the chart instance, which the "
            "figure's mvp-chart:drawn event carries and "
            "echarts.getInstanceByDom() returns for its drawing surface."
        )
    return mark_safe(quoted.translate(SCRIPT_SAFE_ESCAPES))  # noqa: S308
