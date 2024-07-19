import importlib.util

from . import lendl_method

VERSION = "2.0.2"

REPORT_INSTALLED = bool(importlib.util.find_spec("pyroll.report"))

if REPORT_INSTALLED:
    from pyroll.report import plugin_manager
    from . import report
    plugin_manager.register(report)

