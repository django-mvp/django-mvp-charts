"""The ECharts backend: turning component attributes into an options object.

The template half of this namespace lives in
``mvp_charts/templates/cotton/echarts/``. This package is the Python half, and
the two are named for the charting library for the same reason (Article XIII).
"""

from mvp_charts.echarts.options import Bar, Chart, Line, Pie, Scatter, Series

__all__ = ["Bar", "Chart", "Line", "Pie", "Scatter", "Series"]
