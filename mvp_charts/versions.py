"""The ECharts versions this package is known to render against.

The package neither ships nor depends on ECharts, so no dependency specifier
states which versions work. This is the one place a consumer can look.
"""

#: The ECharts versions this package is known to render against. A range, not
#: a pin, and not enforced: a version outside it is untested rather than
#: blocked. pyecharts 2.1.0 is the first release that targets ECharts 6.
ECHARTS_SUPPORTED_VERSIONS = ">=6.0,<7.0"
