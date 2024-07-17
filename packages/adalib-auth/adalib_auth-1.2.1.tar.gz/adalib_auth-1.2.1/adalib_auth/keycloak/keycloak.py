import logging
from typing import Union

import requests

import keycloak
import keycloak.exceptions

from . import config, jupyterhub


def app_authentication(audience: str, scope: str = "openid") -> dict:
    """
    Returns an audience authentication token from an exchange with an app token.

    :param audience: The audience for which the token is requested.
    :type audience: str
    :param scope: The scope of the token exchange, defaults to "openid"
    :type scope: str, optional
    :return: The audience token.
    :rtype: dict
    """
    adalib_config = config.get_config()
    app_token = {
        "access_token": adalib_config.CREDENTIALS["app_access_token"],
        "refresh_token": adalib_config.CREDENTIALS["app_refresh_token"],
    }

    # Exchange the app token for a Jupyterhub token
    jh_token = get_token_from_exchange(
        audience=adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
        token=app_token,
        client_id=adalib_config.CREDENTIALS["client_id"],
        client_secret=adalib_config.CREDENTIALS["client_secret"],
        scope=scope,
    )
    update_tokens_in_config(
        new_token=jh_token,
        client_id=adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
    )
    # Exchange the Jupyterhub token for an audience token
    audience_token = get_token_from_exchange(
        audience=audience,
        token=jh_token,
        client_id=adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
        client_secret=adalib_config.KEYCLOAK_CLIENTS["jupyterhub_secret"],
        scope=scope,
    )
    return audience_token


def authenticate_with_stored_credentials(
    audience_client_id: str,
) -> Union[dict, None]:
    """Attempt to get token for audience_client using stored credentials.

    :param audience_client_id: The client ID of the audience.
    :type audience_client_id: str
    :return: The token for the current user to authenticate to the audience_client with.
    :rtype: dict or None
    """

    adalib_config = config.get_config()
    token = {
        "access_token": adalib_config.CREDENTIALS["access_token"],
        "refresh_token": adalib_config.CREDENTIALS["refresh_token"],
    }
    if token["access_token"] is None and token["refresh_token"] is None:
        logging.debug("No stored credentials.")
        return None
    try:
        audience_token = get_token_from_exchange(
            audience=audience_client_id,
            token=token,
            client_id=adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
            client_secret=adalib_config.KEYCLOAK_CLIENTS["jupyterhub_secret"],
        )
    except AssertionError:
        logging.warning("Stored credentials are no longer valid.")
        return None
    return audience_token


def external_authentication(audience: str, scope: str = "openid") -> dict:
    """
    Returns an audience authentication token from an exchange with external user credentials.

    :param audience: The audience for which the token is requested.
    :type audience: str
    :param scope: The scope of the token exchange, defaults to "openid"
    :type scope: str, optional
    :return: The audience token.
    :rtype: dict
    """
    adalib_config = config.get_config()
    resp = requests.get(
        adalib_config.ADABOARD_API_URL + "/adalib/token",
        headers={
            "Authorization": f"Token {adalib_config.CREDENTIALS['token']}"
        },
    )
    if resp.status_code != 200:
        raise AssertionError(
            "Failed to authenticate with external credentials."
        )

    jh_token = resp.json()["access_token"]
    client = get_client(
        client_id=adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
        client_secret=adalib_config.KEYCLOAK_CLIENTS["jupyterhub_secret"],
    )
    new_token = client.exchange_token(
        token=jh_token,
        audience=adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
    )
    update_tokens_in_config(
        new_token=new_token,
        client_id=adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
    )
    audience_token = get_token_from_exchange(
        audience=audience,
        token=new_token,
        client_id=adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
        client_secret=adalib_config.KEYCLOAK_CLIENTS["jupyterhub_secret"],
        scope=scope,
    )
    return audience_token


def get_client(
    client_id: str = None,
    client_secret: str = None,
) -> keycloak.KeycloakOpenID:
    """Returns a Keycloak client configured for a specific client. Defaults to
    the Jupyterhub client.

    :param client_id: The ID of a client that is registered in Keycloak
    :param client_secret: The secret matching the given client ID
    :return: Keycloak client for the given client ID.
    :rtype: KeycloakClient
    """
    adalib_config = config.get_config()
    external = True if adalib_config.ENVIRONMENT == "external" else False
    if external:
        server_url = adalib_config.SERVICES["keycloak"]["external"] + "/auth/"
    else:
        server_url = adalib_config.SERVICES["keycloak"]["url"] + "/auth/"
    return keycloak.KeycloakOpenID(
        server_url=server_url,
        client_id=client_id,
        client_secret_key=client_secret,
        realm_name=adalib_config.KEYCLOAK_REALM,
        verify=True,
    )


