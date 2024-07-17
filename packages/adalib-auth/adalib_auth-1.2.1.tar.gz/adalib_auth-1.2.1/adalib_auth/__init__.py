"""The adalib-auth package handles the authentication workflow with the AdaLab platform.
"""

import importlib.metadata

from . import config, jupyterhub, keycloak

_DISTRIBUTION_METADATA = importlib.metadata.metadata("adalib-auth")
__project__ = _DISTRIBUTION_METADATA["name"]
__version__ = _DISTRIBUTION_METADATA["version"]
__description__ = _DISTRIBUTION_METADATA["description"]

__all__ = ["config", "jupyterhub", "keycloak"]
