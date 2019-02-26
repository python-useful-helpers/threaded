"""Test rules."""
# Standard Library
import sys


def pytest_ignore_collect(path, config):
    """Ignore sources for python 3.4."""
    return sys.version_info < (3, 5)
