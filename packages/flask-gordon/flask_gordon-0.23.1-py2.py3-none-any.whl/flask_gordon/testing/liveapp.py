"""
LiveApp
-------

This module provides a ``liveapp_cls`` pytest fixture that enables the creation of a live flask/gunicorn process.

When used with ``playwright`` ``page`` fixture, or :meth:`page_else_skip` fixtures, this enables one to test the web UI.


Example
-------

In :file:`tests/conftest/py`

.. code-block:: python

  @fixture(name="liveapp", scope="function")
  def liveapp_fixture(liveapp_cls):
      # Sample configuration
      configuration = {"server": {"database": "sqlite://""}}

      # Assumes that `python -m{{mypackage}}` runs the application
      liveapp = liveapp_cls.configure(mod="mypackage", configuration=configuration)
      with liveapp.run():
          yield liveapp

For your test:

.. code-block:: python

    @mark.liveapp
    def test_app_metrics(liveapp, page_else_skip):
        page = page_else_skip
        page.goto(f"{liveapp.base_url}/app/metrics")

Your :file:`pyproject.toml` should contain the marker:

.. code-block:: ini

  [tool.pytest.ini_options]
  markers = [
    "liveapp: Run tests that require a live application (unselect with '-m not \"liveapp\"')",
  ]


.. autoclass:: LiveApp
   :members: base_url, port, cfgfile, cmdline, parseline, urlpath, configure, configure_configuration, configure_cmdline, run
   :special-members:

.. autofixture:: liveapp_cls

"""

import contextlib
import logging
import signal
import subprocess
import tempfile
import time

import requests
import yaml
from pytest import fixture
from requests.exceptions import ReadTimeout

logger = logging.getLogger(__name__)


