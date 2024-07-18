from __future__ import annotations

import os
import typing

from digitalhub_core.client.objects.base import Client
from digitalhub_core.utils.exceptions import BackendError
from pydantic import BaseModel
from requests import request
from requests.exceptions import JSONDecodeError, RequestException, Timeout

if typing.TYPE_CHECKING:
    from requests import Response

MAX_API_LEVEL = 100
MIN_API_LEVEL = 5


class AuthConfig(BaseModel):
    """Client configuration model."""

    user: str = None
    """Username."""


class OAuth2TokenAuth(AuthConfig):
    """OAuth2 token authentication model."""

    access_token: str
    """OAuth2 token."""


class BasicAuth(AuthConfig):
    """Basic authentication model."""

    password: str
    """Basic authentication password."""


class ClientDHCore(Client):
    """
    DHCore client.

    The DHCore client is used to communicate with the Digitalhub Core
    backendAPI via REST. The client supports basic authentication and
    OAuth2 token authentication.
    At creation, the client tries to get the endpoint and authentication
    parameters from the environment variables. In case the user incours
    into an authentication/endpoint error during the client creation,
    the user has the possibility to update the correct parameters using
    the `set_dhub_env` function.
    If the dhcore client is already initialized, this function will
    override the configuration, otherwise it simply set the environment
    variables.
    """

    def __init__(self, config: dict | None = None) -> None:
        super().__init__()

        self._endpoint: str | None = None
        self._auth_type: str | None = None
        self._user: str | None = None
        self._password: str | None = None
        self._access_token: str | None = None

        self._configure(config)

    def create_object(self, api: str, obj: dict, **kwargs) -> dict:
        """
        Create an object in DHCore.

        Parameters
        ----------
        api : str
            Create API.
        obj : dict
            The object to create.
        **kwargs : dict
            Keyword arguments to pass to the request.

        Returns
        -------
        dict
            Response object.
        """
        kwargs["json"] = obj
        return self._call("POST", api, **kwargs)

    def read_object(self, api: str, **kwargs) -> dict:
        """
        Get an object from DHCore.

        Parameters
        ----------
        api : str
            Read API.
        **kwargs : dict
            Keyword arguments to pass to the request.

        Returns
        -------
        dict
            Response object.
        """
        return self._call("GET", api, **kwargs)

    def update_object(self, api: str, obj: dict, **kwargs) -> dict:
        """
        Update an object in DHCore.

        Parameters
        ----------
        api : str
            Update API.
        obj : dict
            The object to update.
        **kwargs : dict
            Keyword arguments to pass to the request.

        Returns
        -------
        dict
            Response object.
        """
        kwargs["json"] = obj
        return self._call("PUT", api, **kwargs)

    def delete_object(self, api: str, **kwargs) -> dict:
        """
        Delete an object from DHCore.

        Parameters
        ----------
        api : str
            Delete API.
        **kwargs : dict
            Keyword arguments to pass to the request.

        Returns
        -------
        dict
            Response object.
        """
        resp = self._call("DELETE", api, **kwargs)
        if isinstance(resp, bool):
            resp = {"deleted": resp}
        return resp

    def list_objects(self, api: str, **kwargs) -> list[dict]:
        """
        List objects from DHCore.

        Parameters
        ----------
        api : str
            List API.
        **kwargs : dict
            Keyword arguments to pass to the request.

        Returns
        -------
        list[dict]
            Response objects.
        """
        if kwargs is None:
            kwargs = {}

        if kwargs.get("params") is None:
            kwargs["params"] = {}

        start_page = 0
        if "page" not in kwargs["params"]:
            kwargs["params"]["page"] = start_page

        objects = []
        while True:
            resp = self._call("GET", api, **kwargs)
            contents = resp["content"]
            total_pages = resp["totalPages"]
            if not contents or kwargs["params"]["page"] >= total_pages:
                break
            objects.extend(contents)
            kwargs["params"]["page"] += 1

        return objects

    def _call(self, call_type: str, api: str, **kwargs) -> dict:
        """
        Make a call to the DHCore API.

        Parameters
        ----------
        call_type : str
            The type of call to make.
        api : str
            The api to call.
        **kwargs : dict
            Keyword arguments to pass to the request.

        Returns
        -------
        dict
            Response object.
        """
        # Set URL
        url = self._build_url(api)

        # Choose auth type
        kwargs = self._set_auth_header(kwargs)

        # Call the API
        response = request(call_type, url, timeout=60, **kwargs)

        # Parse the response
        self._raise_for_error(response)
        self._check_core_version(response)
        return self._parse_response(response)

    def _build_url(self, api: str) -> str:
        """
        Build the URL for the DHCore API.

        Parameters
        ----------
        api : str
            The api to call.

        Returns
        -------
        str
            The URL for the DHCore API.
        """
        return self._endpoint + api

    def _set_auth_header(self, kwargs: dict) -> dict:
        """
        Set the authentication header.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments to pass to the request.

        Returns
        -------
        dict
            Keyword arguments with the authentication header.
        """
        if self._auth_type == "basic":
            kwargs["auth"] = self._user, self._password
        elif self._auth_type == "oauth2":
            kwargs["headers"] = {"Authorization": f"Bearer {self._access_token}"}

        return kwargs

    def _raise_for_error(self, response: Response) -> None:
        """
        Raise an exception if the response indicates an error.

        Parameters
        ----------
        response : Response
            The response object.

        Returns
        -------
        None
        """
        try:
            response.raise_for_status()
        except RequestException as e:
            if isinstance(e, Timeout):
                msg = "Request to DHCore backend timed out."
            elif isinstance(e, ConnectionError):
                msg = "Unable to connect to DHCore backend."
            else:
                msg = f"Backend error. Status code: {e.response.status_code}. Reason: {e.response.text}"
            raise BackendError(msg) from e
        except Exception as e:
            msg = f"Some error occurred: {e}"
            raise RuntimeError(msg) from e

    def _check_core_version(self, response: Response) -> None:
        """
        Raise an exception if the response indicates an error.

        Parameters
        ----------
        response : Response
            The response object.

        Returns
        -------
        None
        """
        if "X-Api-Level" in response.headers:
            core_api_level = int(response.headers["X-Api-Level"])
            if not (MIN_API_LEVEL <= core_api_level <= MAX_API_LEVEL):
                raise BackendError("Backend API level not supported.")

    def _parse_response(self, response: Response) -> dict:
        """
        Parse the response object.

        Parameters
        ----------
        response : Response
            The response object.

        Returns
        -------
        dict
            The parsed response object.
        """
        try:
            return response.json()
        except JSONDecodeError:
            if response.text == "":
                return {}
            raise BackendError("Backend response could not be parsed.")

    ################################
    # Configuration methods
    ################################

    def _configure(self, config: dict | None = None) -> None:
        """
        Configure the client attributes with config (given or from
        environment).
        Regarding authentication parameters, the config parameter
        takes precedence over the env variables, and the token
        over the basic auth. Furthermore, the config parameter is
        validated against the proper pydantic model.

        Parameters
        ----------
        config : dict
            Configuration dictionary.

        Returns
        -------
        None
        """
        self._get_endpoint_from_env()

        if config is not None:
            if config.get("access_token") is not None:
                config = OAuth2TokenAuth(**config)
                self._user = config.user
                self._access_token = config.access_token
                self._auth_type = "oauth2"

            elif config.get("user") is not None and config.get("password") is not None:
                config = BasicAuth(**config)
                self._user = config.user
                self._password = config.password
                self._auth_type = "basic"

            return

        self._get_auth_from_env()

    def _get_endpoint_from_env(self) -> None:
        """
        Get the DHCore endpoint from the env.

        Returns
        -------
        None

        Raises
        ------
        Exception
            If the endpoint of DHCore is not set in the env variables.
        """
        endpoint = os.getenv("DIGITALHUB_CORE_ENDPOINT")
        if endpoint is None:
            raise BackendError("Endpoint not set as environment variables.")

        # Sanitize endpoint string
        sanitized_endpoint = endpoint.removesuffix("/")

        # Set endpoint
        self._endpoint = sanitized_endpoint

    def _get_auth_from_env(self) -> None:
        """
        Get authentication parameters from the env.

        Returns
        -------
        None
        """
        self._user = os.getenv("DIGITALHUB_CORE_USER")

        token = os.getenv("DIGITALHUB_CORE_TOKEN")
        if token is not None and token != "":
            self._auth_type = "oauth2"
            self._access_token = token
            return

        password = os.getenv("DIGITALHUB_CORE_PASSWORD")
        if self._user is not None and password is not None:
            self._auth_type = "basic"
            self._password = password
            return

    @staticmethod
    def is_local() -> bool:
        """
        Declare if Client is local.

        Returns
        -------
        bool
            False
        """
        return False
