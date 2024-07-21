"""
Description
===========

WARNING: Requires a re-write

This extension is best used only when testing the ``Flask`` application, and
can be initialied only in a ``pytest.fixture`` for example.

It modifies the test client to make it a :class:`FlaskTestClient`. The latter
will have direct access to session variables via :class:`FlaskTestSession` and
to a request response validation class via :class:`FlaskTestResponse`


Classes
=======

.. autoclass:: FlaskTestingExt
  :members:

.. autoclass:: FlaskTestClient
  :members:

.. autoclass:: FlaskTestResponse
  :members:

.. autoclass:: FlaskTestSession
  :members:

"""

import typing as t
from collections.abc import MutableMapping

from flask import Response
from flask.testing import FlaskClient

if t.TYPE_CHECKING:
    from _typeshed.wsgi import WSGIApplication


# TODO: requires a re-write
#
class FlaskTestSession(MutableMapping):
    """
    Lorem ipsum
    """

    # https://flask.palletsprojects.com/en/2.2.x/api/#flask.sessions.SessionInterface
    def __init__(self, client):
        """
        Lorem ipsum
        """
        self._client = client

    def _call(self, fn: t.Callable):
        with self._client.session_transaction() as session:
            return fn(session)

    def set(self, key, value) -> None:
        """
        Lorem ipsum
        """
        with self._client.session_transaction() as session:
            session[key] = value

    def get(self, key, default=None):
        """
        Lorem ipsum
        """
        return self._call(lambda s: s.get(key, default))

    def items(self):
        """
        Lorem ipsum
        """
        return self._call(lambda s: dict(s.items()))

    def clear(self) -> None:
        """
        Lorem ipsum
        """
        return self._call(lambda s: s.clear())

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __getitem__(self, key):
        return self._call(lambda s: s[key])

    def __delitem__(self, key):
        with self._client.session_transaction() as session:
            del session[key]

    def __str__(self):
        return self._call(lambda s: s.__str__())

    def __repr__(self):
        return self._call(lambda s: s.__repr__())

    def __iter__(self):
        return iter(self.items())

    def __len__(self):
        # pylint: disable=unnecessary-lambda
        return self._call(lambda s: len(s))

    def __contains__(self, key):
        return self._call(lambda s: key in s)


class FlaskTestResponse(Response):
    """
    Lorem Ipsum
    """

    # https://flask.palletsprojects.com/en/2.2.x/api/#flask.Response
    def expect(self, status_code=200, *, content_type=None):
        """
        Lorem Ipsum
        """
        if status_code is not None and not isinstance(status_code, int):
            assert False, f"Status code '{status_code}' must be None, or an integer"

        # content_type:
        #   None  = guess, and check the guess against what we recieved,
        #   *     = accept anything, do not guess
        #   "xzz" = exact match
        #
        # Verify status code
        if status_code:
            message = f"Expected client to return HTTP code {status_code}, received {self.status_code} instead"
            assert status_code == self.status_code, message

        # If 'X-Content-Type-Options' is set to nosniff, then content-type should be set
        # in the response, and unit test should check it.
        # TODO: assert the self.content_type is set
        if self.headers.get("X-Content-Type-Options") == "nosniff":
            pass

        # Get the real data
        data = self.data
        if self.is_json:
            # This is a json payload, expected content-type should be set to json
            # FIXME: if data is b'' then it can actually be text/plain, etc...
            data = self.json if data else {}
            if not content_type:
                content_type = "application/json"

        if content_type == "*":
            pass
        elif content_type:
            # Alter the content type for some types
            if content_type == "application/json" and self.status_code >= 400:
                content_type = "application/problem+json"

            # Verify content_type
            content = self.content_type.split(";")[0]
            message = f"Expecting '{content_type}' as content-type but got '{content}'"
            assert content_type == content, message

        if content_type in ["application/json", "application/problem+json"]:
            assert self.is_json, "Expecting data to be json, but it was not"

        return self


class FlaskTestClient(FlaskClient):
    """
    A test client class that inherits from `Flask`'s test client and also
    from ``Werkzeug``'s test client.

    See Also
    --------

    `FlaskClient <https://flask.palletsprojects.com/en/latest/api/#flask.Test.FlaskClient>`_

    """

    # https://flask.palletsprojects.com/en/latest/api/#flask.Test.FlaskClient
    #
    # Inherits from Flask's FlaskClient:
    #   .venv/lib/python3.9/site-packages/flask/testing.py
    # And from Werkzeug's Client:
    #   .venv/lib/python3.9/site-packages/werkzeug/test.py
    #
    def __init__(self, *args, **kwargs):
        """
        Lorem Ipsum
        """
        super().__init__(*args, **kwargs)
        self._default_headers = {}

    # pylint: disable=arguments-differ
    def get(self, url: str, **kwargs) -> FlaskTestResponse:
        """
        Call :meth:`request` with ``method`` set to ``GET``.
        """
        return self.request(url, method="GET", **kwargs)

    # pylint: disable=arguments-differ
    def post(self, url: str, **kwargs) -> FlaskTestResponse:
        """
        Call :meth:`request` with ``method`` set to ``POST``.
        """
        return self.request(url, method="POST", **kwargs)

    # TODO: add all methods from
    # .venv/lib64/./python3.9/./site-packages/werkzeug/test.py
    def request(self, url: str, method="GET", session=None, headers=None, **kwargs) -> FlaskTestResponse:
        """
        The test client makes requests to the application without running a live server.
        Flask-Gordon's client extends Flask's client which itself extends Werkzeug's client.

        follow_redirects:
        query_string
        headers
        data
        json
        """
        # https://flask.palletsprojects.com/en/2.2.x/Test/#sending-requests-with-the-test-client
        # https://werkzeug.palletsprojects.com/en/2.2.x/test/
        #
        # Create or edit the session
        for k, v in (session or {}).items():
            self.session.set(k, v)

        # Set the headers
        # py39: headers = self._default_headers | (headers or {})
        headers = {**self._default_headers, **(headers or {})}

        if method == "GET":
            return super().get(url, headers=headers, **kwargs)
        if method == "POST":
            return super().post(url, headers=headers, **kwargs)
        assert False, f"call method '{method}' not yet implemented"

    @property
    def session(self) -> FlaskTestSession:
        """
        Returns an instance of :class:`FlaskTestSession`
        """
        return FlaskTestSession(self)

    @property
    def default_headers(self):
        """
        Lorem Ipsum
        """
        return self._default_headers

    @default_headers.setter
    def default_headers(self, value):
        """
        Lorem Ipsum
        """
        self._default_headers = value


class FlaskTestingExt:
    """
    Extension that alters the ``Flask`` default response class and test client
    class.
    """

    def __init__(self, app: t.Optional["WSGIApplication"] = None):
        """
        Initialize ``app`` with extension: alter the default ``Flask``
        :meth:`response_class` and the :meth:`test_client_class`.

        Parameters
        ----------

        app: WSGIApplication

            The WSGI application to bind extension to.
        """
        if app is not None:
            self.init_app(app)

    def init_app(self, app: "WSGIApplication") -> "WSGIApplication":
        """
        Initialize ``app`` with extension: alter the default ``Flask``
        :meth:`response_class` and the :meth:`test_client_class`.

        Parameters
        ----------

        app: WSGIApplication

            The WSGI application to bind extension to.
        """
        app.response_class = FlaskTestResponse  # type: ignore[attr-defined]
        app.test_client_class = FlaskTestClient  # type: ignore[attr-defined]
        return app
