from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from mimetypes import guess_type
from pathlib import Path

from pydantic import BaseModel


class FileInfo(BaseModel):
    """
    File info class.
    """

    path: str = None
    name: str = None
    content_type: str = None
    extension: str = None
    size: int = None
    hash: str = None
    last_modified: str = None


def calculate_blob_hash(data_path: str) -> str:
    """
    Calculate the hash of a file.

    Parameters
    ----------
    data_path : str
        Path to the file.

    Returns
    -------
    str
        The hash of the file.
    """
    with open(data_path, "rb") as f:
        data = f.read()
        return f"sha256:{sha256(data).hexdigest()}"


def get_file_size(data_path: str) -> int:
    """
    Get the size of a file.

    Parameters
    ----------
    data_path : str
        Path to the file.

    Returns
    -------
    int
        The size of the file.
    """
    return Path(data_path).stat().st_size


def get_file_mime_type(data_path: str) -> str:
    """
    Get the mime type of a file.

    Parameters
    ----------
    data_path : str
        Path to the file.

    Returns
    -------
    str
        The mime type of the file.
    """
    return guess_type(data_path)[0]


def get_file_extension(data_path: str) -> str:
    """
    Get the extension of a file.

    Parameters
    ----------
    data_path : str
        Path to the file.

    Returns
    -------
    str
        The extension of the file.
    """
    return Path(data_path).suffix[1:]


def get_file_name(data_path: str) -> str:
    """
    Get the name of a file.

    Parameters
    ----------
    data_path : str
        Path to the file.

    Returns
    -------
    str
        The name of the file.
    """
    return Path(data_path).name


def get_last_modified(data_path: str) -> str:
    """
    Get the last modified date of a file.

    Parameters
    ----------
    data_path : str
        Path to the file.

    Returns
    -------
    str
        The last modified date of the file.
    """
    path = Path(data_path)
    timestamp = path.stat().st_mtime
    return datetime.fromtimestamp(timestamp).astimezone().isoformat()


def get_file_info_from_local(path: str, src_path: str) -> None | dict:
    """
    Get file info from path.

    Parameters
    ----------
    path : str
        Target path of the object.
    src_path : str
        Local path of some source.

    Returns
    -------
    dict
        File info.
    """
    try:
        return FileInfo(
            path=path,
            name=get_file_name(path),
            content_type=get_file_mime_type(src_path),
            extension=get_file_extension(src_path),
            size=get_file_size(src_path),
            hash=calculate_blob_hash(src_path),
            last_modified=get_last_modified(src_path),
        ).dict()
    except Exception:
        return None


def get_file_info_from_s3(metadata: dict, path: str) -> None | dict:
    """
    Get file info from path.

    Parameters
    ----------
    metadata : dict
        Metadata of the object from S3.
    path : str
        Object key.

    Returns
    -------
    dict
        File info.
    """
    try:
        return FileInfo(
            path=path,
            name=get_file_name(path),
            content_type=metadata["ContentType"],
            extension=get_file_extension(path),
            size=metadata["ContentLength"],
            last_modified=metadata["LastModified"].isoformat(),
        ).dict()
    except Exception:
        return None
