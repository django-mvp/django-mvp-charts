import math
import random
from datetime import date
from decimal import Decimal

from django.views.generic import TemplateView
from mvp.views import MVPTemplateView


class OverviewView(MVPTemplateView):
    """What this package is, and where the chart pages will appear."""

    template_name = "demo/overview.html"
    page_title = "Overview"
    page_subtitle = "Charts as Cotton components, one namespace per charting library"
    breadcrumbs = [{"text": "Overview"}]


class ChartRegionView(MVPTemplateView):
    """Placing a chart region, and several of them on one page."""

    template_name = "demo/chart_region.html"
    page_title = "Chart region"
    page_subtitle = (
        "The space a chart draws into, and how it behaves when nothing draws"
    )
    breadcrumbs = [{"text": "Chart region"}]


class ChartRegionNoLibraryView(TemplateView):
    """One region on a page with no charting library, for the frame above.

    Not in the navigation and not a page anyone visits. The check for the
    library reads a global, so it is a fact about the whole document — the
    only way to show that state beside a working one is to put it in a
    document of its own and embed it.
    """

    template_name = "demo/chart_region_no_library.html"


MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


class ChartTypeView(MVPTemplateView):
    """The four chart-type pages, each showing one component's whole surface.

    Every page holds the same ladder in the same order — written out, from a
    view, several series, built in Python, and reaching past the named
    attributes — because the point being demonstrated is that the ladder is the
    same whichever chart is on the page.

    The data is stub data and deliberately varied: a generated series is seeded
    so a page looks the same on every reload, which is what makes it possible to
    talk about what is on the screen.
    """

    breadcrumbs: list[dict[str, str]] = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["months"] = MONTHS
        return context


