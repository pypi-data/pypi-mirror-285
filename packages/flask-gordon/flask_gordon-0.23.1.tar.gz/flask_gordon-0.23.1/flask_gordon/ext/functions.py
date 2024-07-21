import contextlib
import sys

__all__ = [
    "get_app_class",
    "is_celery_app",
    "is_celery_worker_app",
]


def get_app_class(app):
    # Is this a flask or celery application?
    with contextlib.suppress(AttributeError):
        _ = app.run
        return "flask"

    with contextlib.suppress(AttributeError):
        _ = app.control.inspect
        return "celery"

    return None


def is_celery_app():
    return "celery.bin.celery" in sys.modules


def is_celery_worker_app():
    if not is_celery_app():
        return False
    return "worker" in sys.argv[1:]
