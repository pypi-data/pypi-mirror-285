import typing as t
from copy import deepcopy

from boltons.iterutils import remap
from torxtools import xdgtools
from torxtools.cfgtools import which
from torxtools.pathtools import expandpath
from yaml import safe_load

from ..defaults import CFGFILE_SEARCH_PATHS, make_config


def _strip_none(_p: str, k: str, v: t.Any) -> bool:
    return k is not None and v is not None


def _deepmerge(src: t.Dict[str, t.Any], dst: t.Dict[str, t.Any], path: t.List[str] = None) -> t.Dict[str, t.Any]:
    """
    Take every key, value from src and merge it recursively into dst.
    Adapted from https://stackoverflow.com/questions/7204805

    Parameters
    ----------
    dst: dict
        Destination dictionary

    src: dict
        Source dictionary

    path:
        Used internally

    Returns
    -------
    dict:
        Merged dictionary
    """
    if path is None:
        path = []

    for key in src:
        if key not in dst:
            dst[key] = src[key]
        elif isinstance(dst[key], dict) and isinstance(src[key], dict):
            _deepmerge(src[key], dst[key], path + [str(key)])
        elif dst[key] == src[key]:
            pass  # same leaf value
        else:
            dst[key] = src[key]
    return dst


def deepmerge(dst: t.Dict[str, t.Any], src: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    """
    Take every key, value from src and merge it recursivly into dst.
    None values are stripped from src before merging.

    Adapted from https://stackoverflow.com/questions/7204805

    Parameters
    ----------
    dst: dict
        destination dictionary

    src: dict
        source dictionary

    Returns
    -------
    dict:
        merged dictionary
    """
    # pylint: disable=unnecessary-lambda-assignment
    src = remap(src, visit=_strip_none)

    return _deepmerge(src, deepcopy(dst))


def _read(cfgfile: str) -> t.Dict[str, t.Any]:
    """
    Convenience function in order to be mocked.

    Parameters
    ----------
    cfgfile: str

        a single path representing a yaml file.

    Returns
    -------
    dict:

        a dictionary
    """
    with open(cfgfile, encoding="UTF-8") as fd:
        data = safe_load(fd)
    return data or {}


def prepare_configuration(cfgfilename, cfgfilepaths, default_cfg):
    # Sets environment variables for XDG paths
    xdgtools.setenv()

    # Prepare search path for configuration file. Disable it if we're looking
    # for a impossible (None) file name
    cfgfilename, cfgfilepaths = _prepare_search_paths(cfgfilename, cfgfilepaths)

    # Create a default configuration from what was passed
    # and what we set. Other values are filtered
    defaults = make_config(default_cfg)
    return cfgfilename, cfgfilepaths, defaults


def _prepare_search_paths(cfgfilename, cfgfilepaths):
    # Prepare search path for configuration file. Disable it if we're looking
    # for a impossible (None) file name
    if not cfgfilename:
        cfgfilename = "settings.yml"
    if cfgfilepaths is None:
        cfgfilepaths = CFGFILE_SEARCH_PATHS
    cfgfilepaths = [e.format(cfgfilename=cfgfilename) for e in cfgfilepaths]
    return cfgfilename, cfgfilepaths


def read_configuration(cfgfile, cfgfilename, cfgfilepaths):
    # Search for the configuration file
    if cfgfile is None and cfgfilepaths:
        # Search for cfgfile
        cfgfilepaths = [e.format(cfgfilename=cfgfilename) for e in cfgfilepaths]
        cfgfile = which(cfgfile, expandpath(cfgfilepaths))

    return cfgfile, _read(cfgfile or "/dev/null") or {}
