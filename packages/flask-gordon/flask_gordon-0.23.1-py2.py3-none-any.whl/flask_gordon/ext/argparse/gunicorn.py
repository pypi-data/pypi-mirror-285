r"""
Description
-----------

Options
-------

.. program:: flasket

.. option:: -l HOST, --listen HOST

   The ip to listen on (default: localhost)

.. option:: -p PORT, --port PORT

   The port to listen on (default: 8080)

.. option:: -c CFGFILE, --cfgfile CFGFILE

   Use CFGFILE as configuration file, otherwise first file found in
   search path is used. (default search path: (...))

.. option:: --ui, --no-ui

   Enable the OpenAPI UI. Disable with :option:`--no-ui`. (default: enabled)

.. option::  -w WORKERS, --workers WORKERS

   Number of thread workers. (default: 0. If 0, cpu to use is (cpu_count * 2) with a maximum
   of 8; if negative, cpu to use is (cpu_count * 2) with no maximum.)

.. option::  --pidfile FILE

   A filename to use for the PID file. (default: none)

Usage
-----

.. program:: flasket

.. code-block:: python

  #!/usr/bin/env python3

  from flasket import make_flasket_cli

  if __name__ == "__main__":
      flasket = make_flasket_cli(__file__, "gunicorn", cfgname="example.yml")
      flasket.run()

"""

import argparse
import typing as t


class GunicornHelper:
    @staticmethod
    def force_cfg(cfg: t.Dict["str", t.Any]) -> None:
        cfg["server"]["production"] = True
        cfg["server"]["debug"] = False
        return cfg

    @staticmethod
    def add_arguments(defaults: t.Dict["str", t.Any], parser: argparse.ArgumentParser) -> None:
        """
        Adds Gunicorn middleware specific command line arguments :option:`--workers`, :option:`--pidfile`
        to the ArgumentParser.

        Parameters
        ----------
        defaults:

            a dictionnary containing default values

        parser: argparse.ArgumentParser

            a parser on which `add_argument` will be called
        """
        workers = defaults["workers"]
        pidfile = defaults["pidfile"]
        if not pidfile:
            pidfile = "none"

        # fmt: off
        parser.add_argument(
            "-w", "--workers", metavar="WORKERS", type=int,
            help=f"Number of thread workers. (default: {workers}. If 0, cpu to use is (cpu_count * 2) with a maximum of 8; if negative, cpu to use is (cpu_count * 2) with 8 maximum.)",
        )
        parser.add_argument(
            "--pidfile", metavar="FILE", type=str,
            help=f"A filename to use for the PID file. (default: {pidfile})",
        )
        # fmt: on
