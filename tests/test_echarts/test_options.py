"""Tests for the options object a line chart asks ECharts to draw.

Python only, mirroring ``mvp_charts/echarts/options.py`` (Article X). No
Cotton compilation here — the rendered-output contract is covered in
``tests/test_components/test_line.py``.
"""

from mvp_charts.echarts.options import Attribute, Line


class TestAttribute:
    """One attribute's Python value: empty reads as not given, else untouched."""

    def test_an_empty_string_reads_as_not_given(self):
        attribute = Attribute("")
        assert attribute.given is False
        assert attribute.value is None

    def test_zero_is_a_value_somebody_wrote(self):
        """A naive falsy check would mistake this for not given."""
        attribute = Attribute(0)
        assert attribute.given is True
        assert attribute.value == 0

    def test_zero_point_zero_is_a_value_somebody_wrote(self):
        attribute = Attribute(0.0)
        assert attribute.given is True
        assert attribute.value == 0.0

    def test_a_list_is_returned_exactly_as_it_arrived(self):
        raw = [12, 14, 15]
        attribute = Attribute(raw)
        assert attribute.given is True
        assert attribute.value == raw

    def test_a_string_is_returned_unparsed(self):
        """FR-002a: the package never reads data out of text.

        Written where a list belongs, a string is not split, not guessed at
        and not reported — it travels through exactly as it arrived.
        """
        attribute = Attribute("12,14,15")
        assert attribute.given is True
        assert attribute.value == "12,14,15"


class TestLine:
    """The options object built for values with labels, without, and for none."""

    def test_values_with_labels(self):
        options = Line([12, 14, 15], ["Jan", "Feb", "Mar"]).options()
        assert options == {
            "xAxis": {"type": "category", "data": ["Jan", "Feb", "Mar"]},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "data": [12, 14, 15]}],
        }

    def test_values_without_labels(self):
        options = Line([12, 14, 15], "").options()
        assert options == {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "data": [12, 14, 15]}],
        }

    def test_no_values_at_all(self):
        options = Line("", "").options()
        assert options == {
            "xAxis": {"type": "category"},
            "yAxis": {"type": "value"},
            "series": [{"type": "line", "data": []}],
        }

    def test_a_value_list_with_none_a_float_and_a_zero_survives_unchanged(self):
        """FR-004: nothing reordered, dropped, combined, rounded or filled in."""
        options = Line([None, 1.5, 0], ["a", "b", "c"]).options()
        assert options["series"][0]["data"] == [None, 1.5, 0]
