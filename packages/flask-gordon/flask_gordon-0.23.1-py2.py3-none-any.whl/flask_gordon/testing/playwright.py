"""
Playwright
----------

This module provides conditional and helper fixtures for ``playwright``.

Fixtures require ``pytest-playwright`` to be loaded.

.. autofixture:: has_page_skip
.. autofixture:: page_else_skip
.. autofixture:: has_page_fail
.. autofixture:: page_else_fail

"""

from pytest import fail, fixture, skip


def has_launch_browser(launch_browser):
    browser = None
    try:
        browser = launch_browser()
        return True
    except Exception:
        return False
    finally:
        if browser:
            browser.close()


@fixture(name="_has_page_skip", scope="session")
def has_page_skip(launch_browser):
    """
    Skip (or fail) a test has this this fixture unless ``playwright`` browsers are installed.
    """
    if not has_launch_browser(launch_browser):
        skip("playwright browser not found")


@fixture(name="page_else_skip", scope="function")
def page_else_skip(_has_page_skip, page):
    """
    Skip (or fail) a test has this this fixture unless ``playwright`` browsers are installed.

    Returns
    -------

    A ``playwright`` ``page`` fixture.
    """
    yield page


@fixture(name="_has_page_fail", scope="session")
def has_page_fail(launch_browser):
    """
    Refer to :meth:`has_page_skip`
    """
    if not has_launch_browser(launch_browser):
        fail("playwright browser not found")


@fixture(name="page_else_fail", scope="function")
def page_else_fail(_has_page_fail, page):
    """
    Refer to :meth:`page_else_fail`
    """
    yield page
