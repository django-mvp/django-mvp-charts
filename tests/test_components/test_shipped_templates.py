"""Properties every template this package ships has to hold.

Not about any one component. These are the mistakes that are invisible in
review, cost nothing to check, and reach a reader's page when nobody does.
"""

import re
from pathlib import Path

import pytest
from pyecharts.charts import Line

import mvp_charts

PACKAGE_TEMPLATES = Path(mvp_charts.__file__).parent / "templates"
SHIPPED = sorted(PACKAGE_TEMPLATES.rglob("*.html"))

#: Identify each parametrised case by the template it covers.
BY_TEMPLATE = {
    "argnames": "template",
    "argvalues": SHIPPED,
    "ids": lambda path: path.relative_to(PACKAGE_TEMPLATES).as_posix(),
}


class TestShippedTemplates:
    def test_there_are_templates_to_check(self):
        assert SHIPPED

    @pytest.mark.parametrize(**BY_TEMPLATE)
    def test_no_comment_spans_more_than_one_line(self, template):
        for number, line in enumerate(template.read_text().splitlines(), start=1):
            assert line.count("{#") == line.count("#}"), (
                f"{template.name}:{number} opens a comment it does not close "
                f"on the same line; everything after it is served as page text"
            )

    @pytest.mark.parametrize(**BY_TEMPLATE)
    def test_every_user_facing_string_is_wrapped_for_translation(self, template):
        source = template.read_text()
        source = re.sub(
            r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}", "", source, flags=re.S
        )
        source = re.sub(r"\{#.*?#\}", "", source)
        source = re.sub(
            r"\{%\s*(trans|blocktrans).*?%\}.*?(\{%\s*endblocktrans\s*%\}|$)",
            "",
            source,
            flags=re.S,
        )
        source = re.sub(r"<[^>]*>", "\n", source)
        source = re.sub(r"\{\{.*?\}\}|\{%.*?%\}", "", source, flags=re.S)
        leftover = [line.strip() for line in source.splitlines() if line.strip()]
        assert leftover == []

    @pytest.mark.parametrize(**BY_TEMPLATE)
    def test_no_shipped_template_names_a_remote_origin(self, template):
        assert not re.search(r"https?://", template.read_text())

    def test_a_rendered_chart_carries_no_explanation_of_itself(self, render):
        chart = Line().add_xaxis(["Jan"]).add_yaxis("Revenue", [12])
        html = render(
            '<c-chart :chart="chart" id="revenue" name="Revenue"'
            ' description="Revenue by month." />',
            chart=chart,
        )
        assert "<figure" in html, "this has to be a rendered chart, not the guard"
        for tell in ("the module", "Props:", "pyecharts", "{#", "#}"):
            assert tell not in html
