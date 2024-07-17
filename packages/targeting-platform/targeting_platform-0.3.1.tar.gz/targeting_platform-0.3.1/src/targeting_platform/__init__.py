""".. include:: ../../README.md
    :start-line: 1
    :end-before: How to use

## Targeting Platform Classes

There is one base class `Platform` with all availiable interfaces.

Then you have implementation for each platform we support. Not all interfaces will be implemented in specific classes as not supported,
e.g. The Trade Dest does not have clone and delete for Ad Groups.
"""

__author__ = """Siarhei Ivanou"""
__email__ = "sinusu@gmail.com"
__version__ = "0.1.0"
__docformat__ = "google"

from .platform import Platform
from .platform_ttd import PlatformTTD
from .platform_meta import PlatformMeta
from .platform_dv360 import PlatformDV360

__all__ = ["Platform", "PlatformTTD", "PlatformMeta", "PlatformDV360"]
