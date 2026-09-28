"""The package's Django app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MvpChartsConfig(AppConfig):
    """Register the chart component and its template tag."""

    name = "mvp_charts"
    label = "mvp_charts"
    verbose_name = _("Charts")
