"""
Description
===========

Parse command line arguments for Flask, or for Celery, and export
the contents of the yaml configuration file passed by `--cfgfile` (Flask)
or `--conf` (Celery) to the Flask app.

No settings are stored directly in Celery app.

When ArgParseExt is used on the Flask application, it will parse application
arguments and display the help if needed.

When used on the Celery application, it will parse application arguments
only to find the `--conf` flag, equivalent to the Flask `--cfgfile` argument.

ArgParseExt then searchs for the configuration file according to it's name,
"settings.yml" by default. The default search path will be shown in the `--help`
command printout.

`default_cfg` and `forced_cfg` are relative to the root contents of the settings
file. In other words, when passing Celery configuration, the celery settings must
be under the `celery` key.


.. docs/ext/argparse/flask.rst
.. include:: argparse/flask.rst

.. docs/ext/argparse/gunicorn.rst
.. include:: argparse/gunicorn.rst


Usage
=====

.. program:: flask-dev

Initializing applications
-------------------------

.. code-block:: python

  #!/usr/bin/env python3

  from flask import Flask
  from flask_gordon.ext import ArgParseExt
  from flask_gordon.ext import CeleryExt

  # Initialize Flask
  flask_app = Flask(__name__)

  # Initialize Celery
  celery = CeleryExt().init_app(flask_app)
  celery = ArgParseExt().init_app(
      forced_cfg={
          "imports": "<PACKAGE_NAME>.tasks",
      },
  )

  # If this is Flask:
  if __name__ == "__main__":
      global flask_app
      flask_app = ArgParseExt().init_flask_app(flask_app)
      # This line is reached if parsing of arguments did
      # not raise an error and was not `--help`.


Classes
=======

.. autoclass:: ArgParseExt
   :members: __init__, init_app

"""

import argparse
import os
import sys
import typing as t

from torxtools.argtools import is_not_dir

from .. import _functions as functions
from ._functions import deepmerge, prepare_configuration, read_configuration
from .flask import FlaskHelper
from .gunicorn import GunicornHelper


