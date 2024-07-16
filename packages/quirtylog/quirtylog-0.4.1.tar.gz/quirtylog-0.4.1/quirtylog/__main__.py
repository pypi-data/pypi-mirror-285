"""
-----------
__main__.py
-----------

quirtylog main entry point

Example:

    .. code-block:: bash

    python -m quirtylog script.py

"""

import sys
import importlib
import importlib.util

from .core import configure_logger


def load_module(source: str):
    """
    Read file source and loads it as a module

    :param source: file to load
    :return: loaded module
    """

    spec = importlib.util.spec_from_file_location(source, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[source] = module
    spec.loader.exec_module(module)

    return module


def wrapper(argv: list[str] | None = None):
    """Execute the script using default log"""
    if argv is None:
        argv = sys.argv[1:]

    configure_logger()
    script_name = argv[0]
    load_module(script_name)


sys.exit(wrapper())
