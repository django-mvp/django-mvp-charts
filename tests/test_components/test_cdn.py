"""Tests for <c-echarts.cdn>, the development delivery.

This is the one place in the package that names a third-party origin, and it
only reaches a page because a project put it in its own base template. Nothing
else in the package may reference a remote origin at all, which the last class
here asserts over every shipped template rather than trusting review to notice.
"""

import re
from pathlib import Path

import mvp_charts
from mvp_charts.versions import (
    ECHARTS_CDN_INTEGRITY,
    ECHARTS_CDN_VERSION,
    ECHARTS_SUPPORTED_VERSIONS,
)

from .test_region import render

PACKAGE_TEMPLATES = Path(mvp_charts.__file__).parent / "templates"


class TestDevelopmentDelivery:
    """One pinned, integrity-checked script tag, and nothing else."""

    def test_it_renders_exactly_one_script_tag(self):
        html = render("<c-echarts.cdn />")
        assert len(re.findall(r"<script\b", html)) == 1

    def test_the_version_is_pinned_in_the_url(self):
        """A floating URL cannot carry an integrity hash and is a new file daily."""
        html = render("<c-echarts.cdn />")
        source = re.search(r'src="([^"]+)"', html).group(1)
        assert f"echarts@{ECHARTS_CDN_VERSION}/" in source
        assert source.startswith("https://")

    def test_it_carries_the_integrity_hash_and_asks_for_anonymous_credentials(self):
        """Both, or neither works.

        A browser ignores `integrity` on a cross-origin request unless the
        request is made in CORS mode, so an integrity hash without
        `crossorigin` is a hash that is never checked — which looks exactly
        like a hash that is.
        """
        html = render("<c-echarts.cdn />")
        script = re.search(r"<script[^>]*>", html).group(0)
        assert f'integrity="{ECHARTS_CDN_INTEGRITY}"' in script
        assert 'crossorigin="anonymous"' in script

    def test_the_integrity_hash_is_a_sha384_digest(self):
        assert re.fullmatch(r"sha384-[A-Za-z0-9+/]{64}", ECHARTS_CDN_INTEGRITY)

    def test_the_pinned_version_falls_inside_the_declared_range(self):
        """T011: the range the namespace claims has to cover what it loads.

        Read as numbers rather than by string comparison, so a 6.10.0 pin is
        not silently judged against "6.1".
        """
        low, high = ECHARTS_SUPPORTED_VERSIONS.split(",")
        assert low.startswith(">=") and high.startswith("<")
        as_numbers = lambda text: tuple(  # noqa: E731 - one expression, used twice
            int(part) for part in re.findall(r"\d+", text)
        )
        pinned = as_numbers(ECHARTS_CDN_VERSION)
        assert as_numbers(low) <= pinned[: len(as_numbers(low))]
        assert pinned[: len(as_numbers(high))] < as_numbers(high)


class TestNothingElseReachesOffSite:
    """Article XII, asserted over what ships rather than left to review.

    A component that loaded a third-party script on a reader's behalf would
    give every project installing this package an external origin it did not
    choose. The delivery component is the sole exception, and it only reaches
    a page because a project placed it there itself.
    """

    def test_no_other_shipped_template_names_a_remote_origin(self):
        offenders = {
            path.relative_to(PACKAGE_TEMPLATES).as_posix()
            for path in PACKAGE_TEMPLATES.rglob("*.html")
            if path.name != "cdn.html" and re.search(r"https?://", path.read_text())
        }
        assert offenders == set()

    def test_the_region_itself_loads_no_third_party_script(self):
        html = render(
            '<c-echarts.region name="Revenue" description="Revenue by month." />'
        )
        assert "http://" not in html
        assert "https://" not in html
