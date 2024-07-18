from __future__ import annotations

import shutil
from pathlib import Path

from digitalhub_core.stores.objects.base import Store, StoreConfig
from digitalhub_core.utils.file_utils import get_file_info_from_local


class LocalStoreConfig(StoreConfig):
    """
    Local store configuration class.
    """

    path: str
    """Local path."""


class LocalStore(Store):
    """
    Local store class. It implements the Store interface and provides methods to fetch and persist
    artifacts on local filesystem based storage.
    """

    def __init__(self, name: str, store_type: str, config: LocalStoreConfig) -> None:
        """
        Constructor.

        Parameters
        ----------
        config : LocalStoreConfig
            Local store configuration.

        See Also
        --------
        Store.__init__
        """
        super().__init__(name, store_type)
        self.config = config

    ############################
    # IO methods
    ############################

    def download(self, src: str, dst: str | None = None) -> str:
        """
        Method to download an artifact from backend. Please note that this method is not
        implemented since the local store is not meant to download artifacts.

        Raises
        ------
        NotImplementedError
            This method is not implemented.
        """
        raise NotImplementedError("Local store does not support download. Use as_file() instead.")

    def fetch_artifact(self, src: str, dst: str | None = None) -> str:
        """
        Method to fetch an artifact from backend and to register it on the paths registry.
        If destination is not provided, return the source path, otherwise the path of the copied
        file.

        Parameters
        ----------
        src : str
            The source location of the artifact.
        dst : str
            The destination of the artifact.

        Returns
        -------
        str
            Returns the path of the artifact.
        """
        if dst is None:
            return src
        self._check_local_dst(dst)
        return shutil.copy(src, dst)

    def upload(self, src: str, dst: str | None = None) -> str:
        """
        Method to upload an artifact to the backend. Please note that this method is not implemented
        since the local store is not meant to upload artifacts.

        Returns
        -------
        None

        Raises
        ------
        NotImplementedError
            This method is not implemented.
        """
        raise NotImplementedError("Local store does not support upload.")

    def persist_artifact(self, src: str, dst: str | None = None) -> str:
        """
        Method to persist (copy) an artifact on local filesystem.
        If destination is not provided, the artifact is written to the default
        store path with source name.

        Parameters
        ----------
        src : str
            The source location of the artifact.
        dst : str
            The destination of the artifact.

        Returns
        -------
        dst
            Returns the URI of the artifact.
        """
        if dst is None:
            dst = str(Path(self.config.path) / Path(src).name)
        self._check_local_dst(dst)
        return shutil.copy(src, dst)

    def get_file_info(self, path: str, src_path: str | None = None) -> dict | None:
        """
        Method to get file metadata.

        Parameters
        ----------
        path : str
            The path of the file.
        src_path : str
            The source path of the file.

        Returns
        -------
        dict
            Returns the metadata of the file.
        """
        return get_file_info_from_local(path, src_path)

    ############################
    # Store interface methods
    ############################

    @staticmethod
    def is_local() -> bool:
        """
        Check if the store is local.

        Returns
        -------
        bool
            True
        """
        return True
