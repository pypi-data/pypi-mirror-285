from __future__ import annotations

from digitalhub_core.registry.models import RegistryEntry


class GlobalEntityRegistry:
    """
    Global entity registry where all entities classpaths are stored.
    It keeps track of all entities that are registered in the system.
    """

    def register(self, entity_kind: str, entry: dict) -> None:
        """
        Register an entity kind.

        Parameters
        ----------
        entity_kind : str
            Entity kind to be registered.
        entry : dict
            Entry to be registered.

        Returns
        -------
        None

        """
        if hasattr(self, entity_kind):
            raise ValueError(f"Entity kind {entity_kind} already registered")
        entry = RegistryEntry(**entry)
        setattr(self, entity_kind, entry)

    def update(self, entity_kind: str, entry: dict) -> None:
        """
        Update an entity kind.

        Parameters
        ----------
        entity_kind : str
            Entity kind to be updated.
        entry : dict
            Entry to be updated.

        Returns
        -------
        None
        """
        if hasattr(self, entity_kind):
            entry = RegistryEntry(**entry)
            setattr(self, entity_kind, entry)
        else:
            raise ValueError(f"Entity kind {entity_kind} not registered")

    def get_entity_type(self, entity_kind: str) -> str:
        """
        Get entity type from kind.

        Parameters
        ----------
        entity_kind : str
            Entity kind.

        Returns
        -------
        str
            Entity type.
        """
        if not hasattr(self, entity_kind):
            raise ValueError(f"Entity kind {entity_kind} not registered")
        entry: RegistryEntry = getattr(self, entity_kind)
        return entry.entity_type


registry = GlobalEntityRegistry()
