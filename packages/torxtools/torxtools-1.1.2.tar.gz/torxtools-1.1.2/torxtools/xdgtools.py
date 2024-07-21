"""
Functions for working with xdg paths and environment.

The :func:`setenv` function sets all XDG single directory environment variables to their values. It is also called on module instantiation.
"""

import os

from torxtools.pathtools import expandpath

__all__ = [
    "setenv",
]

_defaults = {
    "XDG_CONFIG_DIR": "/etc/xdg",
    "XDG_DATA_DIR": "/usr/local/share:/usr/share",
    "XDG_CACHE_HOME": "$HOME/.cache",
    "XDG_CONFIG_HOME": "$HOME/.config",
    "XDG_DATA_HOME": "$HOME/.local/share",
    "XDG_RUNTIME_DIR": None,
}


def setenv() -> None:
    """
    XDG Base Directory Specification environment variables setter.

    Sets all XDG environment variables (:ev:`XDG_CACHE_HOME`,
    :ev:`XDG_CONFIG_HOME`, :ev:`XDG_DATA_HOME`, :ev:`XDG_CONFIG_DIRS`,
    :ev:`XDG_DATA_DIRS`, and :ev:`XDG_RUNTIME_DIR`) to their respective values
    according to current os.environ or their defaults.

    All paths will be expanded before being set.

    Example
    -------

    .. code-block:: python

        from torxtools import xdgtools, pathtools

        try:
            del os.environ["XDG_CONFIG_HOME"]
        except:
            pass
        # We changed the XDG environment:
        xdgtools.setenv()
        assert os.environ["XDG_CONFIG_HOME"] == pathtools.expandpath("$HOME/.config")

    See Also
    --------
    `XDG Base Directory Specification <https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html>`__
    """
    for k, v in _defaults.items():
        path = os.environ.get(k, v)
        if path:
            os.environ[k] = expandpath(path)
