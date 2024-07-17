from __future__ import annotations

import typing

from digitalhub_core.client.objects.dhcore import ClientDHCore
from digitalhub_core.client.objects.local import ClientLocal

if typing.TYPE_CHECKING:
    from digitalhub_core.client.objects.base import Client


class ClientBuilder:
    """
    Client builder class.

    This class is used to create two possible client instances:
    Local and DHCore.
    It saves the client instances in the class attributes using
    singleton pattern.
    """

    def __init__(self) -> None:
        self._local = None
        self._dhcore = None

    def build(self, local: bool = False, config: dict | None = None) -> Client:
        """
        Method to create a client instance.

        Parameters
        ----------
        local : bool
            Whether to create a local client or not.

        Returns
        -------
        Client
            Returns the client instance.
        """
        if local:
            if self._local is None:
                self._local = ClientLocal()
            return self._local

        if self._dhcore is None:
            self._dhcore = ClientDHCore(config)
        return self._dhcore


def get_client(local: bool = False) -> Client:
    """
    Wrapper around ClientBuilder.build.

    Parameters
    ----------
    local : bool
        Whether to create a local client or not.

    Returns
    -------
    Client
        The client instance.
    """
    return client_builder.build(local)


def build_client(local: bool = False, config: dict | None = None) -> None:
    """
    Wrapper around ClientBuilder.build.

    Parameters
    ----------
    local : bool
        Whether to create a local client or not.
    config : dict
        DHCore env configuration.

    Returns
    -------
    Client
        The client instance.
    """
    client_builder.build(local, config)


def check_client_exists(local: bool = False) -> bool:
    """
    Check if client exists.

    Parameters
    ----------
    local : bool
        Check client existence by local.

    Returns
    -------
    bool
        True if client exists, False otherwise.
    """
    if local:
        return client_builder._local is not None
    return client_builder._dhcore is not None


client_builder = ClientBuilder()
