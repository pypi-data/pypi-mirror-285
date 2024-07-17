"""Module to work with JupyterHub on the AdaLab platform.
"""

from .jupyterhub import get_token_from_auth_state, is_this_jupyterhub

__all__ = ["get_token_from_auth_state", "is_this_jupyterhub"]

__title__ = "adalib-auth JupyterHub"
