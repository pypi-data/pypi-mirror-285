from __future__ import annotations

from abc import ABCMeta, abstractmethod
from pathlib import Path
from tempfile import mkdtemp
from typing import Literal

from digitalhub_core.utils.exceptions import StoreError
from digitalhub_core.utils.uri_utils import map_uri_scheme
from pydantic import BaseModel


class Store(metaclass=ABCMeta):
    """
    Store abstract class.
    """

    def __init__(self, name: str, store_type: str) -> None:
        """
        Constructor.

        Parameters
        ----------
        name : str
            Store name.
        store_type : str
            Store type. Used to choose the right store implementation.

        Returns
        -------
        None
        """
        self.name = name
        self.type = store_type

        # Private attributes
        self._registry: dict[str, str] = {}

    ############################
    # IO methods
    ############################

    @abstractmethod
    def download(self, src: str, dst: str | None = None) -> str:
        """
        Method to download artifact from storage.
        """

    @abstractmethod
    def fetch_artifact(self, src: str, dst: str | None = None) -> str:
        """
        Method to fetch artifact from storage.
        """

    @abstractmethod
    def upload(self, src: str, dst: str | None = None) -> str:
        """
        Method to upload artifact to storage.
        """

    @abstractmethod
    def persist_artifact(self, src: str, dst: str | None = None) -> str:
        """
        Method to persist artifact in storage.
        """

    @abstractmethod
    def get_file_info(self, path: str, src_path: str | None = None) -> dict | None:
        """
        Method to get file metadata.
        """

    ############################
    # Helpers methods
    ############################

    def _check_local_dst(self, dst: str) -> None:
        """
        Check if the local destination directory exists. Create in case it does not.

        Parameters
        ----------
        dst : str
            The destination directory.

        Returns
        -------
        None

        Raises
        ------
        StoreError
            If the destination is not a local path.
        """
        if map_uri_scheme(dst) != "local":
            raise StoreError(f"Destination '{dst}' is not a local path.")
        self._build_path(dst)

    @staticmethod
    def _build_path(path: str) -> None:
        """
        Get path from store path and path.

        Parameters
        ----------
        path : str
            The path to build.

        Returns
        -------
        None
        """
        pth = Path(path)
        if pth.suffix != "":
            pth = pth.parent
        pth.mkdir(parents=True, exist_ok=True)

    def _build_temp(self, src: str) -> str:
        """
        Build a temporary path.

        Parameters
        ----------
        src : str
            Source filename.

        Returns
        -------
        str
            Temporary path.
        """
        tmpdir = mkdtemp()
        dst = str(Path(tmpdir) / Path(src).name)
        self._registry[src] = dst
        return dst

    @staticmethod
    @abstractmethod
    def is_local() -> bool:
        """
        Method to check if store is local.
        """


class StoreConfig(BaseModel):
    """
    Store configuration base class.
    """


class StoreParameters(BaseModel):
    """
    Store configuration class.
    """

    name: str
    """Store id."""

    type: Literal["local", "s3", "remote", "sql"]
    """Store type to instantiate."""

    config: StoreConfig = None
    """Configuration for the store."""

    is_default: bool = False
    """Flag to determine if the store is the default one."""
