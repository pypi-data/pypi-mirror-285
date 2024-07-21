"""
Description
-----------

Options
-------

.. program:: flasket-dev

.. option:: -l HOST, --listen HOST

   The ip to listen on (default: localhost)

.. option:: -p PORT, --port PORT

   The port to listen on (default: 8080)

.. option:: -c CFGFILE, --cfgfile CFGFILE

   Use CFGFILE as configuration file, otherwise first file found in
   search path is used. (default search path: (...))

.. option:: --ui, --no-ui

   Enable the OpenAPI UI. Disable with :option:`--no-ui`. (default: enabled)

.. option:: --debug, --no-debug

  Enable debug mode. Disable with :option:`--no-debug`. (default: disabled)

Usage
-----

.. program:: flasket-dev

.. code-block:: python

  #!/usr/bin/env python3

  from flasket.cli import make_flasket

  if __name__ == "__main__":
      flasket = make_flasket_cli(__file__, "flask", cfgname="example.yml")
      flasket.run()


"""

import argparse
import typing as t


class FlaskHelper:
    @staticmethod
    def force_cfg(cfg: t.Dict["str", t.Any]) -> None:
        # debug is set via flag
        cfg["server"]["production"] = False
        return cfg

    @staticmethod
    def add_arguments(defaults: t.Dict["str", t.Any], parser: argparse.ArgumentParser) -> None:
        """
        Adds Flask middleware specific command line arguments :option:`--debug`, :option:`--no-debug`
        to the ArgumentParser.

        Parameters
        ----------
        defaults:

            a dictionnary containing default values

        parser: argparse.ArgumentParser

            a parser on which `add_argument` will be called
        """
        debug = {True: "enabled", False: "disabled"}[defaults["debug"]]

        # fmt: off
        parser.add_argument(
            "--debug", action="store_true", default=None,
            help=f"Enable debug mode. Disable with --no-debug. (default: {debug})",
        )
        parser.add_argument(
            "--no-debug", action="store_false", default=None, dest="debug",
            help=argparse.SUPPRESS,
        )
        # fmt: on
