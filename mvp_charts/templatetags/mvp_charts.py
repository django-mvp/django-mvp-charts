"""What a template needs from this package that a template cannot state itself."""

from django import template

from mvp_charts import versions

register = template.Library()


@register.simple_tag
def echarts_cdn():
    """Where `<c-echarts.cdn />` loads ECharts from, and the hash it must match.

    A template cannot read a Python constant, and these three values have to
    agree with each other — a URL whose version no longer matches its hash is
    a script the browser silently refuses. Handing the template one object
    from one source keeps them from drifting apart in the markup.
    """
    return {
        "url": versions.ECHARTS_CDN_URL,
        "integrity": versions.ECHARTS_CDN_INTEGRITY,
        "version": versions.ECHARTS_CDN_VERSION,
    }
