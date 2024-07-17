from __future__ import annotations

from pydantic import BaseModel


class RuntimeEntry(BaseModel):
    """
    Model for Runtime entry.
    It specifies the module path and the runtime class name.
    """

    module: str
    """Module path."""

    class_name: str
    """Class name."""

    kind_registry_module: str
    """Kind registry module path."""

    kind_registry_class_name: str
    """Kind registry class name."""


class SpecEntry(BaseModel):
    """
    Model for Spec entry.
    It specifies the module path, the spec class name
    and the spec pydantic class validator.
    """

    module: str
    """Module path."""

    class_name: str
    """Class name."""

    parameters_validator: str
    """Class name of the parameter validator."""


class StatusEntry(BaseModel):
    """
    Model for Status entry.
    It specifies the module path and the status class name.
    """

    module: str
    """Module path."""

    class_name: str
    """Class name."""


class MetadataEntry(BaseModel):
    """
    Model for Metadata entry.
    It specifies the module path and the metadata class name.
    """

    module: str
    """Module path."""

    class_name: str
    """Class name."""


class RegistryEntry(BaseModel):
    """
    Basic entry model for every entity.
    Functions, tasks and runs specify also the runtime field.
    """

    entity_type: str
    """Entity type."""

    spec: SpecEntry
    """Spec infos."""

    status: StatusEntry
    """Status infos."""

    metadata: MetadataEntry
    """Metadata infos."""

    runtime: RuntimeEntry = None
    """Runtime infos."""
