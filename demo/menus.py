"""Sidebar navigation for the demo project.

The tree is registered by :meth:`demo.apps.DemoConfig.ready` importing this
module.
"""

from flex_menu import MenuItem
from mvp.menus import AppMenu

AppMenu.extend(
    [
        MenuItem(
            name="overview",
            view_name="overview",
            extra_context={"label": "Overview", "icon": "overview"},
        ),
        MenuItem(
            name="chart_types",
            view_name="chart_types",
            extra_context={"label": "Chart types", "icon": "chart"},
        ),
        MenuItem(
            name="chart_options",
            view_name="chart_options",
            extra_context={"label": "Options", "icon": "chart"},
        ),
    ]
)
