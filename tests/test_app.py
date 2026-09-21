"""The package installs and exposes what a consuming project needs from it."""

from pathlib import Path

from django.apps import apps

import mvp_charts


class TestPackagedApp:
    """What a host project gets after installing and adding it to INSTALLED_APPS."""

    def test_app_is_installed(self) -> None:
        assert apps.is_installed("mvp_charts")

    def test_echarts_namespace_is_where_cotton_looks_for_it(self) -> None:
        """Cotton resolves `<c-echarts.line>` to `cotton/echarts/line.html`.

        The directory name is the tag name, so it is not a free choice: renaming
        it breaks every component tag in the namespace at once, and does so
        silently — a missing component renders as empty output rather than
        raising. The namespace is the charting library, not this package, so
        that a second backend can be added alongside without touching the first.
        """
        namespace = (
            Path(mvp_charts.__file__).parent / "templates" / "cotton" / "echarts"
        )
        assert namespace.is_dir()
