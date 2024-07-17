from __future__ import annotations

import typing

from digitalhub_core.registry.registry import registry
from digitalhub_core.registry.utils import import_class

if typing.TYPE_CHECKING:
    from digitalhub_core.entities._base.spec import Spec
    from digitalhub_core.registry.models import RegistryEntry


def build_spec(kind: str, validate: bool = True, **kwargs) -> Spec:
    """
    Build entity spec object. The builder takes as input
    the kind of spec's object to build, a validation flag
    and the keyword arguments to pass to the spec's constructor.
    The specific Spec class is searched in the global registry,
    where lies info about where to find the class.
    If the validation flag is set to True, the arguments are
    validated against a pydantic schema and then passed to the
    constructor.

    Parameters
    ----------
    kind : str
        Registry entry kind.
    validate : bool
        Flag to determine if validate kwargs.
    **kwargs : dict
        Keyword arguments for the constructor.

    Returns
    -------
    Spec
        Spec object.
    """
    infos: RegistryEntry = getattr(registry, kind)
    spec = import_class(infos.spec.module, infos.spec.class_name)
    if validate:
        validator = import_class(infos.spec.module, infos.spec.parameters_validator)
        kwargs = validator(**kwargs).dict(by_alias=True, exclude_none=True)
    return spec(**kwargs)
