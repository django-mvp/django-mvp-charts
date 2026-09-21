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
    ``"color"`` naming a theme role.

``values`` is shorthand for a ``series`` of one, so a chart never has two
different internal shapes. Everything below works on the ``series`` list.

Colour is not decided here. Every colour this module writes is a sentinel
string — ``mvp:slot-1``, ``mvp:base-content/70`` — resolved against the theme
the browser is actually running, because the theme is chosen in the browser and
can change without a page load. The same sentinels work inside a raw ``options``
object, so the escape hatch stays themed rather than dropping to literal colours.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from django.utils.translation import gettext_lazy as _

#: How many categorical slots the palette offers before it stops assigning.
#:
#: The browser derives them from the theme's own primary colour. Six is where
#: the derivation still clears a distinguishability check on every theme the
#: demo offers; past it, a chart has more series than colour can carry and the
#: honest remedy is folding the tail together or splitting the chart, neither of
#: which a component can decide on the author's behalf.
PALETTE_SLOTS = 6

#: The wording shown in place of a chart that has nothing to draw.
DEFAULT_EMPTY_MESSAGE = _("No data to chart.")

#: What an unnamed tail of pie slices is called once it has been folded together.
OTHER_SLICE_LABEL = _("Other")


class Attribute:
    """Reading one attribute that may arrive as a Python object or as text.

    A component attribute reaches a template two ways. ``labels="Jan,Feb"`` is
    text the author typed; ``:labels="months"`` is the list a view built. Both
    have to end up as the same Python value, and the rule is one sentence: a
    string that starts with ``[`` or ``{`` is JSON, any other string is a
    comma-separated list, and anything that is not a string is already the value.

    Grouped on a class rather than left as four module-level functions because
    they share a subject — one attribute's value — and because a project that
    needs a different reading has something to subclass (Article XI).
    """

    @classmethod
    def value(cls, raw: Any) -> Any:
        """The Python value behind one attribute."""
        if not isinstance(raw, str):
            return raw
        text = raw.strip()
        if not text:
            return None
        if text[0] in "[{":
            return json.loads(text)
        return [cls.scalar(part.strip()) for part in text.split(",")]

    @classmethod
    def scalar(cls, text: str) -> Any:
        """A single comma-separated item, as a number where it reads as one."""
        try:
            number = float(text)
        except ValueError:
            return text
        return int(number) if number.is_integer() and "." not in text else number

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

    Carries the charting libraries' own meaning of the word (``CONTEXT.md``),
    plus the one thing this package adds: ``color`` may name a theme role, so a
    series that *means* something — errors, revenue — can say so instead of
    taking whatever slot its position landed on.
    """

    def __init__(
        self, data: Sequence[Any], name: str = "", color: str = ""
    ) -> None:
        self.data = list(data or [])
        self.name = name
        self.color = color

    @classmethod
    def read(cls, raw: Any) -> list["Series"]:
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

    def slot_color(self, index: int) -> str:
        """The sentinel this series' marks are painted with.

        A named role wins over the slot, which is the whole point of naming one.
        Past the palette's last slot the sentinel still resolves — to the final
        slot — because a chart that silently drew two series in one colour would
        be worse than one that repeats a colour the author can see repeating.
        """
        if self.color:
            return f"mvp:{self.color}"
        return f"mvp:slot-{min(index + 1, PALETTE_SLOTS)}"


class Chart:
    """The options object one chart component hands to ECharts.

    Subclasses differ only in their axes and in what one datum is. Everything
    else — the grid, the legend, the tooltip, the ink colours, the empty case,
    the raw-options merge — is shared, because a vocabulary that means the same
    thing on four charts has to be built in one place to stay that way.
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
        empty: str = "",
        renderer: str = "canvas",
        **extra: Any,
    ) -> None:
        self.name = name
        self.description = description
        self.labels = [str(label) for label in (Attribute.value(labels) or [])]
        self.series = Series.read(series) or self._single_series(values)
        self.raw_options = Attribute.mapping(options)
        self.empty = empty or DEFAULT_EMPTY_MESSAGE
        self.renderer = "svg" if str(renderer).lower() == "svg" else "canvas"
        self.configure(**extra)

    def configure(self, **extra: Any) -> None:
        """Per-type attributes, for the subclasses that have any."""

    def _single_series(self, values: Any) -> list[Series]:
        data = Attribute.value(values)
        return [Series(data=data, name=self.name)] if data else []

    @classmethod
    def build(cls, config: Any = None, **attrs: Any) -> "Chart":
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

    @property
    def is_empty(self) -> bool:
        """Whether there is anything at all to draw."""
        return not any(series.data for series in self.series)

    def options(self) -> dict[str, Any]:
        """The full ECharts options object, with the raw ones merged last."""
        built: dict[str, Any] = {
            "animation": True,
            "textStyle": {"color": "mvp:base-content/70"},
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
            "backgroundColor": "mvp:base-100",
            "borderColor": "mvp:base-300",
            "textStyle": {"color": "mvp:base-content"},
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
            "textStyle": {"color": "mvp:base-content"},
        }

    def axes(self) -> dict[str, Any]:
        """The axes this chart type has, if any."""
        return {}

    def series_options(self) -> list[dict[str, Any]]:
        return [
            self.one_series(series, index)
            for index, series in enumerate(self.series)
        ]

    def one_series(self, series: Series, index: int) -> dict[str, Any]:
        return {
            "type": self.series_type,
            "name": series.name or self.name,
            "data": series.data,
            "itemStyle": {"color": series.slot_color(index)},
        }

    # -- shared axis pieces ---------------------------------------------------

    def category_axis(self) -> dict[str, Any]:
        """The axis that carries names rather than numbers."""
        return {
            "type": "category",
            "data": self.labels,
            "boundaryGap": self.series_type == "bar",
            "axisTick": {"show": False},
            "axisLine": {"lineStyle": {"color": "mvp:base-content/20"}},
            "axisLabel": {"color": "mvp:base-content/70"},
        }

    def value_axis(self) -> dict[str, Any]:
        """The axis that carries numbers.

        Gridlines are solid hairlines one step off the surface. Dashed ones read
        as a threshold or a projection when they are only a grid, and the axis
        line itself is dropped entirely because the gridlines already say where
        the values are.
        """
        return {
            "type": "value",
            "axisTick": {"show": False},
            "axisLine": {"show": False},
            "axisLabel": {"color": "mvp:base-content/70"},
            "splitLine": {
                "lineStyle": {"color": "mvp:base-content/12", "type": "solid"}
            },
        }

    # -- merging --------------------------------------------------------------

    @classmethod
    def _merge(
        cls, base: Mapping[str, Any], over: Mapping[str, Any]
    ) -> dict[str, Any]:
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
        color = series.slot_color(index)
        return {
            "type": "line",
            "name": series.name or self.name,
            "data": series.data,
            "showSymbol": len(series.data) <= self.MARKER_LIMIT,
            "symbolSize": 8,
            "lineStyle": {"width": 2, "cap": "round", "join": "round"},
            "itemStyle": {
                "color": color,
                # The ring is what keeps a marker readable where it crosses
                # another series' line, and it is drawn in the surface colour
                # so it reads as a gap rather than as an outline.
                "borderColor": "mvp:base-100",
                "borderWidth": 2,
            },
            # A gap in the data is a gap in the line, not a drop to zero.
            "connectNulls": False,
        }


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
                "color": series.slot_color(index),
                # Rounded at the data end, square at the baseline, so the bar
                # still starts from a single flat line.
                "borderRadius": radius,
            },
            "label": {
                "show": labelled,
                "position": "right" if self.horizontal else "top",
                "color": "mvp:base-content/70",
            },
        }


