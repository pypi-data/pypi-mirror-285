from __future__ import annotations

import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from zipfile import ZipFile

import numpy as np
from boto3 import client as boto3_client
from digitalhub_core.utils.io_utils import read_text
from requests import get as requests_get


def get_timestamp() -> str:
    """
    Get the current timestamp timezoned.

    Returns
    -------
    str
        The current timestamp.
    """
    return datetime.now().astimezone().isoformat()


def decode_string(string: str) -> str:
    """
    Decode a string from base64.

    Parameters
    ----------
    string : str
        The string to decode.

    Returns
    -------
    str
        The string decoded from base64.
    """
    return base64.b64decode(string).decode()


def encode_string(string: str) -> str:
    """
    Encode a string in base64.

    Parameters
    ----------
    string : str
        The string to encode.

    Returns
    -------
    str
        The string encoded in base64.
    """
    return base64.b64encode(string.encode()).decode()


def encode_source(path: str) -> str:
    """
    Read a file and encode in base64 the content.

    Parameters
    ----------
    path : str
        The file path to read.

    Returns
    -------
    str
        The file content encoded in base64.
    """
    return encode_string(read_text(path))


def requests_chunk_download(source: str, filename: Path) -> None:
    """
    Download a file in chunks.

    Parameters
    ----------
    source : str
        URL to download the file.
    filename : Path
        Path where to save the file.

    Returns
    -------
    None
    """
    with requests_get(source, stream=True) as r:
        r.raise_for_status()
        with filename.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def extract_archive(path: Path, filename: Path) -> None:
    """
    Extract a zip archive.

    Parameters
    ----------
    path : Path
        Path where to extract the archive.
    filename : Path
        Path to the archive.

    Returns
    -------
    None
    """
    with ZipFile(filename, "r") as zip_file:
        zip_file.extractall(path)


def check_overwrite(dst: str, overwrite: bool) -> None:
    """
    Check if destination path exists for overwrite.

    Parameters
    ----------
    dst : str
        Destination path as filename.
    overwrite : bool
        Specify if overwrite an existing file.

    Returns
    -------
    None

    Raises
    ------
    Exception
        If destination path exists and overwrite is False.
    """
    if Path(dst).exists() and not overwrite:
        raise Exception(f"Destination {dst} already exists.")


def get_s3_source(bucket: str, key: str, filename: Path) -> None:
    """
    Get S3 source.

    Parameters
    ----------
    bucket : str
        S3 bucket name.
    key : str
        S3 object key.
    filename : Path
        Path where to save the function source.

    Returns
    -------
    None
    """
    s3 = boto3_client("s3", endpoint_url=os.getenv("S3_ENDPOINT_URL"))
    s3.download_file(bucket, key, filename)


def get_bucket_and_key(path: str) -> tuple[str, str]:
    """
    Get bucket and key from path.

    Parameters
    ----------
    path : str
        The source path to get the key from.

    Returns
    -------
    tuple[str, str]
        The bucket and key.
    """
    parsed = urlparse(path)
    return parsed.netloc, parsed.path


class MyEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle numpy types.
    """

    def default(self, obj: Any) -> Any:
        """
        Convert numpy types to json.

        Parameters
        ----------
        obj : Any
            The object to convert.

        Returns
        -------
        Any
            The object converted to json.
        """
        if isinstance(obj, (int, str, float, list, dict)):
            return obj
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return str(obj)


def dict_to_json(struct: dict) -> str:
    """
    Convert a dict to json.

    Parameters
    ----------
    struct : dict
        The dict to convert.

    Returns
    -------
    str
        The json string.
    """
    return json.dumps(struct, cls=MyEncoder)
