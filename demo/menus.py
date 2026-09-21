"""Sidebar navigation for the demo project.

The tree is registered by :meth:`demo.apps.DemoConfig.ready` importing this
module.

Adding a chart page is one entry in ``CHART_PAGES``. Nothing else here changes.
"""

from flex_menu import MenuItem
from mvp.menus import AppMenu, MenuCollapse

#: One entry per chart demo page, in the order they should read in the sidebar.
#:
#: Empty until the first chart component exists, which is why the Charts
#: section below is conditional. A navigation node is drawn from the leaf
#: template until it has children, so a node added with none renders as an
#: inert button carrying the literal text ``href="None"`` — not as a section
#: heading, and not as something that expands. That holds for both of the
#: container classes django-mvp offers, so there is no choice between them that
#: avoids it. Leaving the section out until it holds a page is the only shape
#: that draws correctly at every point, and it costs nothing: the first chart
#: page brings its section with it.
CHART_PAGES: list[MenuItem] = [
    MenuItem(
        name="chart_region",
        view_name="chart_region",
        extra_context={"label": "Chart region", "icon": "chart"},
    ),
    MenuItem(
        name="chart_region_failures",
        view_name="chart_region_failures",
        extra_context={"label": "When a region cannot draw", "icon": "info"},
    ),
]

AppMenu.extend(
    [
        MenuItem(
            name="overview",
            view_name="overview",
            extra_context={"label": "Overview", "icon": "overview"},
        ),
    ]
)

if CHART_PAGES:
    AppMenu.append(
        MenuCollapse(
            name="charts",
            extra_context={"label": "Charts", "icon": "chart"},
            children=CHART_PAGES,
        )
    )
