"""Tests for the options object a line chart asks ECharts to draw.

Python only, mirroring ``mvp_charts/echarts/options.py`` (Article X). No
Cotton compilation here — the rendered-output contract is covered in
``tests/test_components/test_line.py``.
"""

from mvp_charts.echarts.options import Attribute, Line, Merge


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


class TestMerge:
    """An `options` attribute deep-merged over what this package built (FR-012).

    Mappings merge recursively, a list replaces a list, `series` is the one
    exception and merges entry by entry against position, and no key is
    filtered anywhere - including one this package has never heard of.
    """

    def test_a_mapping_merges_deeply(self):
        base = {"xAxis": {"type": "category", "data": ["Jan", "Feb"]}}
        overrides = {"xAxis": {"axisLine": {"show": False}}}
        merged = Merge(base, overrides).result()
        assert merged == {
            "xAxis": {
                "type": "category",
                "data": ["Jan", "Feb"],
                "axisLine": {"show": False},
            }
        }

    def test_the_overrides_value_wins_on_a_key_both_sides_name(self):
        base = {"yAxis": {"type": "value"}}
        overrides = {"yAxis": {"type": "log"}}
        merged = Merge(base, overrides).result()
        assert merged["yAxis"]["type"] == "log"

    def test_a_list_replaces_a_list_rather_than_merging_element_by_element(self):
        base = {"color": ["red", "blue", "green"]}
        overrides = {"color": ["purple"]}
        merged = Merge(base, overrides).result()
        assert merged["color"] == ["purple"]

    def test_series_merges_entry_by_entry_against_position(self):
        """An option added to a series entry keeps that entry's own data."""
        base = {"series": [{"type": "line", "data": [1, 2, 3]}]}
        overrides = {"series": [{"lineStyle": {"color": "#7c3aed"}}]}
        merged = Merge(base, overrides).result()
        assert merged["series"] == [
            {"type": "line", "data": [1, 2, 3], "lineStyle": {"color": "#7c3aed"}}
        ]

    def test_series_merge_leaves_an_unnamed_position_untouched(self):
        base = {
            "series": [
                {"type": "line", "data": [1, 2, 3]},
                {"type": "line", "data": [4, 5, 6]},
            ]
        }
        overrides = {"series": [{"lineStyle": {"color": "red"}}]}
        merged = Merge(base, overrides).result()
        assert merged["series"][0]["lineStyle"] == {"color": "red"}
        assert merged["series"][1] == {"type": "line", "data": [4, 5, 6]}

    def test_series_merge_carries_an_entry_beyond_the_base_length(self):
        base = {"series": [{"type": "line", "data": [1, 2, 3]}]}
        overrides = {"series": [{}, {"type": "bar", "data": [7, 8, 9]}]}
        merged = Merge(base, overrides).result()
        assert merged["series"][1] == {"type": "bar", "data": [7, 8, 9]}

    def test_a_key_this_package_has_never_heard_of_arrives_unchanged(self):
        base = {"xAxis": {"type": "category"}}
        overrides = {"toolbox": {"feature": {"saveAsImage": {}}}}
        merged = Merge(base, overrides).result()
        assert merged["toolbox"] == {"feature": {"saveAsImage": {}}}

    def test_nothing_named_by_the_base_is_dropped(self):
        base = {"xAxis": {"type": "category"}, "yAxis": {"type": "value"}}
        overrides = {"grid": {"top": 40}}
        merged = Merge(base, overrides).result()
        assert merged["xAxis"] == {"type": "category"}
        assert merged["yAxis"] == {"type": "value"}
