"""The package installs and exposes what a consuming project needs from it."""

from pathlib import Path

from django.apps import apps

import mvp_charts
from mvp_charts.versions import ECHARTS_SUPPORTED_VERSIONS


class TestPackagedApp:
    def test_app_is_installed(self) -> None:
        assert apps.is_installed("mvp_charts")

    def test_the_component_is_where_cotton_looks_for_it(self) -> None:
        component = (
            Path(mvp_charts.__file__).parent / "templates" / "cotton" / "chart.html"
        )
        assert component.is_file()

    def test_the_browser_module_is_where_a_static_tag_will_find_it(self) -> None:
        module = (
            Path(mvp_charts.__file__).parent
            / "static"
            / "mvp_charts"
            / "js"
            / "mvp-charts.js"
        )
        assert module.is_file()

    def test_the_package_ships_exactly_one_component(self) -> None:
        components = sorted(
            path.name
            for path in (
                Path(mvp_charts.__file__).parent / "templates" / "cotton"
            ).rglob("*.html")
        )
        assert components == ["chart.html"]

    def test_the_readme_quotes_the_supported_range_the_package_states(self) -> None:
        readme = (Path(mvp_charts.__file__).parent.parent / "README.md").read_text()
        assert f"`{ECHARTS_SUPPORTED_VERSIONS}`" in readme
