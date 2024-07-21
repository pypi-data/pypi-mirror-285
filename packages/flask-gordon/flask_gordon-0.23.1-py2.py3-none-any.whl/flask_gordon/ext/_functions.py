from .functions import *

__all__ = [
    "get_app_class",
    "is_celery_app",
    "is_celery_worker_app",
]


def app_junction(app, flask, celery):
    app_class = get_app_class(app)
    if app_class == "flask":
        return flask()
    if app_class == "celery":
        return celery()
    raise NotImplementedError("Could not determine if app is Flask or Celery")
