import os

import requests_oauthlib


def get_token_from_auth_state(
    username: str,
    jh_token: str,
    jh_api_url: str,
) -> dict:
    """Get a keycloak token from jupyter auth state.

    :return: Token to access jupyterhub.
    :rtype: dict
    """
    if jh_api_url.startswith("http://"):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    session = requests_oauthlib.OAuth2Session(token={"access_token": jh_token})
    response = session.get(f"{jh_api_url}/users/{username}")
    response.raise_for_status()
    user_info = response.json()
    auth_state = user_info["auth_state"]
    if not auth_state:
        raise ValueError("No auth state returned by JupyterHub API")
    return auth_state


def is_this_jupyterhub():
    """Checks whether this package is running in a JupyterHub environment.

    :return: `true` if called from a program in JupyterHub, `false` otherwise
    :rtype: bool
    """
    return "JUPYTERHUB_API_TOKEN" in os.environ
