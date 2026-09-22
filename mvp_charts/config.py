"""Project-level settings, one namespace per charting library.

``MVP_CHARTS_CONFIG`` is built by merging a project's ``settings.MVP_CHARTS_CONFIG``
over the defaults below, so a project states only what it is changing::

    MVP_CHARTS_CONFIG = {"echarts": {"renderer": "svg"}}

Read it as a dict::

    from mvp_charts.config import MVP_CHARTS_CONFIG

    MVP_CHARTS_CONFIG["echarts"]["renderer"]

**Settings are per backend, like everything else here.** ECharts' renderer means
nothing to a second charting library, and a flat key would have to be renamed the
day one arrives (Article XIII).

**What lives here rather than on a tag.** A setting is for a choice a project
makes once, about its own environment, that a template author is in no position
to make chart by chart. Anything about one chart — its data, its axes, how it
looks — is an attribute or a raw option, and stays there.
"""

from collections.abc import Mapping
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

#: What every ECharts chart in a project is initialised with.
DEFAULTS: dict[str, Any] = {
    "echarts": {
        # Which renderer `echarts.init` draws with: "canvas" or "svg".
        #
        # Canvas is ECharts' own default and suits most pages. SVG uses less
        # memory, which matters on low-end mobile devices and on pages carrying
        # many charts at once, and it stays sharp when zoomed or printed. What
        # decides it — the devices a project serves, how many charts a page
        # shows, whether pages get printed — is true of a project rather than of
        # one chart, which is why it is here and not on the tag.
        #
        # A project that bundles ECharts itself rather than loading a full build
        # has to have registered the SVG renderer for "svg" to do anything:
        #
        #     import { SVGRenderer } from "echarts/renderers";
        #     echarts.use([SVGRenderer]);
        #
        # Without it ECharts quietly draws with whichever renderer the bundle
        # does have, and says nothing. Nothing on this side can detect that, so
        # a project switching to SVG checks its own bundle.
        "renderer": "canvas",
    },
}

#: The renderers `echarts.init` accepts.
ECHARTS_RENDERERS = ("canvas", "svg")


def _merge(base: Mapping[str, Any], over: Mapping[str, Any]) -> dict[str, Any]:
    """Deep-merge ``over`` onto ``base``, mappings recursively.

    Recursive so that a project naming one key in a backend's settings keeps the
    defaults for the rest of them, rather than replacing the whole namespace and
    silently losing every key it did not restate.
    """
    out = dict(base)
    for key, value in (over or {}).items():
        if isinstance(value, Mapping) and isinstance(out.get(key), Mapping):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def _validate(config: Mapping[str, Any]) -> None:
    """Refuse a setting that cannot mean anything, at startup rather than later.

    The renderer is a closed set of two values a project either wrote correctly
    or mistyped. ECharts itself falls back to a working renderer rather than
    complaining, so a typo here draws a chart that looks right and ignores the
    setting — the failure nobody ever goes looking for.
    """
    renderer = config["echarts"]["renderer"]
    if renderer not in ECHARTS_RENDERERS:
        raise ImproperlyConfigured(
            f'MVP_CHARTS_CONFIG["echarts"]["renderer"] is {renderer!r}; '
            f"it has to be one of {', '.join(repr(r) for r in ECHARTS_RENDERERS)}."
        )


def build() -> dict[str, Any]:
    """The defaults with the project's overrides merged over them, validated."""
    config = _merge(DEFAULTS, getattr(settings, "MVP_CHARTS_CONFIG", {}) or {})
    _validate(config)
    return config


MVP_CHARTS_CONFIG = build()
