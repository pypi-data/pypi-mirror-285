from __future__ import annotations

import typing

from digitalhub_core.registry.registry import registry
from digitalhub_core.registry.utils import import_class
from digitalhub_core.utils.generic_utils import get_timestamp

if typing.TYPE_CHECKING:
    from digitalhub_core.entities._base.metadata import Metadata
    from digitalhub_core.registry.models import RegistryEntry


def build_metadata(kind: str, **kwargs) -> Metadata:
    """
    Build entity metadata object. The builder takes as input
    the kind of metadata's object to build and the keyword
    arguments to pass to the metadata's constructor.
    The specific Metadata class is searched in the global
    registry, where lies info about where to find the class.
    The arguments are parsed, eventually adding default values,
    and then passed to the constructor.

    Parameters
    ----------
    kind : str
        Registry entry kind.
    **kwargs : dict
        Keyword arguments for the constructor.

    Returns
    -------
    Metadata
        Metadata object.
    """
    infos: RegistryEntry = getattr(registry, kind)
    metadata = import_class(infos.metadata.module, infos.metadata.class_name)
    kwargs = parse_arguments(**kwargs)
    return metadata(**kwargs)


def parse_arguments(**kwargs) -> dict:
    """
    Parse keyword arguments and add default values if necessary.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments.

    Returns
    -------
    dict
        A dictionary containing the entity metadata attributes.
    """
    if "created" not in kwargs or kwargs["created"] is None:
        kwargs["created"] = get_timestamp()
    if "updated" not in kwargs or kwargs["updated"] is None:
        kwargs["updated"] = kwargs["created"]
    return kwargs
