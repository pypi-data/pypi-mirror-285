import importlib

from .argparse import ArgParseExt
from .ctx import current_logger
from .logger import LoggerExt
from .testing import FlaskTestingExt

__all__ = [
    # Extensions
    "ArgParseExt",
    "FlaskTestingExt",
    "LoggerExt",
    # LocalProxies
    "current_logger",
]

if importlib.util.find_spec("celery") is not None:
    from .celery import CeleryExt
