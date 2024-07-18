from __future__ import absolute_import, unicode_literals
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')

REQUIRED_SETTINGS = [
    'DJANGO_CLICKHOUSE_LOGGER_HOST',
    'DJANGO_CLICKHOUSE_LOGGER_PORT',
    'DJANGO_CLICKHOUSE_LOGGER_USER',
    'DJANGO_CLICKHOUSE_LOGGER_PASSWORD'
]


def check_settings():
    if 'django_logger_clickhouse' in settings.INSTALLED_APPS:
        for setting_name in REQUIRED_SETTINGS:
            if not hasattr(settings, setting_name):
                raise ImproperlyConfigured(
                    f'django_logger_clickhouseerror: Missing required setting: {setting_name}')
