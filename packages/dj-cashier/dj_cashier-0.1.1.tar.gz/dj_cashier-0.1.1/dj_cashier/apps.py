from django.apps import AppConfig
from django.conf import settings


class DjCashierConfig(AppConfig):
    default_auto_field = getattr(settings, 'DEFAULT_AUTO_FIELD', 'django.db.models.BigAutoField')
    name = 'dj_cashier'
