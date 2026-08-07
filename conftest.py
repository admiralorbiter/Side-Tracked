"""Root Pytest Configuration & Environment Patching."""

import os
import sys

os.environ["PYTEST_ADDOPTS"] = "-p no:qt " + os.environ.get("PYTEST_ADDOPTS", "")


def _patch_shiboken():
    for importer in list(sys.meta_path):
        cls = type(importer)
        if "SixMetaPathImporter" in cls.__name__:
            cls._path = None
            try:
                importer._path = None
            except Exception:
                pass


_patch_shiboken()


def pytest_configure(config):
    _patch_shiboken()


import matplotlib

matplotlib.use("Agg")

try:
    pass
except Exception:
    pass
