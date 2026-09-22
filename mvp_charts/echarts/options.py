"""The options object a line chart asks ECharts to draw."""


class Attribute:
    """One attribute's Python value, exactly as the template author wrote it.

    A value left at ``<c-vars>``'s empty default reads as not given.
    Everything else — including ``0``, ``0.0`` and a string — is returned
    untouched: this class splits nothing, parses nothing and reports nothing
    (FR-002a).
    """

    def __init__(self, raw):
        self._raw = raw

    @property
    def given(self) -> bool:
        return self._raw != ""

    @property
    def value(self):
        return self._raw if self.given else None


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
