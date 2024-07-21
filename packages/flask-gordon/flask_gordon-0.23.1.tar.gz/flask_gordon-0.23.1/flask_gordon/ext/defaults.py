"""
Defaults
--------

.. data:: SERVER_LISTEN
  :noindex:

  Configuration default listen address (``localhost``)

.. data:: SERVER_PORT
  :noindex:

  Configuration default listen port (``8080``)

.. data:: CFGFILE_SEARCH_PATHS
  :noindex:

  Configuration default search paths

  .. code-block:: python

    [
        ".<filename>.yml",
        "<filename>.yml",
        "$XDG_CONFIG_HOME/<filename>.yml",
        "$HOME/.<filename>.yml",
        "/etc/xdg/<filename>.yml",
        "/etc/<filename>.yml",
    ]

Default configuration
---------------------

.. code-block:: python

  {
      # The following can be set in the configuration file:
      "server": {
          "debug": False,
          "listen": SERVER_LISTEN,
          "port": SERVER_PORT,
          "ui": True,
          "workers": 0,
          "pidfile": None,
          "proxy": {
              "x_for": 0,
              "x_proto": 0,
              "x_host": 0,
              "x_port": 0,
              "x_prefix": 0,
          },
          "cachedir": None,
          "timeout": 120,
      },
      "celery": {
          "broker_url": "redis://localhost:6379/0",
          "result_backend": "redis://localhost:6379/0",
          "broker_connection_retry_on_startup": False,
      },
  }

"""

import os
import typing as t

from boltons.iterutils import flatten_iter, unique_iter
from xdg import XDG_CONFIG_DIRS

SERVER_LISTEN: str = "localhost"
SERVER_PORT: int = 8080

# fmt: off
CFGFILE_SEARCH_PATHS: t.List[str] = list(
    unique_iter(
        flatten_iter(
        [
            "./.{cfgfilename}",                # ./.<filename>.yml
            "./{cfgfilename}",                 # ./<filename>.yml
            "$XDG_CONFIG_HOME/{cfgfilename}",  # ~/.config/<filename>.yml
            "~/.{cfgfilename}",                # ~/.<filename>.yml
            [os.path.join(str(e), "{cfgfilename}") for e in XDG_CONFIG_DIRS],
            "/etc/{cfgfilename}",              # /etc/<filename>.yml
        ],
        ),
    ),
)
# fmt: on


def make_config(defaults: t.Dict[str, t.Any] = None) -> t.Dict[str, t.Any]:
    """
    Convenience function that returns defaults for arguments,
    and for configuration file.

    Parameters
    ----------
    defaults: dict
        a dictionary containing default values.

    Returns
    -------
    dict:
        a dictionary
    """
    defaults = defaults or {}
    defaults["server"] = defaults.get("server") or {}

    # cf. src/middleware/__init__.py
    return {
        "server": {
            "debug": defaults["server"].get("debug", False),
            "listen": defaults["server"].get("listen", SERVER_LISTEN),
            "port": defaults["server"].get("port", SERVER_PORT),
            "ui": defaults["server"].get("ui", True),
            "workers": defaults["server"].get("workers", 0),
            "pidfile": defaults["server"].get("pidfile", None),
            "proxy": {
                "x_for": defaults["server"].get("proxy", {}).get("x_for", 0),
                "x_proto": defaults["server"].get("proxy", {}).get("x_proto", 0),
                "x_host": defaults["server"].get("proxy", {}).get("x_host", 0),
                "x_port": defaults["server"].get("proxy", {}).get("x_port", 0),
                "x_prefix": defaults["server"].get("proxy", {}).get("x_prefix", 0),
            },
            "cachedir": None,
            "timeout": 120,
        },
        "celery": {
            "broker_url": "redis://localhost:6379/0",
            "result_backend": "redis://localhost:6379/0",
            "broker_connection_retry_on_startup": False,
        },
    }
