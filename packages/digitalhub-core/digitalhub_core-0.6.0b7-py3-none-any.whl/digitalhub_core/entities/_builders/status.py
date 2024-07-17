from __future__ import annotations

import typing

from digitalhub_core.entities._base.status import State
from digitalhub_core.registry.registry import registry
from digitalhub_core.registry.utils import import_class

if typing.TYPE_CHECKING:
    from digitalhub_core.entities._base.status import Status
    from digitalhub_core.registry.models import RegistryEntry


def build_status(kind: str, **kwargs) -> Status:
    """
    Build entity status object. The builder takes as input
    the kind of status's object to build and the keyword
    arguments to pass to the status's constructor.
    The specific Status class is searched in the global
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
    Status
        Status object.
    """
    infos: RegistryEntry = getattr(registry, kind)
    status = import_class(infos.status.module, infos.status.class_name)
    kwargs = parse_arguments(**kwargs)
    return status(**kwargs)


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
        Keyword arguments with default values.
    """
    state = kwargs.get("state")
    if state is None:
        kwargs["state"] = State.CREATED.value
    else:
        if kwargs["state"] not in State.__members__:
            raise ValueError(f"Invalid state: {state}")
    return kwargs
