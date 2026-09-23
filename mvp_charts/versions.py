"""What this package is known to render against.

The package does not ship ECharts and does not depend on it, so there is no
dependency specifier anywhere stating which versions work. That leaves the
question unanswered unless it is answered here, and a consumer choosing what
to bundle has no other place to look.
"""

#: The ECharts versions this package is known to render against.
#:
#: A range rather than a pin. The package reads one global and calls two of
#: its methods, so it is compatible with far more than it is tested against,
#: and pinning would claim a precision it neither has nor wants. It is also
#: not enforced anywhere: the project chooses what to load, and a version
#: outside this range is untested rather than blocked.
#:
#: pyecharts builds the options, so the lower bound is really its bound too.
#: pyecharts 2.1.0 is the first release that targets ECharts 6.
ECHARTS_SUPPORTED_VERSIONS = ">=6.0,<7.0"
