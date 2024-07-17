"""The Config sub-package sets up the environment for adalib. It also fetches all the
configuration values needed in the library.

The first client call to import this module will initialize it, after which it
will be a singleton instantiation for the duration of the process.
"""

from .config import Configuration, get_config

__all__ = ["Configuration", "get_config"]

__title__ = "adalib-auth Config"
