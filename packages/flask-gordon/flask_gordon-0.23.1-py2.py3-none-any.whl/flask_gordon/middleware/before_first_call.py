"""
Description
===========

This middleware will call a function on, and only on, the first request.
Multiple functions can be registered and will be called one-by-one.

Registering functions after first call will have no effect.

This middleware is best added last to the middlewares that will be called
by your application since a middleware that does not dispatch to another
middleware will inhibit this middleware.


Usage
=====

.. code-block:: python

    from flask import Flask
    from flask_gordon.middleware import BeforeFirstCall


    def once_before_first_call():
        print("Hello World")


    flask_app = Flask(__name__)
    flask_app.wsgi_app = BeforeFirstCall(flask_app.wsgi_app, once_before_first_call)
    flask_app.run()


Classes
=======

.. autoclass:: BeforeFirstCall
  :members: before_first_call

"""

import typing as t

if t.TYPE_CHECKING:
    from _typeshed.wsgi import StartResponse, WSGIApplication, WSGIEnvironment

__all__: t.List[str] = []


class BeforeFirstCall:
    """
    Register function :param:`fn` to be called on first WSGI application call.

    Multiple functions can be registered with the :meth:`before_first_call`
    function.

    Parameters
    ----------

    app: WSGIApplication

        The WSGI application to dispatch to after the processing.

    fn: t.Callable

        Function to be called on the first request.
    """

    def __init__(self, app: "WSGIApplication", fn: t.Callable = None) -> None:  # type: ignore[type-arg]
        self.app = app
        self.__functions = set()
        self.__before_first_call = False
        if fn:
            self.__functions.add(fn)

    def __call__(self, environ: "WSGIEnvironment", start_response: "StartResponse") -> t.Iterable[bytes]:
        if not self.__before_first_call:
            for function in self.__functions:
                function()
            self.__before_first_call = True
        return self.app(environ, start_response)

    def before_first_call(self, fn: t.Callable) -> t.Callable:  # type: ignore[type-arg]
        """
        Register a function to be called once on first call

        Parameters
        ----------

        fn: t.Callable

            Function to be called on the first request.
        """

        self.__functions.add(fn)
        return fn
