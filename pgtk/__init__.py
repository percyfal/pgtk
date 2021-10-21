"""Top-level package for pgtk."""

__author__ = """Per Unneberg"""
__email__ = "per.unneberg@scilifelab.se"


__version__ = "undefined"
try:
    from . import _version

    __version__ = _version.version
except ImportError:
    pass