class LiveApp:
    """
    This class contains the live process.
    TODO
    """

    def __init__(self, tmppath):
        self._urlpath = "/api/metrics"
        self._cfgfile = None
        self._cmdline = None
        self._port = None
        self._process = None
        self._tmppath = tmppath
        self._parseline = lambda x: int(x.split(":", maxsplit=5)[5].split(maxsplit=1)[0])

    @property
    def base_url(self):
        """
        Return the base url for making requests
        """
        return f"http://localhost:{self.port}"

    @property
    def port(self):
        """
        Return the current port that the live application uses. Chosen at random on ``run()``
        """
        return self._port

    @property
    def cfgfile(self):
        """
        Get or set the configuration file to use
        """
        return self._cfgfile

    @cfgfile.setter
    def cfgfile(self, rhs):
        self._cfgfile = rhs
        return self._cfgfile

    @property
    def cmdline(self):
        """
        Get or set the command line to use. If unset, it will be calculated.

        Defaults to `python3 -m{mod} -c{cfgfile} -llocalhost -p0 -w1` where ``mod`` is the value
        passed to :meth:`configure` and  ``cfgfile`` the configuration file if it was created.
        """
        return self._cmdline

    @cmdline.setter
    def cmdline(self, rhs):
        self._cmdline = rhs
        return self._cmdline

    @property
    def parseline(self):
        """
        Get or set the function that parses and returns the port used by the application.

        The function takes a string, and shoud return 0 or None if no port was found, or the port otherwise.
        """
        return self._parseline

    @parseline.setter
    def parseline(self, rhs):
        self._parseline = rhs
        return self._parseline

    @property
    def urlpath(self):
        """
        Get or set the path of the URL to test to detect if app is up.

        Defaults to ``/api/metrics``

        URL must return a 200 HTTP code.
        """
        return self._urlpath

    @urlpath.setter
    def urlpath(self, rhs):
        self._urlpath = rhs
        return self._urlpath

    def configure(self, /, mod=None, configuration=None, urlpath="/api/metrics"):
        """
        Configure the configuration file, command line and urlpath.

        Params
        ------

        mod: str

            Python module that will called as ``python3 -m{{mod}}``

        configuration: dict

            Dictionnary will be written out as a YAML file in the pytest temporary folder.

        urlpath: str

            Refer to :meth:`urlpath`

        """
        self.configure_configuration(configuration)
        self.configure_cmdline(mod)
        self._urlpath = urlpath
        return self

    def configure_configuration(self, configuration):
        """
        Refer to :meth:`configure`
        """
        data = configuration
        if data is None:
            data = {}

        tmppath = self._tmppath.getbasetemp()
        # pylint: disable=consider-using-with
        cfgfile = tempfile.NamedTemporaryFile(dir=tmppath, delete=False, prefix="cfg-", suffix=".yml")
        with open(cfgfile.name, mode="w", encoding="UTF-8") as fd:
            yaml.dump(data, fd)
        self._cfgfile = cfgfile.name
        return self._cfgfile

    def configure_cmdline(self, mod):
        """
        Refer to :meth:`configure`
        """
        if mod is None:
            self._cmdline = None
            return None

        cmdline = f"python3 -m{mod} -llocalhost -p0 -w1"
        if self._cfgfile:
            cmdline += f" -c{self._cfgfile}"
        self._cmdline = cmdline
        return self._cmdline

    @contextlib.contextmanager
    def run(self, cmdline=None, timeout=3600):  # 1 hour timeout
        """
        Run the live process.

        Parameters
        ----------

        timeout: int

            Live process will timeout after this amount of time in seconds. Default and max is 1 hour

        Example
        -------

        .. code-block:: python

          import requests

          @fixture(name="liveapp", scope="function")
          def liveapp_fixture(liveapp_cls, here, sqlite, page, schema):
              liveapp = liveapp_cls.configure(here, database=sqlite, schema=schema, page=page)
              with liveapp.run():
                  yield liveapp

          def test_liveapp(liveapp):
              with liveapp.run(timeout=10):
                  rv = requests.get(url=f"{liveapp.base_url}/api/metrics", timeout=3)
                  rv.raise_for_status()

        """
        if cmdline is None:
            cmdline = self._cmdline

        if cmdline is None:
            raise AssertionError("No command line configured or passed to `run()`")

        if timeout is not None:
            timeout = min(timeout, 3600)  # an hour maxium
            cmdline = f"timeout {timeout}s {self._cmdline}"

        logger.warning(f"Starting process '{self._cmdline}'...")
        try:
            self._process = subprocess.Popen(cmdline.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self._wait_for_port()
            self._wait_for_metrics()
            yield self
            self._wait_for_shutdown()

        finally:
            # Kill the process with SIGTERM if it's still alive
            if self._process:
                self._process.terminate()
                self._process.wait()

        # Reset
        self._port = None
        self._process = None

    def _wait_for_port(self):
        def _find_port(line):
            if "Listening at:" not in line:
                return None
            # Line is "[2022-09-02 11:14:41,535] [INFO] Listening at: http://localhost:36089 (1676660)"
            return self._parseline(line)

        self._port = None
        port = None
        while self._process.poll() is None and port in [None, 0]:
            line = str(self._process.stderr.readline().decode("UTF-8"))
            if not line:
                time.sleep(0.2)
                continue
            port = _find_port(line)

        if port is None:
            raise AssertionError("liveapp process suddenly quit before starting server.")

        logger.info(f"Found port {port}")
        self._port = port

    def _wait_for_metrics(self):
        while self._process.poll() is None:
            try:
                rv = requests.get(url=f"{self.base_url}{self._urlpath}", timeout=3)
                if rv.status_code == 200:
                    logging.getLogger().info("Server is live.")
                    return
            except (ConnectionError, ReadTimeout):
                pass
            time.sleep(0.2)

    def _wait_for_shutdown(self):
        # Kill the process and wait for a proper shutdown if possible
        logger.info("Shutting down...")
        self._process.send_signal(signal.SIGINT)
        index = 0
        while self._process.poll() is None and index < 10:
            time.sleep(0.2)
            index += 1


@fixture(name="liveapp_cls", scope="function")
def liveapp_cls(tmp_path_factory):
    """
    Fixture that returns a ``LiveApp`` configurable class.
    """
    yield LiveApp(tmp_path_factory)
