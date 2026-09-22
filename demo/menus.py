"""Sidebar navigation for the demo project.

The tree is registered by :meth:`demo.apps.DemoConfig.ready` importing this
module.

Adding a chart type's page is one entry in ``CHART_TYPE_PAGES``. Nothing else
here changes.
"""

from flex_menu import MenuItem
from mvp.menus import AppMenu, MenuGroup

#: One entry per chart type, in the order they should read in the sidebar.
#:
#: The Charts group below is conditional on this holding at least one page,
#: because a navigation node is drawn from the leaf template until it has
#: children, so a node added with none renders as an inert button carrying
#: the literal text ``href="None"`` rather than as a section heading. Leaving
#: the group out until it holds a page is the only shape that draws correctly
#: at every point, and it costs nothing: the first chart type brought its
#: group with it.
CHART_TYPE_PAGES: list[MenuItem] = [
    MenuItem(
        name="line_chart",
        view_name="line_chart",
        extra_context={"label": "Line", "icon": "chart"},
    ),
]

AppMenu.extend(
    [
        MenuItem(
            name="overview",
            view_name="overview",
            extra_context={"label": "Overview", "icon": "overview"},
        ),
        MenuItem(
            name="chart_region",
            view_name="chart_region",
            extra_context={"label": "Chart region", "icon": "chart"},
        ),
    ]
)

if CHART_TYPE_PAGES:
    AppMenu.append(
        MenuGroup(
            name="charts",
            extra_context={"label": "Charts", "icon": "chart"},
            children=CHART_TYPE_PAGES,
        )
    )
