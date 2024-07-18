import logging
import requests
import json
from django.conf import settings

from .config import app


logger = logging.getLogger(__name__)

use_logger_queue = getattr(settings, 'USE_LOGGER_QUEUE_NAME', None)
task_decorator = app.task(queue=use_logger_queue) if use_logger_queue else app.task

@task_decorator
def record_in_clickhouse(data, *args):
    """ Производит запись в clickhouse """

    data = json.loads(data)
    data["server_name"] = getattr(
        settings, 'DJANGO_CLICKHOUSE_SERVER_NAME', 'development')
    clickhouse_host = settings.DJANGO_CLICKHOUSE_LOGGER_HOST
    clickhouse_port = settings.DJANGO_CLICKHOUSE_LOGGER_PORT
    clickhouse_user = settings.DJANGO_CLICKHOUSE_LOGGER_USER
    clickhouse_password = settings.DJANGO_CLICKHOUSE_LOGGER_PASSWORD

    query = "INSERT INTO clickhouse.logs FORMAT JSONEachRow"
    url = f"http://{clickhouse_host}:{clickhouse_port}/"
    auth = (clickhouse_user, clickhouse_password)
    try:
        response = requests.post(url, params={"query": query}, data=json.dumps(data), auth=auth)
    except Exception as e:
        logger.error(f'Error connection clickhouse {e}')
        print('Error connection in clickhouse', e)
        return

    if response.status_code != 200:
        logger.error(f'Error clickhouse status {response.text}')
        print(f"Error clickhouse status: {response.text}")
