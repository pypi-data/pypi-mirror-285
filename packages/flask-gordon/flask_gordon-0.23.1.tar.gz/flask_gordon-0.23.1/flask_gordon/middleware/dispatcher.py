"""
Description
===========

This middleware creates a single WSGI application that dispatches to
multiple other WSGI applications mounted at different URL paths.

A common example is writing a Single Page Application, where you have a
backend API and a frontend written in JavaScript that does the routing
in the browser rather than requesting different pages from the server.
The frontend is a single HTML and JS file that should be served for any
path besides :url:`/api`.

This example dispatches to an API app under :url:`/api`, an admin app
under :url:`/admin`, and an app that serves frontend files for all other
requests::

    app = Dispatcher(serve_frontend, {
        '/api': api_app,
        '/admin': admin_app,
    })

In production, you might instead handle this at the HTTP server level,
serving files or proxying to application servers based on location. The
API and admin apps would each be deployed with a separate WSGI server,
and the static files would be served directly by the HTTP server.

Unlike the :class:`werkzeug.middleware.Dispatcher` a call to
:url:`/api` will not be routed to the app handling the prefix :url:`/api`.
A call to :url:`/api/` will though.


Usage
=====

.. code-block:: python

    from flask import Flask
    from flask_gordon.middleware import Dispatcher

    paths = {
        "/api": Flask("api", static_folder="api"),
        "/app": Flask("app", static_folder="app"),
    }

    flask_app = Flask(__name__)
    flask_app.wsgi_app = Dispatcher(flask_app.wsgi_app, paths)


Classes
=======

.. autoclass:: Dispatcher

"""

import typing as t

if t.TYPE_CHECKING:
    from _typeshed.wsgi import StartResponse, WSGIApplication, WSGIEnvironment

__all__: t.List[str] = []


class Dispatcher:
    """
    Combine multiple applications as a single WSGI application.
    Requests are dispatched to an application based on the path it is
    mounted under.

    Parameters
    ----------

    app: WSGIApplication

        The WSGI application to dispatch to if the request
        doesn't match a mounted path.

    mounts: t.Dict[str, "WSGIApplication"]

        Maps path prefixes to applications for dispatching.

    """

    def __init__(
        self,
        app: "WSGIApplication",
        mounts: t.Optional[t.Dict[str, "WSGIApplication"]] = None,
    ) -> None:
        self.app = app
        self.mounts = mounts or {}

    def __call__(self, environ: "WSGIEnvironment", start_response: "StartResponse") -> t.Iterable[bytes]:
        script = environ.get("PATH_INFO", "")

        while "/" in script:
            script, _ = script.rsplit("/", 1)
            path = script + "/"

            for mount, app in self.mounts.items():
                prefix = "/" if mount == "/" else mount + "/"
                if prefix == path:
                    return app(environ, start_response)

        return self.app(environ, start_response)
