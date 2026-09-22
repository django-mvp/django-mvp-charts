"""What this namespace is known to render against.

The package does not ship ECharts and does not depend on it, so there is no
dependency specifier anywhere stating which versions work. That leaves the
question unanswered unless it is answered here, and a consumer choosing what
to bundle has no other place to look.

This is a statement about the `echarts` namespace, not about the package: a
second backend would state its own range beside this one.
"""

#: The ECharts versions this namespace is known to render against.
#:
#: A range rather than a pin. The package reads one global and calls nothing,
#: so it is compatible with far more than it is tested against, and pinning
#: would claim a precision the package neither has nor wants. It is also not
#: enforced anywhere: the project chooses what to load, and a version outside
#: this range is untested rather than blocked.
ECHARTS_SUPPORTED_VERSIONS = ">=6.0,<7.0"
