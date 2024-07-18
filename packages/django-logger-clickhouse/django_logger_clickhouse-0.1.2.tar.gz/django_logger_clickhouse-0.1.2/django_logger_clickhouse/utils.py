import requests

from django.conf import settings

from .config import check_settings


def ensure_clickhouse_db_and_table_exist():
    check_settings()

    clickhouse_host = settings.DJANGO_CLICKHOUSE_LOGGER_HOST
    clickhouse_port = settings.DJANGO_CLICKHOUSE_LOGGER_PORT
    clickhouse_user = settings.DJANGO_CLICKHOUSE_LOGGER_USER
    clickhouse_password = settings.DJANGO_CLICKHOUSE_LOGGER_PASSWORD

    # Строим URL для ClickHouse
    url = f"http://{clickhouse_host}:{clickhouse_port}/"

    # SQL запросы для создания базы данных и таблицы
    create_db_query = "CREATE DATABASE IF NOT EXISTS clickhouse;"
    create_table_query = """
    CREATE TABLE IF NOT EXISTS clickhouse.logs
    (
      uuid String,
      created_dt DateTime64(3),
      pathname Nullable(String),
      funcName Nullable(String),
      lineno Nullable(Int32),
      message Nullable(String),
      exc_text Nullable(String),
      created Nullable(Float64),
      filename Nullable(String),
      levelname Nullable(String),
      levelno Nullable(String),
      module Nullable(String),
      msecs Nullable(Float64),
      msg Nullable(String),
      name Nullable(String),
      process Nullable(String),
      processName Nullable(String),
      relativeCreated Nullable(String),
      stack_info Nullable(String),
      thread Nullable(String),
      threadName Nullable(String),
      server_name Nullable(String)
    )
    ENGINE = MergeTree()
    PARTITION BY toDate(created_dt)
    ORDER BY (created_dt)
    SETTINGS min_bytes_for_wide_part = 0;
    """

    # Выполнение запросов
    try:
        response = requests.post(url, params={"query": create_db_query}, auth=(clickhouse_user, clickhouse_password))
        response.raise_for_status()
        response = requests.post(url, params={"query": create_table_query}, auth=(clickhouse_user, clickhouse_password))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"django_logger_clickhouse error: Failed to ensure ClickHouse DB and table exist: {e}")
