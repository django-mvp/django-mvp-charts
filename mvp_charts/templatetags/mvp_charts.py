"""The template tag a line chart's Cotton component uses to build itself."""

import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe

from mvp_charts.echarts.options import Attribute, Line, Merge

register = template.Library()

#: The three character sequences that can end a `<script>` element early, or
#: smuggle a line/paragraph separator past a browser's line-comment JS
#: parsing — the same three sequences `django.utils.html.json_script` escapes,
#: reproduced here because the payload needs its own `<script>` tag carrying
#: an extra data attribute that `json_script` has no way to add (D1).
_SCRIPT_SAFE_ESCAPES = {
    ord("<"): "\\u003C",
    ord(">"): "\\u003E",
    ord("&"): "\\u0026",
}


class EChartsChart:
    """What `{% echarts_chart %}` hands the template: an id and a JSON payload."""

    def __init__(self, element_id, options):
        self.id = element_id
        # Safe for the same reason django.utils.html.json_script's own output
        # is: the three sequences that could end a <script> element early or
        # smuggle a line/paragraph separator have already been escaped above.
        self.payload = mark_safe(  # noqa: S308
            json.dumps(options, cls=DjangoJSONEncoder).translate(_SCRIPT_SAFE_ESCAPES)
        )


@register.simple_tag
def echarts_chart(element_id="", values="", labels="", options=""):
    """Build a line chart's options and carry them with its id, or nothing.

    Returns ``None`` when no id was given, so a component can guard its
    options script on the tag's result rather than repeating the check. An
    `options` attribute, when given, is deep-merged over the built object
    (FR-012) rather than replacing it.
    """
    if not element_id:
        return None
    built = Line(values, labels).options()
    overrides = Attribute(options)
    if overrides.given:
        built = Merge(built, overrides.value).result()
    return EChartsChart(element_id, built)