def get_client_token(audience_client_id: str) -> dict:
    """Get the token for the current user to authenticate to adaboard with depending on adalib's
    environment configuration.

    :param audience_client_id: The client ID of the audience.
    :type audience_client_id: str
    :return: The token for the current user to authenticate to adaboard with.
    :rtype: dict
    """

    # First try to authenticate with stored credentials
    logging.debug("Attempting to authenticate with stored credentials.")
    token_from_stored_credentials = authenticate_with_stored_credentials(
        audience_client_id=audience_client_id
    )
    if token_from_stored_credentials is not None:
        return token_from_stored_credentials

    # If that fails, try to authenticate with user credentials
    adalib_config = config.get_config()
    logging.debug("Attempting to authenticate with provided credentials.")
    if adalib_config.ENVIRONMENT == "jupyterhub":
        return jupyterhub_authentication(audience=audience_client_id)
    elif adalib_config.ENVIRONMENT == "nonpub-user-app":
        return app_authentication(audience=audience_client_id)
    elif adalib_config.ENVIRONMENT == "external":
        return external_authentication(audience=audience_client_id)


def get_token_from_exchange(
    audience: str,
    token: str,
    client_id: str,
    client_secret: str,
    scope: str = "openid",
) -> dict:
    """Get a token for the audience given a valid client token.

    Note for developers: The scope defaults to `openid` to be consistent with the
    subsequent call to `keycloakOpenID.exchange_token(...)`. If this default is
    changed it should be done so with respect to this underlying method.

    :param audience: Client that we need to get a token for.
    :type audience: str
    :param token: Token to exchange for audience token.
    :type token: str
    :param client_id: Client ID of the client that the token is for.
    :type client_id: str
    :param client_secret: Client secret of the client that the token is for.
    :type client_secret: str
    :param scope: Scope of token requested, defaults to ""
    :type scope: str, optional
    :return: Token to access audience
    :rtype: dict
    """
    client = get_client(client_id=client_id, client_secret=client_secret)
    if not client.introspect(token=token["access_token"])["active"]:
        assert (
            "refresh_token" in token and token["refresh_token"] is not None
        ), "Access token is no longer valid and a refresh token was not provided"
        try:
            token = client.refresh_token(refresh_token=token["refresh_token"])
        except Exception as exc:
            raise AssertionError("Refresh token has expired.") from exc
        update_tokens_in_config(new_token=token, client_id=client_id)

    audience_token = client.exchange_token(
        token=token["access_token"],
        audience=audience,
        subject=None,
        scope=scope,
    )
    return audience_token


def jupyterhub_authentication(audience: str, scope: str = "openid") -> dict:
    """
    Returns an audience authentication token from an exchange with a Jupyterhub token.

    :param audience: The audience for which the token is requested.
    :type audience: str
    :param scope: The scope of the token exchange, defaults to "openid"
    :type scope: str, optional
    :return: The audience token.
    :rtype: dict
    """
    adalib_config = config.get_config()
    jh_token = jupyterhub.get_token_from_auth_state(
        username=adalib_config.CREDENTIALS["username"],
        jh_token=adalib_config.CREDENTIALS["jh_token"],
        jh_api_url=adalib_config.SERVICES["jupyterhub"]["url"] + "/hub/api",
    )
    update_tokens_in_config(
        new_token=jh_token,
        client_id=adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
    )
    audience_token = get_token_from_exchange(
        audience=audience,
        token=jh_token,
        client_id=adalib_config.KEYCLOAK_CLIENTS["jupyterhub"],
        client_secret=adalib_config.KEYCLOAK_CLIENTS["jupyterhub_secret"],
        scope=scope,
    )
    return audience_token


def update_tokens_in_config(new_token: dict, client_id: str):
    """Update the tokens in the config object.

    :param new_token: The new token to update the config with.
    :type new_token: dict
    :param client_id: The client ID of the client that the token is for.
    :type client_id: str
    """
    adalib_config = config.get_config()
    if client_id == adalib_config.KEYCLOAK_CLIENTS["jupyterhub"]:
        adalib_config.CREDENTIALS["access_token"] = new_token["access_token"]
        adalib_config.CREDENTIALS["refresh_token"] = new_token["refresh_token"]
