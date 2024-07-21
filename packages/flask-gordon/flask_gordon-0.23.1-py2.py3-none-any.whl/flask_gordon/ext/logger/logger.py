"""
Description
===========

Initialize loggers for Celery workers.

Usage
=====

Initializing a Celery application
---------------------------------

Sample :file:`<PACKAGE_NAME>/__init__.py` file:

.. code-block:: python

  #!/usr/bin/env python3

  from flask import Flask
  from flask_gordon.ext import CeleryExt

  flask_app = Flask(__name__)
  celery_app = CeleryExt().init_flask_app(flask_app)
  celery_app = LoggerExt().init_app(celery_app)

Classes
=======

.. autoclass:: LoggerExt
   :members: __init__, init_app

"""

import logging

from .. import _functions as functions


class LoggerExt:
    def __init__(self, app=None):
        """
        Parameters
        ----------
        app:

            A Flask or Celery application.
        """
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Refer to :meth:`flask_gordon.ext.logger.logger.LoggerExt`

        Returns
        -------
        app:

            A Flask or Celery application.
        """
        # Is this a flask or celery application?
        return functions.app_junction(
            app,
            lambda: self._init_flask_app(app),
            lambda: self._init_celery_app(app),
        )

    def _init_flask_app(self, app):
        return app

    def _init_celery_app(self, app):
        # Defaults:
        #   https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-worker_log_format
        #
        # We don't need to toy around with the loggers, so we can just change the settings
        app.conf.update(
            {
                "worker_log_format": "[%(asctime)s] [%(levelname)s] [%(processName)s] %(message)s",
                "worker_task_log_format": "[%(asctime)s] [%(levelname)s] [%(processName)s] [%(task_name)s] [%(task_id)s] %(message)s",
                "worker_redirect_stdouts_level": "DEBUG",
            },
        )

        # Print configuration file only in Celery worker application
        # pylint: disable=protected-access
        if functions.is_celery_worker_app() and getattr(app, "_cfgfileread"):
            cfg = app._cfgfileread
            if cfg:
                logging.getLogger("stderr").info(f"Read Celery configuration from file '{cfg}'")
        return app