class ArgParseExt:
    def __init__(
        self,
        app=None,
        middleware: str = "gunicorn",
        argv: t.List[str] = None,
        cfgfilename=None,
        cfgfilepaths=None,
        default_cfg: t.Dict[str, t.Any] = None,
        forced_cfg: t.Dict[str, t.Any] = None,
        description="Flasket server",
        appname: str = None,
    ):
        """
        Parameters
        ----------
        app:

            A Flask or Celery application.

        middleware: str

            Middleware to use: 'gunicorn' for production, 'flask' for debug.
            Unused in the case of a Celery app.

        argv: list[str]

            Uses :code:`sys.argv[1:]` if None. Use :code:`[]` if you desire to deactive argument parsing.

        cfgfilename: str

            Configuration filename to use. Typically this is your packagename with a 'yml' extension.

        cfgfilepaths: str

            Paths to search for in order to find the configuration file. Every value of the list must contain the placeholder '{cfgfilename}' such as :code:`["/home/jdoe/{cfgfilename}"]`

        default_cfg: dict, default: :meth:`flasket.defaults.default_configuration`

            Dictionary containing the defaults for the command line arguments and configuration.
            Passed value will be merged with the default factory configuration, command line arguments
            and the configuration file that was read.

        forced_cfg: dict, default: {}

            Dictionary containing the forced settings.
            Passed value will be merged with the default factory configuration, command line arguments
            and the configuration file that was read, and then the forced_cfg will overwrite the values.
            Flask middleware forced configuration will overwrite the final configuration.

        description: str

            Text description to use in argparse.
            Unused in the case of a Celery app.

        appname: str

            Application name. Used to show application name in `--help` string.
            Defaults to sys.argv[0]
            Unused in the case of a Celery app.

        """
        if app is not None:
            self.init_app(
                app,
                middleware,
                argv=argv,
                cfgfilename=cfgfilename,
                cfgfilepaths=cfgfilepaths,
                default_cfg=default_cfg,
                forced_cfg=forced_cfg,
                description=description,
                appname=appname,
            )

    def init_app(
        self,
        app,
        middleware: str = "gunicorn",
        argv: t.List[str] = None,
        cfgfilename=None,
        cfgfilepaths=None,
        default_cfg: t.Dict[str, t.Any] = None,
        forced_cfg: t.Dict[str, t.Any] = None,
        description="Flask server",
        appname: str = None,
    ):
        """
        Refer to :meth:`flask_gordon.ext.argparse.argparse.ArgParseExt`

        Returns
        -------
        app:

            A Flask or Celery application.
        """
        return functions.app_junction(
            app,
            lambda: self._init_flask_app(
                app,
                middleware,
                argv=argv,
                cfgfilename=cfgfilename,
                cfgfilepaths=cfgfilepaths,
                default_cfg=default_cfg,
                forced_cfg=forced_cfg,
                description=description,
                appname=appname,
            ),
            lambda: self._init_celery_app(
                app,
                argv=argv,
                cfgfilename=cfgfilename,
                cfgfilepaths=cfgfilepaths,
                default_cfg=default_cfg,
                forced_cfg=forced_cfg,
            ),
        )

    def _init_flask_app(
        self,
        app: "Flask",
        middleware: str = "gunicorn",
        argv: t.List[str] = None,
        cfgfilename=None,
        cfgfilepaths=None,
        default_cfg: t.Dict[str, t.Any] = None,
        forced_cfg: t.Dict[str, t.Any] = None,
        description="Flask server",
        appname: str = None,
    ):
        flask_app = app

        # Verify middleware exists
        middleware = middleware.lower().strip()
        if middleware == "flask":
            helper = FlaskHelper()
        elif middleware == "gunicorn":
            helper = GunicornHelper()
        else:
            raise ValueError('middleware argument must be in ["flask", "gunicorn"]')

        # Parse arguments if they exist
        if argv is None:
            argv = sys.argv[1:]
            if appname is None:
                appname = os.path.basename(sys.argv[0])

        cfgfilename, cfgfilepaths, defaults = prepare_configuration(cfgfilename, cfgfilepaths, default_cfg)

        arguments = self._parse_arguments(
            argv=argv,
            cfgfilepaths=cfgfilepaths,
            helper=helper,
            defaults=defaults,
            description=description,
        )

        # Copy arguments over to an dict with server
        arguments = {k: v for k, v in arguments.items() if v is not None}
        cfgfile = arguments.pop("cfgfile", None)
        arguments = {"server": arguments}

        _, data = read_configuration(cfgfile, cfgfilename, cfgfilepaths)

        # Merge in the reverse order of priority
        cfg = defaults
        cfg = deepmerge(cfg, data)
        cfg = deepmerge(cfg, arguments)
        cfg = deepmerge(cfg, forced_cfg or {})
        cfg = helper.force_cfg(cfg)

        flask_app.config["SETTINGS"] = cfg
        return flask_app

    @staticmethod
    def _parse_arguments(*, argv, cfgfilepaths, helper, defaults, description):
        if not argv:
            return {}

        # argument_default=None does not set the default to None for boolean options,
        # so we'll specifically set default=None for those values
        #
        # Default values aren't actually added/set here, but in the FlasketSettings,
        # We only care about values that were specified.
        parser = argparse.ArgumentParser(
            description=description,
            argument_default=None,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        # Create helptext for UI option
        b_ui = {True: "enabled", False: "disabled"}[defaults["server"]["ui"]]
        if cfgfilepaths:
            # Keep on two lines, otherwise line continuation will make
            # an obsure argparse bug appear
            helpmsg_cfgfile = "Use CFGFILE as configuration file, "
            helpmsg_cfgfile += (
                f"otherwise first file found in search path is used. (default search path: {cfgfilepaths})"
            )
        else:
            helpmsg_cfgfile = "Use CFGFILE as configuration file."

        # fmt: off
        parser.add_argument(
            "-l", "--listen", metavar="HOST",
            help=f'The ip to listen on (default: {defaults["server"]["listen"]})',
        )
        parser.add_argument(
            "-p", "--port", metavar="PORT", type=int,
            help=f'The port to listen on (default: {defaults["server"]["port"]})',
        )
        parser.add_argument(
         "-c", "--cfgfile", metavar="CFGFILE",
           help=helpmsg_cfgfile,
           type=is_not_dir,
        )
        parser.add_argument(
            "--ui", action="store_true", default=None,
            help=f"Enable the OpenAPI UI. Disable with --no-ui. (default: {b_ui})",
        )
        parser.add_argument(
            "--no-ui", action="store_false", default=None, dest="ui",
            help=argparse.SUPPRESS,
        )
        # fmt: on
        helper.add_arguments(defaults["server"], parser)
        args = parser.parse_args(argv)
        return vars(args)

    def _init_celery_app(
        self,
        app: "Celery",
        argv: t.List[str] = None,
        cfgfilename=None,
        cfgfilepaths=None,
        default_cfg: t.Dict[str, t.Any] = None,
        forced_cfg: t.Dict[str, t.Any] = None,
    ):
        celery_app = app

        cfgfilename, cfgfilepaths, defaults = prepare_configuration(cfgfilename, cfgfilepaths, default_cfg)

        # Parse arguments if they exist
        if argv is None:
            argv = sys.argv[1:]

        cfgfile = None
        if "--config" in argv:
            idx = argv.index("--config")
            cfgfile = argv[idx + 1]

        cfgfileread, data = read_configuration(cfgfile, cfgfilename, cfgfilepaths)

        # Merge in the reverse order of priority
        cfg = defaults
        cfg = deepmerge(cfg, data)
        cfg = deepmerge(cfg, forced_cfg or {})

        if "celery" not in cfg:
            cfg["celery"] = {}

        # Copy the configuration to the app.
        # When celery starts, the ArgParseExt of app is not called since argv differs
        # between starting the Flask application and the Celery application
        #
        if getattr(celery_app, "app", None):
            celery_app.app().config["SETTINGS"] = cfg

        # Create a celery application
        celery_app.config_from_object(cfg["celery"])
        celery_app.set_default()

        # Save the configuration file used on the celery app, we'll print it if
        # the user also uses LoggerExt
        # pylint: disable=protected-access
        celery_app._cfgfileread = cfgfileread

        return celery_app
