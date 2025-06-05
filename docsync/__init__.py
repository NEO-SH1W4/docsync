"""Compatibility wrapper that exposes ``src.docsync`` as ``docsync``."""

from importlib import import_module
import sys

_real_pkg = import_module("src.docsync")
globals().update({k: getattr(_real_pkg, k) for k in getattr(_real_pkg, "__all__", [])})
sys.modules[__name__].__dict__.update(_real_pkg.__dict__)
