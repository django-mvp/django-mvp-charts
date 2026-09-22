"""One vocabulary, four chart types, and the ECharts options they build.

Three words carry the data on every chart type in this namespace, and they mean
the same thing on each:

``labels``
    What the things being drawn are called — the category axis on a line or a
    bar chart, the slice names on a pie. A scatter chart has none, because its
    points are positioned by two numbers rather than named.
``values``
    One run of numbers, for a chart with a single series. On a scatter chart a
    "number" is a pair.
``series``
    Several named runs, each ``{"name": …, "data": [...]}``, with an optional
    ``"color"``.

``values`` is shorthand for a ``series`` of one, so a chart never has two
different internal shapes. Everything below works on the ``series`` list.

**Colour belongs to the charting library, not to this package.** Nothing here
writes a colour. Series take ECharts' own palette, and a project that wants its
charts to match its theme says so itself — per series with ``color``, or across
a chart with ``options.color``. Deriving a palette from the running daisyUI
theme was built and then removed: it costs a colour-space implementation, a
mutation observer and a repaint path, and it makes the package responsible for a
guarantee no charting library offers.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


class Attribute:
    """Reading one attribute that carries data rather than text.

    **Data and configuration arrive as Python values, written with a colon.**
    ``:values="[12, 14, 15]"`` and ``:values="revenue"`` are both a list by the
    time they reach here; ``values="12,14,15"`` is a string, and it is refused.

    The refusal is the point. A component that split a string on commas would be
    inventing a data format: it has to decide what a comma inside a label means,
    what an empty item is, and which strings look enough like numbers to become
    them — decisions nobody asked for, made silently, and wrong at the edges.
    Python already has a list, Cotton already passes one, and a chart is far
    more often fed from a view than typed out.

    Grouped on a class rather than left as loose functions because they share a
    subject — one attribute's value — and because a project that needs a
    different reading has something to subclass (Article XI).
    """

    @classmethod
    def value(cls, raw: Any) -> Any:
        """The Python value behind one attribute."""
        if raw is None or raw == "":
            return None
        if isinstance(raw, str):
            raise TypeError(
                "a chart's data has to be a Python value, not text: write "
                f':attribute="[…]" or :attribute="variable", not ="{raw[:40]}"'
            )
        return raw

    @classmethod
    def flag(cls, raw: Any) -> bool:
        """A boolean attribute, which Cotton delivers as ``True`` or as text."""
        if isinstance(raw, str):
            return raw.strip().lower() not in {"", "false", "0", "no", "off"}
        return bool(raw)

    @classmethod
    def mapping(cls, raw: Any) -> dict[str, Any]:
        """An attribute that has to be a mapping — ``config`` and ``options``."""
        if raw in (None, ""):
            return {}
        value = cls.value(raw)
        if not isinstance(value, Mapping):
            raise TypeError(f"expected a mapping, got {type(value).__name__}")
        return dict(value)


class Series:
    """One run of values drawn as a single visual run.

    Carries the charting libraries' own meaning of the word (``CONTEXT.md``).
    ``color`` is forwarded to ECharts untouched: any colour it understands, and
    the package neither derives it nor checks it. A series whose colour means
    something — errors in red — says so here, and a project matching its charts
    to its site says so here or in ``options.color``.
    """

    def __init__(self, data: Sequence[Any], name: str = "", color: str = "") -> None:
        self.data = list(data or [])
        self.name = name
        self.color = color

    @classmethod
    def read(cls, raw: Any) -> list[Series]:
        """The ``series`` attribute as a list of series."""
        value = Attribute.value(raw)
        if not value:
            return []
        if isinstance(value, Mapping):
            value = [value]
        out: list[Series] = []
        for entry in value:
            if isinstance(entry, Mapping):
                out.append(
                    cls(
                        data=entry.get("data") or entry.get("values") or [],
                        name=str(entry.get("name", "")),
                        color=str(entry.get("color", "")),
                    )
                )
            else:
                # A bare list among the series is one unnamed run of values.
                out.append(cls(data=entry))
        return out

    def item_style(self) -> dict[str, Any]:
        """What this series' marks are painted with, when it says.

        An empty dict when it does not, so the key is absent from the options
        object entirely and ECharts reaches for its own palette. Writing
        ``{"color": None}`` instead would be this package making a colour
        decision and calling it none.
        """
        return {"color": self.color} if self.color else {}


class Chart:
    """The options object one chart component hands to ECharts.

    Subclasses differ only in their axes and in what one datum is. Everything
    else — the grid, the legend, the tooltip, the raw-options merge — is
    shared, because a vocabulary that means the same thing on four charts has
    to be built in one place to stay that way.

    **A chart with no data is a chart with no data.** The options are built and
    handed over exactly as they are for any other, and ECharts draws whatever
    it draws for an empty series. The package writes no message, because what a
    page should show when it has nothing to plot is the page's decision, and
    one made here could not be undone from a template.
    """

    #: The ECharts series type this chart draws.
    series_type = ""

    #: What the tooltip follows: the axis position, or the mark under the cursor.
    tooltip_trigger = "axis"

    #: The shape drawn under the cursor to show which values are being read.
    axis_pointer = "line"

    def __init__(
        self,
        *,
        name: str = "",
        description: str = "",
        labels: Any = None,
        values: Any = None,
        series: Any = None,
        options: Any = None,
        **extra: Any,
    ) -> None:
        self.name = name
        self.description = description
        self.labels = [str(label) for label in (Attribute.value(labels) or [])]
        self.series = Series.read(series) or self._single_series(values)
        self.raw_options = Attribute.mapping(options)
        self.configure(**extra)

    def configure(self, **extra: Any) -> None:
        """Per-type attributes, for the subclasses that have any."""

    def _single_series(self, values: Any) -> list[Series]:
        data = Attribute.value(values)
        return [Series(data=data, name=self.name)] if data else []

    @classmethod
    def build(cls, config: Any = None, **attrs: Any) -> Chart:
        """One chart from a config object and the attributes written on the tag.

        The precedence rule, which is the whole answer to "what happens when the
        two disagree": **the tag wins.** A config object is the general
        statement a view made; an attribute is the specific one this template
        makes about this chart, and it is the one a reader of the template can
        see. That is the same order django-mvp already resolves everything in —
        component attribute, then configuration, then the default.

        Raw ``options`` are the exception, and deliberately: they are merged
        over the finished object rather than competing with an attribute,
        because reaching for a raw option is how an author says they want
        something no attribute offers.
        """
        settings = Attribute.mapping(config)
        for key, value in attrs.items():
            if not cls._written(value):
                continue
            settings[key] = value
            # `values` and `series` are two spellings of one thing — a series of
            # one, and several. Writing either on the tag replaces whatever the
            # config object said in the other, because otherwise "the tag wins"
            # would be true key by key and false for the chart: a tag saying
            # `values` while the object says `series` would silently draw the
            # object's data.
            if key in ("values", "series"):
                settings.pop("series" if key == "values" else "values", None)
        options = cls._merge(
            Attribute.mapping(Attribute.mapping(config).get("options")),
            Attribute.mapping(attrs.get("options")),
        )
        settings["options"] = options
        return cls(**settings)

    @staticmethod
    def _written(value: Any) -> bool:
        """Whether an attribute was actually written on the tag.

        Every component declares its attributes with an empty default, so an
        attribute nobody wrote and one written empty arrive identically — which
        is what stops a component's own default from beating a config object
        that did say something. The defaults live in Python instead, below.

        `0` and `0.0` are values somebody wrote. A plain `if value` would drop
        them, and so would testing against a tuple containing `False`, because
        `0 == False`.
        """
        if value is None or value is False:
            return False
        return not (isinstance(value, str) and not value.strip())

    # -- the options object ---------------------------------------------------

    def options(self) -> dict[str, Any]:
        """The full ECharts options object, with the raw ones merged last."""
        built: dict[str, Any] = {
            "animation": True,
            "grid": self.grid(),
            "tooltip": self.tooltip(),
            "series": self.series_options(),
        }
        built.update(self.axes())
        legend = self.legend()
        if legend:
            built["legend"] = legend
        merged = self._merge(built, self.raw_options)
        merged["series"] = self._merge_series(
            built["series"], self.raw_options.get("series")
        )
        return merged

    @classmethod
    def _merge_series(
        cls, built: list[dict[str, Any]], over: Any
    ) -> list[dict[str, Any]]:
        """Raw options about a series, merged onto the series they are about.

        `series` is the one list merged entry by entry rather than replaced.
        Everywhere else replacing is right, because a list of axis names or of
        colours is one statement and an author has to be able to take it back.
        A series entry is not: it is identified by its position, the component
        built the one at that position, and an author adding an area fill to the
        second series means the second series — not "a new series with nothing
        in it but an area fill", which is what replacement gives them and which
        is never what anyone wanted.
        """
        if not isinstance(over, Sequence) or isinstance(over, str):
            return built
        out = [dict(entry) for entry in built]
        for index, extra in enumerate(over):
            if not isinstance(extra, Mapping):
                continue
            if index < len(out):
                out[index] = cls._merge(out[index], extra)
            else:
                out.append(dict(extra))
        return out

    def grid(self) -> dict[str, Any]:
        """The plot's box inside the region.

        ``containLabel`` is what keeps the axis labels inside the region rather
        than clipped by it — a plot that fits while its axis does not is the
        commonest way a chart ends up with its own little scrollbar.
        """
        return {
            "left": 8,
            "right": 16,
            "top": 16,
            "bottom": 32 if self.legend() else 8,
            "containLabel": True,
        }

    def tooltip(self) -> dict[str, Any]:
        return {
            "trigger": self.tooltip_trigger,
            "axisPointer": {"type": self.axis_pointer},
        }

    def legend(self) -> dict[str, Any] | None:
        """A legend for two or more series, and none for one.

        With one series there is one colour, and the chart's accessible name
        already says what is plotted — a box with a single swatch restates the
        title and costs space. With two or more it is the identity channel that
        does not depend on telling colours apart, so it is never optional.
        """
        if len(self.series) < 2:
            return None
        return {
            "type": "scroll",
            "bottom": 0,
            "icon": "circle",
            "itemWidth": 10,
            "itemHeight": 10,
        }

    def axes(self) -> dict[str, Any]:
        """The axes this chart type has, if any."""
        return {}

    def series_options(self) -> list[dict[str, Any]]:
        return [
            self.one_series(series, index) for index, series in enumerate(self.series)
        ]

    def one_series(self, series: Series, index: int) -> dict[str, Any]:
        built: dict[str, Any] = {
            "type": self.series_type,
            "name": series.name or self.name,
            "data": series.data,
        }
        style = series.item_style()
        if style:
            built["itemStyle"] = style
        return built

    # -- shared axis pieces ---------------------------------------------------

    def category_axis(self) -> dict[str, Any]:
        """The axis that carries names rather than numbers."""
        return {
            "type": "category",
            "data": self.labels,
            "boundaryGap": self.series_type == "bar",
            "axisTick": {"show": False},
        }

    def value_axis(self) -> dict[str, Any]:
        """The axis that carries numbers.

        Gridlines stay solid: a dashed one reads as a threshold or a projection
        when it is only a grid. The axis line itself is dropped, because the
        gridlines already say where the values are. Neither is a colour
        decision — what shade they come out is ECharts'.
        """
        return {
            "type": "value",
            "axisTick": {"show": False},
            "axisLine": {"show": False},
            "splitLine": {"lineStyle": {"type": "solid"}},
        }

    # -- merging --------------------------------------------------------------

    @classmethod
    def _merge(cls, base: Mapping[str, Any], over: Mapping[str, Any]) -> dict[str, Any]:
        """Deep-merge ``over`` onto ``base``, mappings recursively.

        A list replaces a list rather than merging item by item. Merging two
        lists of series would give an author no way to *remove* one, and an
        option they cannot take back is worse than one they have to restate.
        """
        out = dict(base)
        for key, value in (over or {}).items():
            if isinstance(value, Mapping) and isinstance(out.get(key), Mapping):
                out[key] = cls._merge(out[key], value)
            else:
                out[key] = value
        return out


class Line(Chart):
    """Trend over time, or any value read along an ordered category axis."""

    series_type = "line"

    #: Above this many points a marker per point stops reading as a marker and
    #: starts reading as a thick line, so the line carries the shape alone.
    MARKER_LIMIT = 12

    def axes(self) -> dict[str, Any]:
        category = self.category_axis()
        category["splitLine"] = {"show": False}
        return {"xAxis": category, "yAxis": self.value_axis()}

    def one_series(self, series: Series, index: int) -> dict[str, Any]:
        built: dict[str, Any] = {
            "type": "line",
            "name": series.name or self.name,
            "data": series.data,
            "showSymbol": len(series.data) <= self.MARKER_LIMIT,
            "symbolSize": 8,
            "lineStyle": {"width": 2, "cap": "round", "join": "round"},
            # A gap in the data is a gap in the line, not a drop to zero.
            "connectNulls": False,
        }
        style = series.item_style()
        if style:
            built["itemStyle"] = style
        return built


class Bar(Chart):
    """Magnitude compared across categories.

    ``horizontal`` is the one variant with its own attribute, because long
    category names are the ordinary reason a bar chart is unreadable and turning
    the chart is the ordinary fix. Everything else a bar chart can be — stacked,
    grouped a particular way — stays in raw options until it has earned a name.
    """

    series_type = "bar"
    axis_pointer = "shadow"

    #: Above this many bars a value on every cap stops being a label and starts
    #: being noise, so the axis carries the values instead.
    LABEL_LIMIT = 8

    def configure(self, horizontal: Any = False, **extra: Any) -> None:
        self.horizontal = Attribute.flag(horizontal)

    def axes(self) -> dict[str, Any]:
        category = self.category_axis()
        value = self.value_axis()
        if self.horizontal:
            category["splitLine"] = {"show": False}
            category["inverse"] = True
            return {"yAxis": category, "xAxis": value}
        category["splitLine"] = {"show": False}
        return {"xAxis": category, "yAxis": value}

    def one_series(self, series: Series, index: int) -> dict[str, Any]:
        labelled = len(self.series) == 1 and len(series.data) <= self.LABEL_LIMIT
        radius = [0, 4, 4, 0] if self.horizontal else [4, 4, 0, 0]
        return {
            "type": "bar",
            "name": series.name or self.name,
            "data": series.data,
            # Capped rather than filling its slot: the leftover in the band is
            # the air that stops a bar chart reading as a solid block.
            "barMaxWidth": 24,
            "barGap": "8%",
            "itemStyle": {
                # Rounded at the data end, square at the baseline, so the bar
                # still starts from a single flat line.
                "borderRadius": radius,
                **series.item_style(),
            },
            "label": {
                "show": labelled,
                "position": "right" if self.horizontal else "top",
            },
        }


class Pie(Chart):
    """Part-to-whole, at a glance, for a handful of parts.

    **The slices are the values given, in the order given.** A pie does stop
    being readable somewhere around six slices, and a long tail of slivers is
    usually better summed into one — but that is a judgement about the data, and
    reading the data is the project's job (README, *Scope & philosophy*). Both
    are a line of Python in the view that already produced the values. Neither
    can be undone from a template once a component has done it.
    """

    series_type = "pie"
    tooltip_trigger = "item"

    def legend(self) -> dict[str, Any] | None:
        """A pie's identity lives on its slices, which are directly labelled."""
        return None

    def grid(self) -> dict[str, Any]:
        """A pie has no grid; the radius below is what keeps its labels inside."""
        return {"left": 0, "right": 0, "top": 0, "bottom": 0}

    def axes(self) -> dict[str, Any]:
        return {}

    def slices(self) -> list[dict[str, Any]]:
        """Each value paired with its label, in the order they arrived."""
        values = self.series[0].data if self.series else []
        return [
            {
                "name": self.labels[i] if i < len(self.labels) else str(i + 1),
                "value": value,
            }
            for i, value in enumerate(values)
            if value is not None
        ]

    def series_options(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "pie",
                "name": self.name,
                # Leaves room for the labels and their leader lines, which are
                # how a pie says what each slice is without a legend.
                "radius": ["0%", "62%"],
                "center": ["50%", "52%"],
                "avoidLabelOverlap": True,
                "data": self.slices(),
                "label": {"formatter": "{b}  {d}%"},
            }
        ]


