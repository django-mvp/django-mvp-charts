"""The options object a line chart asks ECharts to draw."""

from typing import Any


class Attribute:
    """One attribute's Python value, exactly as the template author wrote it.

    A value left at ``<c-vars>``'s empty default reads as not given.
    Everything else — including ``0``, ``0.0`` and a string — is returned
    untouched: this class splits nothing, parses nothing and reports nothing
    (FR-002a).
    """

    def __init__(self, raw):
        self.raw = raw

    @property
    def given(self) -> bool:
        return bool(self.raw != "")

    @property
    def value(self):
        return self.raw if self.given else None


class Line:
    """The options object for a line chart: labels, values, nothing else.

    No grid, tooltip, legend, animation, colour, line width, symbol, axis
    tick or split line (FR-013) — every one of those is an appearance
    decision, and this package makes none.
    """

    def __init__(self, values, labels):
        self.values = Attribute(values)
        self.labels = Attribute(labels)

    def options(self) -> dict:
        x_axis = {"type": "category"}
        if self.labels.given:
            x_axis["data"] = self.labels.value
        return {
            "xAxis": x_axis,
            "yAxis": {"type": "value"},
            "series": [
                {
                    "type": "line",
                    "data": self.values.value if self.values.given else [],
                }
            ],
        }


class Merge:
    """An author's `options` attribute, deep-merged over what this package built.

    A mapping merges recursively and the override wins on every key it
    names. A list replaces a list, because there is no position to merge two
    arbitrary lists against. `series` is the one exception: its entries are
    matched by position and merged like mappings, so an option added to an
    entry keeps that entry's own data. No key is filtered anywhere the merge
    looks, including one this package has never heard of (FR-012).
    """

    def __init__(self, base: dict, overrides: dict):
        self.base = base
        self.overrides = overrides

    def result(self) -> dict:
        # The annotated local is what narrows `merge`'s `Any` return to `dict`;
        # returning the call directly is a mypy `no-any-return`.
        merged: dict = self.merge(self.base, self.overrides)
        return merged

    def merge(self, base: Any, overrides: Any) -> Any:
        if not isinstance(base, dict) or not isinstance(overrides, dict):
            return overrides
        merged = dict(base)
        for key, value in overrides.items():
            if key == "series":
                merged[key] = self.merge_series(merged.get("series"), value)
            else:
                merged[key] = self.merge(merged.get(key), value)
        return merged

    def merge_series(self, base_series: Any, override_series: Any) -> Any:
        if not isinstance(base_series, list) or not isinstance(override_series, list):
            return override_series
        length = max(len(base_series), len(override_series))
        merged = []
        for position in range(length):
            if position >= len(override_series):
                merged.append(base_series[position])
            elif position >= len(base_series):
                merged.append(override_series[position])
            else:
                merged.append(
                    self.merge(base_series[position], override_series[position])
                )
        return merged
