import logging
import os
import threading
import urllib.parse

import requests


class Singleton(type):
    """Class to ensure singleton behaviour of the Configuration class."""

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Instantiate Configuration singleton."""
        if cls not in cls._instances:
            with cls._lock:
                cls._instances[cls] = super(Singleton, cls).__call__(
                    *args, **kwargs
                )
        return cls._instances[cls]

    def reset_instances(cls):
        """Reset Configuration singleton instance."""
        if cls in cls._instances:
            with cls._lock:
                del cls._instances[cls]
        else:
            raise ValueError("No instance exists, therefore nothing to reset.")


class Configuration(metaclass=Singleton):
    """Configuration singleton class."""

    def __init__(self, adaboard_api_url=None, **kwargs):
        """Initialize Configuration instance"""
        self.LOG_LEVEL = os.getenv("ADALIB_LOG_LEVEL", "INFO")
        self.HARBOR_AUTH_FILE = os.path.join(
            os.getenv("XDG_RUNTIME_DIR", ".docker"), "config.json"
        )
        self.__configure_logging()
        self.__configure_environment()
        self.__configure_adaboard(adaboard_api_url=adaboard_api_url)
        self.__configure_clients()
        self.__configure_services(**kwargs)
        self.__configure_credentials(**kwargs)
        match self.ENVIRONMENT:
            case "jupyterhub":
                logging.info("adalib configured, running in JupyterHub.")
            case "nonpub-user-app":
                logging.info(
                    "adalib configured, running in a non-public deployed app."
                )
            case "external":
                logging.info(
                    "adalib configured, running in an external environment."
                )

    def __configure_credentials(self, **kwargs):
        """access token and refresh token refer to the JH client"""
        if self.ENVIRONMENT == "jupyterhub":
            self.CREDENTIALS = {
                "username": os.environ["LOGNAME"],
                "jh_token": os.environ["JUPYTERHUB_API_TOKEN"],
                "access_token": None,
                "refresh_token": None,
            }
        elif self.ENVIRONMENT == "nonpub-user-app":
            self.CREDENTIALS = {
                "client_id": os.environ["_UA_CLIENT_ID"],
                "client_secret": os.environ["_UA_CLIENT_SECRET"],
                "app_access_token": kwargs.get(
                    "app_access_token"
                ),  # Deployed app client
                "app_refresh_token": kwargs.get(
                    "app_refresh_token"
                ),  # Deployed app client
                "access_token": None,
                "refresh_token": None,
            }
        elif self.ENVIRONMENT == "external":
            self.CREDENTIALS = {
                "access_token": None,
                "refresh_token": None,
                "token": kwargs.get("token"),
            }

    def __configure_environment(self, **kwargs):
        """
        Find out in which environment is adalib running.
        """
        if "JUPYTERHUB_API_TOKEN" in os.environ:
            self.ENVIRONMENT = "jupyterhub"
        elif "_UA_CLIENT_ID" in os.environ:
            self.ENVIRONMENT = "nonpub-user-app"
        else:
            self.ENVIRONMENT = "external"

    def __configure_adaboard(self, adaboard_api_url=None):
        """Confgiure the target Adaboard API URL."""
        if self.ENVIRONMENT == "external" and (
            adaboard_api_url is None and "ADABOARD_API_URL" not in os.environ
        ):
            raise ValueError(
                "adaboard_api_url must be provided for external environment"
            )
        if adaboard_api_url:
            self.ADABOARD_API_URL = adaboard_api_url
        elif "ADABOARD_API_URL" in os.environ:
            self.ADABOARD_API_URL = os.environ["ADABOARD_API_URL"]
        elif "_NAMESPACE" in os.environ:
            self.ADABOARD_API_URL = (
                f"http://adaboard-api-svc.{os.environ['_NAMESPACE']}:8000"
            )
        else:
            self.ADABOARD_API_URL = "http://adaboard-api-svc:8000"

    def __configure_service_x(self, x: str, given_name: str, apps: list[dict]):
        """Configure AdaLab app or service."""
        url_type = "external" if self.ENVIRONMENT == "external" else "internal"
        for app in apps:
            if app["name"] == x:
                url_parsed = urllib.parse.urlparse(url=app[url_type])
                self.SERVICES[given_name] = {
                    "url": app["internal"],
                    "external": app["external"],
                    "netloc": url_parsed.netloc,
                    "path": url_parsed.path,
                }

    def __configure_services(self, **kwargs):
        """Configure all services present in the AdaLab deployment."""
        token = kwargs.get("token")
        headers = (
            {"Authorization": f"token {token}"} if token is not None else None
        )
        resp = requests.get(
            self.ADABOARD_API_URL,
            params={"include_apps": True},
            timeout=10,
            headers=headers,
        ).json()

        apps = resp["apps"]

        if (
            resp["jh_secret"] == ""
            and "ADALAB_CLIENT_SECRET" not in os.environ
        ):
            raise ValueError("AdaLab client secret was not set")
        elif resp["jh_secret"] == "":
            self.KEYCLOAK_CLIENTS["jupyterhub_secret"] = os.environ[
                "ADALAB_CLIENT_SECRET"
            ]
        else:
            self.KEYCLOAK_CLIENTS["jupyterhub_secret"] = resp["jh_secret"]

        namespace = resp["namespace"]
        network_host = resp["network_host"]

        self.NAMESPACE = namespace
        self.NETWORK_HOST = network_host
        self.SERVICES = dict()
        self.__configure_service_x(
            x="adaboard-api", given_name="adaboard-api", apps=apps
        )
        self.__configure_service_x(
            x="container-registry", given_name="harbor", apps=apps
        )
        self.__configure_service_x(
            x="jupyterhub", given_name="jupyterhub", apps=apps
        )
        self.__configure_service_x(
            x="keycloak", given_name="keycloak", apps=apps
        )
        self.__configure_service_x(x="mlflow", given_name="mlflow", apps=apps)
        self.__configure_service_x(
            x="superset", given_name="superset", apps=apps
        )

    def __configure_clients(self):
        """Configure clients for services present in the AdaLab deployment."""
        self.KEYCLOAK_REALM = os.environ.get("KEYCLOAK_REALM", "adalab")
        self.KEYCLOAK_CLIENTS = dict()
        self.KEYCLOAK_CLIENTS["adaboard-api"] = os.environ.get(
            "KEYCLOAK_ADABOARD_CLIENT_ID", "adaboard"
        )
        self.KEYCLOAK_CLIENTS["harbor"] = os.environ.get(
            "KEYCLOAK_HARBOR_CLIENT_ID", "harbor"
        )
        self.KEYCLOAK_CLIENTS["jupyterhub"] = os.environ.get(
            "KEYCLOAK_JUPYTERHUB_CLIENT_ID", "jupyterhub"
        )
        self.KEYCLOAK_CLIENTS["superset"] = os.environ.get(
            "KEYCLOAK_SUPERSET_CLIENT_ID", "superset"
        )

    def __configure_logging(self):
        """Set up execution logs."""
        log_level = getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    @classmethod
    def clean(cls):
        """
        Delete existing instances of the class.
        """
        cls.reset_instances()

    def reset(self, adaboard_api_url=None, **kwargs):
        """
        Clean up and create a new class instance with the new parameters.
        """
        self.clean()
        self.__init__(adaboard_api_url=adaboard_api_url, **kwargs)


def get_config(adaboard_api_url=None, **kwargs):
    """
    Initialize the Configuration singleton. This is called automatically when
    the Configuration class is imported.
    """
    return Configuration(adaboard_api_url=adaboard_api_url, **kwargs)
