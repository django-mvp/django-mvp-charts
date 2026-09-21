from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MvpChartsConfig(AppConfig):
    name = "mvp_charts"
    label = "mvp_charts"
    verbose_name = _("Charts")
