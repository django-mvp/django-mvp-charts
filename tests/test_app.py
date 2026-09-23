"""The package installs and exposes what a consuming project needs from it."""

from pathlib import Path

from django.apps import apps

import mvp_charts
from mvp_charts.versions import ECHARTS_SUPPORTED_VERSIONS


class TestPackagedApp:
    """What a host project gets after installing and adding it to INSTALLED_APPS."""

    def test_app_is_installed(self) -> None:
        assert apps.is_installed("mvp_charts")

    def test_the_component_is_where_cotton_looks_for_it(self) -> None:
        """Cotton resolves `<c-chart>` to `cotton/chart.html`.

        The file name is the tag name, so it is not a free choice: renaming it
        breaks every chart on every page at once, and does so silently — a
        component Cotton cannot find renders as empty output rather than
        raising.
        """
        component = (
            Path(mvp_charts.__file__).parent / "templates" / "cotton" / "chart.html"
        )
        assert component.is_file()

    def test_the_browser_module_is_where_a_static_tag_will_find_it(self) -> None:
        """The path in every project's base template, and in the README.

        The project writes `{% static 'mvp_charts/js/mvp-charts.js' %}` itself,
        so a file moved here leaves that line resolving to a 404 with nothing
        raising at render time.
        """
        module = (
            Path(mvp_charts.__file__).parent
            / "static"
            / "mvp_charts"
            / "js"
            / "mvp-charts.js"
        )
        assert module.is_file()

    def test_the_package_ships_exactly_one_component(self) -> None:
        """The whole public surface, asserted rather than described.

        A second component added here is a decision about the package's API,
        not an implementation detail, and this is what makes one arrive
        deliberately.
        """
        components = sorted(
            path.name
            for path in (
                Path(mvp_charts.__file__).parent / "templates" / "cotton"
            ).rglob("*.html")
        )
        assert components == ["chart.html"]

    def test_the_readme_quotes_the_supported_range_the_package_states(self) -> None:
        """Two places say what this renders against, and they have to agree.

        The constant is what a project reads from code; the README is what a
        person reads before bundling. A range bumped in one and not the other
        is wrong somewhere, and nothing else would catch it.
        """
        readme = (Path(mvp_charts.__file__).parent.parent / "README.md").read_text()
        assert f"`{ECHARTS_SUPPORTED_VERSIONS}`" in readme