class Pie(Chart):
    """Part-to-whole, at a glance, for a handful of parts.

    Pie is the one chart type here whose defaults have to argue with the data.
    It stops being readable somewhere around six slices and stops being
    comparable well before that, so the component folds the tail together rather
    than drawing a ring of slivers nobody can tell apart. ``slices`` moves where
    that happens; it does not remove it.
    """

    series_type = "pie"
    tooltip_trigger = "item"

    def configure(self, slices: Any = PALETTE_SLOTS, **extra: Any) -> None:
        self.slices = max(2, int(slices or PALETTE_SLOTS))

    def legend(self) -> dict[str, Any] | None:
        """A pie's identity lives on its slices, which are directly labelled."""
        return None

    def grid(self) -> dict[str, Any]:
        """A pie has no grid; the radius below is what keeps its labels inside."""
        return {"left": 0, "right": 0, "top": 0, "bottom": 0}

    def axes(self) -> dict[str, Any]:
        return {}

    def slices_data(self) -> list[dict[str, Any]]:
        """Named values, biggest first, with the tail folded into one slice."""
        values = self.series[0].data if self.series else []
        named = [
            {
                "name": self.labels[i] if i < len(self.labels) else str(i + 1),
                "value": value,
            }
            for i, value in enumerate(values)
            if value is not None
        ]
        named.sort(key=lambda entry: entry["value"], reverse=True)
        if len(named) <= self.slices:
            return named
        head, tail = named[: self.slices - 1], named[self.slices - 1 :]
        return [
            *head,
            {
                "name": str(OTHER_SLICE_LABEL),
                "value": sum(entry["value"] for entry in tail),
            },
        ]

    def series_options(self) -> list[dict[str, Any]]:
        data = [
            {**entry, "itemStyle": {"color": f"mvp:slot-{min(i + 1, PALETTE_SLOTS)}"}}
            for i, entry in enumerate(self.slices_data())
        ]
        return [
            {
                "type": "pie",
                "name": self.name,
                # Leaves room for the labels and their leader lines, which are
                # how a pie says what each slice is without a legend.
                "radius": ["0%", "62%"],
                "center": ["50%", "52%"],
                "avoidLabelOverlap": True,
                "minAngle": 2,
                "data": data,
                "itemStyle": {
                    # A 2px separation in the surface colour, not a stroke.
                    "borderColor": "mvp:base-100",
                    "borderWidth": 2,
                },
                "label": {
                    "color": "mvp:base-content/70",
                    "formatter": "{b}  {d}%",
                },
                "labelLine": {"lineStyle": {"color": "mvp:base-content/30"}},
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
            "itemStyle": {
                "color": series.slot_color(index),
                "opacity": 0.85,
                "borderColor": "mvp:base-100",
                "borderWidth": 2,
            },
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
