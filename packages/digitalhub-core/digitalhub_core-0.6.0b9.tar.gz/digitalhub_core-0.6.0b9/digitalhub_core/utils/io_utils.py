from __future__ import annotations

from pathlib import Path

import yaml

####################
# Writers
####################


def write_yaml(filepath: str | Path, obj: dict | list[dict]) -> None:
    """
    Write a dict or a list of dict to a yaml file.

    Parameters
    ----------
    filepath : str | Path
        The yaml file path to write.
    obj : dict
        The dict to write.

    Returns
    -------
    None
    """
    if isinstance(obj, list):
        with open(filepath, "w", encoding="utf-8") as out_file:
            yaml.dump_all(obj, out_file, sort_keys=False, default_flow_style=False)
    else:
        with open(filepath, "w", encoding="utf-8") as out_file:
            yaml.dump(obj, out_file, sort_keys=False)


####################
# Readers
####################


def read_yaml(filepath: str | Path) -> dict | list[dict]:
    """
    Read a yaml file and return a dict or a list of dict.

    Parameters
    ----------
    filepath : str | Path
        The yaml file path to read.

    Returns
    -------
    dict | list[dict]
        The yaml file content.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as in_file:
            data = yaml.load(in_file, Loader=yaml.SafeLoader)

    # If yaml contains multiple documents
    except yaml.composer.ComposerError:
        with open(filepath, "r", encoding="utf-8") as in_file:
            data = list(yaml.load_all(in_file, Loader=yaml.SafeLoader))
    return data


def read_text(filepath: str | Path) -> str:
    """
    Read a file and return the text.

    Parameters
    ----------
    filepath : str | Path
        The file path to read.

    Returns
    -------
    str
        The file content.
    """
    return Path(filepath).read_text(encoding="utf-8")
