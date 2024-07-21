import contextlib
import logging

from flask import current_app
from werkzeug.local import LocalProxy

with contextlib.suppress(ImportError):
    from celery.utils.log import get_task_logger


def __get_current_logger():
    # Without a context, the stderr logger is still valid
    if not current_app:
        return logging.getLogger("stderr")

    # If we're in celery, return a celery logger
    celery_app = current_app.extensions.get("celery")
    if celery_app and celery_app.current_worker_task:
        return get_task_logger(__name__)

    # Users shouldn't directly log requests, so return
    # the stderr logger
    return logging.getLogger("stderr")


def _get_current_logger():
    return __get_current_logger()


# pylint: disable=unnecessary-lambda
current_logger = LocalProxy(lambda: _get_current_logger())