class LineChartView(ChartTypeView):
    template_name = "demo/line.html"
    page_title = "Line"
    page_subtitle = "A value read along an ordered category axis"
    breadcrumbs = [{"text": "Charts"}, {"text": "Line"}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rng = random.Random(11)  # noqa: S311 - stub data for a demo page, not a secret

        # Decimals and dates on purpose: these are what a view actually holds,
        # and the point of passing a Python value is not having to convert it.
        context["revenue"] = [
            Decimal(f"{12 + i * 1.4 + rng.random():.2f}") for i in range(12)
        ]

        context["traffic"] = [
            {
                "name": "Direct",
                "data": [420, 455, 470, 510, 545, 590, 610, 640, 705, 760, 790, 840],
            },
            {
                "name": "Search",
                "data": [310, 340, 395, 430, 480, 505, 560, 615, 650, 690, 745, 810],
            },
            {
                "name": "Referral",
                "data": [180, 175, 210, 225, 220, 260, 275, 290, 310, 305, 340, 370],
            },
        ]

        # A colour that means something rather than one that only tells two
        # series apart. The package does not choose it: `color` is handed to
        # ECharts as written, so a project matching its charts to its site
        # decides these two values, here or in options.color.
        context["health"] = [
            {
                "name": "Requests served",
                "data": [980, 992, 995, 988, 999, 1000, 997],
                "color": "#00a96e",
            },
            {"name": "Errors", "data": [20, 8, 5, 12, 1, 0, 3], "color": "#ff5861"},
        ]
        context["weekdays"] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        context["latency_chart"] = {
            "name": "Median response time",
            "description": (
                "Median response time in milliseconds for each month of the year, "
                "falling from 240 in January to 96 in December."
            ),
            "labels": MONTHS,
            "series": [
                {
                    "name": "Median",
                    "data": [240, 232, 218, 205, 190, 176, 165, 150, 138, 124, 110, 96],
                }
            ],
            "options": {
                "yAxis": {"axisLabel": {"formatter": "{value} ms"}, "min": 0},
            },
        }

        # A generated run, long enough that a marker per point would be noise.
        context["sensor_days"] = [str(date(2026, 1, 1 + (i % 28))) for i in range(120)]
        context["sensor"] = [
            round(14 + 6 * math.sin(i / 9) + rng.uniform(-1.2, 1.2), 2)
            for i in range(120)
        ]

        # Gaps, not zeroes: a missing reading is an absence, and a line that
        # dropped to the floor would claim a measurement nobody took.
        context["intermittent"] = [12, 15, None, None, 22, 19, None, 26, 31, 28]
        return context


class BarChartView(ChartTypeView):
    template_name = "demo/bar.html"
    page_title = "Bar"
    page_subtitle = "Magnitude compared across categories"
    breadcrumbs = [{"text": "Charts"}, {"text": "Bar"}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quarters"] = ["Q1", "Q2", "Q3", "Q4"]
        context["bookings"] = [148, 172, 165, 203]

        context["by_plan"] = [
            {"name": "Starter", "data": [62, 71, 68, 80]},
            {"name": "Team", "data": [48, 57, 61, 74]},
            {"name": "Enterprise", "data": [38, 44, 36, 49]},
        ]

        context["departments"] = [
            "Research and development",
            "Customer operations",
            "Sales and marketing",
            "Finance and legal",
            "People and workplace",
        ]
        context["headcount"] = [58, 41, 37, 16, 12]

        context["storage_chart"] = {
            "name": "Storage used by bucket",
            "description": (
                "Storage in terabytes across five buckets, from 41 in archive "
                "down to 4 in staging."
            ),
            "labels": ["Archive", "Media", "Backups", "Exports", "Staging"],
            "values": [41, 33, 21, 9, 4],
            "options": {"yAxis": {"axisLabel": {"formatter": "{value} TB"}}},
        }

        context["variance"] = [-12, 8, -3, 21, -18, 14]
        context["variance_labels"] = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        return context


class PieChartView(ChartTypeView):
    template_name = "demo/pie.html"
    page_title = "Pie"
    page_subtitle = "Part-to-whole, at a glance, for a handful of parts"
    breadcrumbs = [{"text": "Charts"}, {"text": "Pie"}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["channels"] = ["Direct", "Search", "Referral", "Social"]
        context["channel_share"] = [42, 31, 17, 10]

        # Twelve categories into a shape that stops being readable at six. The
        # component folds rather than drawing a ring of slivers.
        context["languages"] = [
            "Python",
            "JavaScript",
            "HTML",
            "CSS",
            "SQL",
            "Shell",
            "Dockerfile",
            "Makefile",
            "TOML",
            "YAML",
            "Markdown",
            "Nix",
        ]
        context["language_bytes"] = [
            412_000,
            188_000,
            96_000,
            74_000,
            41_000,
            22_000,
            9_400,
            6_100,
            4_800,
            3_900,
            2_700,
            900,
        ]

        context["spend_chart"] = {
            "name": "Spend by category",
            "description": (
                "Monthly spend split across four categories: hosting is the "
                "largest at 48 percent, then salaries, tooling and travel."
            ),
            "labels": ["Hosting", "Salaries", "Tooling", "Travel"],
            "values": [4800, 3100, 1450, 620],
        }

        context["long_names"] = [
            "Awaiting customer response",
            "In progress with engineering",
            "Scheduled for the next release",
            "Closed without a change",
        ]
        context["long_name_counts"] = [34, 22, 15, 47]
        return context


class ScatterChartView(ChartTypeView):
    template_name = "demo/scatter.html"
    page_title = "Scatter"
    page_subtitle = "The relationship between two numbers, one point per observation"
    breadcrumbs = [{"text": "Charts"}, {"text": "Scatter"}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rng = random.Random(7)  # noqa: S311 - stub data for a demo page, not a secret

        context["sizes"] = [
            [round(rng.uniform(1, 40), 1), round(rng.uniform(40, 900))]
            for _ in range(60)
        ]

        context["cohorts"] = [
            {
                "name": "Free",
                "data": [
                    [round(rng.uniform(1, 30), 1), round(rng.uniform(10, 240))]
                    for _ in range(45)
                ],
            },
            {
                "name": "Team",
                "data": [
                    [round(rng.uniform(10, 60), 1), round(rng.uniform(120, 520))]
                    for _ in range(45)
                ],
            },
            {
                "name": "Enterprise",
                "data": [
                    [round(rng.uniform(35, 95), 1), round(rng.uniform(380, 900))]
                    for _ in range(35)
                ],
            },
        ]

        context["correlation_chart"] = {
            "name": "Build time against test count",
            "description": (
                "Build duration in seconds plotted against the number of tests "
                "in the suite, for 80 recent builds. Longer suites take longer, "
                "with a wide spread above 600 tests."
            ),
            "series": [
                {
                    "name": "Builds",
                    "data": [
                        [n, round(18 + n * 0.21 + rng.uniform(-14, 22))]
                        for n in range(60, 940, 11)
                    ],
                }
            ],
            "options": {
                "xAxis": {"name": "Tests", "nameLocation": "middle", "nameGap": 28},
                "yAxis": {"name": "Seconds", "nameLocation": "middle", "nameGap": 40},
            },
        }

        context["dense"] = [
            [round(rng.gauss(50, 14), 1), round(rng.gauss(400, 110), 1)]
            for _ in range(600)
        ]
        return context