class Scatter(Chart):
    """The relationship between two numbers, one point per observation.

    The one chart type whose datum is a pair rather than a number, which is why
    it is built alongside the other three rather than after them: a vocabulary
    that has only ever met a series of numbers does not survive meeting this.
    It has no ``labels``, because nothing here is named by position.
    """

    series_type = "scatter"
    tooltip_trigger = "item"
    axis_pointer = "cross"

    def axes(self) -> dict[str, Any]:
        x = self.value_axis()
        y = self.value_axis()
        # Both axes carry numbers, so both get gridlines: a point's position
        # means nothing without being readable against each.
        x["scale"] = True
        y["scale"] = True
        return {"xAxis": x, "yAxis": y}

    def one_series(self, series: Series, index: int) -> dict[str, Any]:
        return {
            "type": "scatter",
            "name": series.name or self.name,
            "data": series.data,
            "symbolSize": 10,
            # Overlapping points stay individually visible rather than merging
            # into one solid mass, which is the whole failure mode of a scatter
            # chart with any density to it.
            "itemStyle": {"opacity": 0.85, **series.item_style()},
        }


#: Which class a component tag resolves to. The key is the chart type, the
#: second segment of the tag, so `<c-echarts.line>` and `CHART_TYPES["line"]`
#: cannot drift apart without one of them failing loudly.
CHART_TYPES: dict[str, type[Chart]] = {
    "line": Line,
    "bar": Bar,
    "pie": Pie,
    "scatter": Scatter,
}
