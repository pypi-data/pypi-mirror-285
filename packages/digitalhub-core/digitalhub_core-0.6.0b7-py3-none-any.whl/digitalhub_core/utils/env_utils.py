from __future__ import annotations

import os
import typing

from digitalhub_core.client.builder import check_client_exists, get_client

if typing.TYPE_CHECKING:
    from digitalhub_core.client.objects.dhcore import ClientDHCore


def set_dhub_env(
    endpoint: str | None = None,
    user: str | None = None,
    password: str | None = None,
    token: str | None = None,
) -> None:
    """
    Function to set environment variables for DHub Core config.
    Note that if the environment variable is already set, it will be overwritten.
    It also ovverides the remote client config.

    Parameters
    ----------
    endpoint : str
        The endpoint of DHub Core.
    user : str
        The user of DHub Core.
    password : str
        The password of DHub Core.
    token : str
        The token of DHub Core.

    Returns
    -------
    None
    """
    if endpoint is not None:
        os.environ["DIGITALHUB_CORE_ENDPOINT"] = endpoint
    if user is not None:
        os.environ["DIGITALHUB_CORE_USER"] = user
    if password is not None:
        os.environ["DIGITALHUB_CORE_PASSWORD"] = password
    if token is not None:
        os.environ["DIGITALHUB_CORE_TOKEN"] = token

    if check_client_exists(local=False):
        update_client_from_env()


def update_client_from_env() -> None:
    """
    Function to update client from environment variables.

    Returns
    -------
    None
    """
    client: ClientDHCore = get_client(local=False)

    # Update endpoint
    endpoint = os.getenv("DIGITALHUB_CORE_ENDPOINT")
    if endpoint is not None:
        client._endpoint = endpoint

    # Update auth

    # If token is set, it will override the other auth options
    token = os.getenv("DIGITALHUB_CORE_TOKEN")
    if token is not None:
        client._access_token = token
        client._auth_type = "oauth2"
        return

    # Otherwise, if user and password are set, basic auth will be used
    username = os.getenv("DIGITALHUB_CORE_USER")
    password = os.getenv("DIGITALHUB_CORE_PASSWORD")
    if username is not None and password is not None:
        client._user = username
        client._password = password
        client._auth_type = "basic"


def get_s3_bucket() -> str | None:
    """
    Function to get S3 bucket name.

    Returns
    -------
    str
        The S3 bucket name.
    """
    return os.getenv("S3_BUCKET_NAME", "datalake")
