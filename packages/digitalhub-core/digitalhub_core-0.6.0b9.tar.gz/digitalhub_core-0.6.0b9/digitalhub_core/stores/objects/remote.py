from __future__ import annotations

from pathlib import Path

import requests
from digitalhub_core.stores.objects.base import Store, StoreConfig


class RemoteStoreConfig(StoreConfig):
    """
    Remote store configuration class.
    """


class RemoteStore(Store):
    """
    HTTP store class. It implements the Store interface and provides methods to fetch
    artifacts from remote HTTP based storage.
    """

    def __init__(self, name: str, store_type: str, config: RemoteStoreConfig) -> None:
        """
        Constructor.

        Parameters
        ----------
        config : RemoteStoreConfig
            Remote store configuration.

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
        Method to download an artifact from backend.

        Parameters
        ----------
        src : str
            The source location of the artifact.
        dst : str
            The destination of the artifact.

        Returns
        -------
        str
            The path of the downloaded artifact.
        """
        return self._registry.get(src, self.fetch_artifact(src, dst))

    def fetch_artifact(self, src: str, dst: str | None = None) -> str:
        """
        Method to fetch an artifact from the remote storage and to register
        it on the paths registry.
        If the destination is not provided, a temporary folder will be created.

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
        dst = dst if dst is not None else self._build_temp("remote")
        if not dst.endswith(".csv") and not dst.endswith(".parquet"):
            dst = str(Path(dst) / "temp.file")
        return self._download_file(src, dst)

    def upload(self, src: str, dst: str | None = None) -> str:
        """
        Method to upload an artifact to the backend. Please note that this method is not implemented
        since the remote store is not meant to upload artifacts.

        Raises
        ------
        NotImplementedError
            This method is not implemented.
        """
        raise NotImplementedError("Remote store does not support upload.")

    def persist_artifact(self, src: str, dst: str | None = None) -> str:
        """
        Method to persist an artifact. Note that this method is not implemented
        since the remote store is not meant to write artifacts.

        Raises
        ------
        NotImplementedError
            This method is not implemented.
        """
        raise NotImplementedError("Remote store does not support persist_artifact.")

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
        None
        """

    ############################
    # Private helper methods
    ############################

    @staticmethod
    def _check_head(src) -> None:
        """
        Check if the source exists.

        Parameters
        ----------
        src : str
            The source location.

        Returns
        -------
        None

        Raises
        ------
        HTTPError
            If an error occurs while checking the source.
        """
        r = requests.head(src, timeout=60)
        r.raise_for_status()

    def _download_file(self, url: str, dst: str) -> str:
        """
        Method to download a file from a given url.

        Parameters
        ----------
        url : str
            The url of the file to download.
        dst : str
            The destination of the file.

        Returns
        -------
        str
            The path of the downloaded file.
        """
        self._check_head(url)
        self._check_local_dst(dst)
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(dst, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return dst

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
            False
        """
        return False
