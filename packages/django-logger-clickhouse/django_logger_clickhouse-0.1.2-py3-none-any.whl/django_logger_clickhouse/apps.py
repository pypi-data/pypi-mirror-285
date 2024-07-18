from django.apps import AppConfig


class DjangoClickhouseLoggerConfig(AppConfig):
    name = 'django_logger_clickhouse'
    verbose_name = 'ClickHouse Django Logger'

    def ready(self):
        from django.conf import settings

        if self.name in settings.INSTALLED_APPS:
            from .utils import ensure_clickhouse_db_and_table_exist
            from .config import check_settings

            check_settings()
            ensure_clickhouse_db_and_table_exist()
