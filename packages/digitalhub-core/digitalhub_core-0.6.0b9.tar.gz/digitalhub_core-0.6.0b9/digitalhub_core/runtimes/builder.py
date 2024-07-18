from __future__ import annotations

import typing

from digitalhub_core.registry.registry import registry
from digitalhub_core.registry.utils import import_class

if typing.TYPE_CHECKING:
    from digitalhub_core.registry.models import RegistryEntry
    from digitalhub_core.runtimes.base import Runtime
    from digitalhub_core.runtimes.kind_registry import KindRegistry


def build_runtime(kind: str, project: str) -> Runtime:
    """
    Build runtime object. The builder takes in input a kind.
    This kind can derive from functions, tasks, or runs, and
    is inserted in the global kind registry where the runtimes
    pakages are registered.
    The builder requires the module path where the Runtime
    subclass is defined and the class name. It requires also
    the kind registry module, kind registry class and the project
    name.

    Parameters
    ----------
    kind : str
        The type of runtime to build.
    project : str
        The project name.

    Returns
    -------
    Runtime
        Runtime object.
    """
    infos: RegistryEntry = getattr(registry, kind)
    cls = import_class(infos.runtime.module, infos.runtime.class_name)
    kind_registry = get_kind_registry(kind)
    return cls(kind_registry, project)


def get_kind_registry(kind: str) -> KindRegistry:
    """
    Get kind registry.

    Returns
    -------
    KindRegistry
        Kind registry.
    """
    infos: RegistryEntry = getattr(registry, kind)
    return import_class(infos.runtime.kind_registry_module, infos.runtime.kind_registry_class_name)
