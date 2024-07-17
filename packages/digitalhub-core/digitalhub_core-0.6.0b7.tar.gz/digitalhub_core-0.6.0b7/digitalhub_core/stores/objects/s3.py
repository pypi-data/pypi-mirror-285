from __future__ import annotations

from io import BytesIO
from typing import Type
from urllib.parse import urlparse

import boto3
import botocore.client  # pylint: disable=unused-import
from botocore.exceptions import ClientError
from digitalhub_core.stores.objects.base import Store, StoreConfig
from digitalhub_core.utils.exceptions import StoreError
from digitalhub_core.utils.file_utils import get_file_info_from_s3

# Type aliases
S3Client = Type["botocore.client.S3"]


class S3StoreConfig(StoreConfig):
    """
    S3 store configuration class.
    """

    endpoint_url: str
    """S3 endpoint URL."""

    aws_access_key_id: str
    """AWS access key ID."""

    aws_secret_access_key: str
    """AWS secret access key."""

    bucket_name: str
    """S3 bucket name."""


class S3Store(Store):
    """
    S3 store class. It implements the Store interface and provides methods to fetch and persist
    artifacts on S3 based storage.
    """

    def __init__(self, name: str, store_type: str, config: S3StoreConfig) -> None:
        """
        Constructor.

        Parameters
        ----------
        config : S3StoreConfig
            S3 store configuration.

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
        Download an artifact from S3 based storage.

        See Also
        --------
        fetch_artifact
        """
        return self._registry.get(src, self.fetch_artifact(src, dst))

    def fetch_artifact(self, src: str, dst: str | None = None) -> str:
        """
        Fetch an artifact from S3 based storage. If the destination is not provided,
        a temporary directory will be created and the artifact will be saved there.

        Parameters
        ----------
        src : str
            The source location of the artifact on S3.
        dst : str
            The destination of the artifact on local filesystem.

        Returns
        -------
        str
            Returns the path of the downloaded artifact.
        """
        dst = dst if dst is not None else self._build_temp(src)
        bucket = urlparse(src).netloc
        key = self._get_key(src)
        return self._download_file(bucket, key, dst)

    def upload(self, src: str, dst: str | None = None) -> str:
        """
        Upload an artifact to S3 based storage.

        See Also
        --------
        persist_artifact
        """
        return self.persist_artifact(src, dst)

    def persist_artifact(self, src: str, dst: str | None = None) -> str:
        """
        Persist an artifact on S3 based storage. If the destination is not provided,
        the key will be extracted from the source path.

        Parameters
        ----------
        src : Any
            The source object to be persisted.
        dst : str
            The destination partition for the artifact.

        Returns
        -------
        str
            Returns the URI of the artifact on S3 based storage.
        """
        key = self._get_key(dst) if dst is not None else self._get_key(src)
        return self._upload_file(src, key)

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
        bucket = self._get_bucket()
        key = self._get_key(path)
        client = self._get_client()
        self._check_access_to_storage(client, bucket)
        metadata = client.head_object(Bucket=bucket, Key=key)
        return get_file_info_from_s3(metadata, path)

    ############################
    # Private helper methods
    ############################

    def _get_bucket(self) -> str:
        """
        Get the name of the S3 bucket from the URI.

        Returns
        -------
        str
            The name of the S3 bucket.
        """
        return str(self.config.bucket_name)

    def _get_client(self) -> S3Client:
        """
        Get an S3 client object.

        Returns
        -------
        S3Client
            Returns a client object that interacts with the S3 storage service.
        """
        cfg = {
            "endpoint_url": self.config.endpoint_url,
            "aws_access_key_id": self.config.aws_access_key_id,
            "aws_secret_access_key": self.config.aws_secret_access_key,
        }
        return boto3.client("s3", **cfg)

    @staticmethod
    def _get_key(path: str) -> str:
        """
        Build key.

        Parameters
        ----------
        path : str
            The source path to get the key from.

        Returns
        -------
        str
            The key.
        """
        key = urlparse(path).path
        if key.startswith("/"):
            key = key[1:]
        return key

    def _check_factory(self) -> tuple[S3Client, str]:
        """
        Check if the S3 bucket is accessible by sending a head_bucket request.

        Returns
        -------
        tuple[S3Client, str]
            A tuple containing the S3 client object and the name of the S3 bucket.
        """
        client = self._get_client()
        bucket = self._get_bucket()
        self._check_access_to_storage(client, bucket)
        return client, bucket

    def _check_access_to_storage(self, client: S3Client, bucket: str) -> None:
        """
        Check if the S3 bucket is accessible by sending a head_bucket request.

        Parameters
        ----------
        client : S3Client
            The S3 client object.
        bucket : str
            The name of the S3 bucket.

        Returns
        -------
        None

        Raises
        ------
        StoreError:
            If access to the specified bucket is not available.
        """
        try:
            client.head_bucket(Bucket=bucket)
        except ClientError as e:
            raise StoreError("No access to s3 bucket!") from e

    def _download_file(self, bucket: str, key: str, dst: str) -> str:
        """
        Download a file from S3 based storage. The function checks if the bucket is accessible
        and if the destination directory exists. If the destination directory does not exist,
        it will be created.

        Parameters
        ----------
        bucket : str
            The name of the S3 bucket.
        key : str
            The key of the file on S3 based storage.
        dst : str
            The destination of the file on local filesystem.

        Returns
        -------
        str
            The path of the downloaded file.
        """
        client = self._get_client()
        self._check_access_to_storage(client, bucket)
        self._check_local_dst(dst)
        client.download_file(bucket, key, dst)
        return dst

    def _upload_file(self, src: str, key: str) -> str:
        """
        Upload a file to S3 based storage. The function checks if the bucket is accessible.

        Parameters
        ----------
        src : str
            The source path of the file on local filesystem.
        key : str
            The key of the file on S3 based storage.

        Returns
        -------
        str
            The URI of the uploaded file on S3 based storage.
        """
        client, bucket = self._check_factory()
        client.upload_file(Filename=src, Bucket=bucket, Key=key)
        return f"s3://{bucket}/{key}"

    def _upload_fileobj(self, fileobj: BytesIO, key: str) -> str:
        """
        Upload a fileobject to S3 based storage. The function checks if the bucket is accessible.

        Parameters
        ----------
        fileobj : BytesIO
            The fileobject to be uploaded.
        key : str
            The key of the file on S3 based storage.

        Returns
        -------
        str
            The URI of the uploaded fileobject on S3 based storage.
        """
        client, bucket = self._check_factory()
        client.put_object(Bucket=bucket, Key=key, Body=fileobj.getvalue())
        return f"s3://{bucket}/{key}"

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
