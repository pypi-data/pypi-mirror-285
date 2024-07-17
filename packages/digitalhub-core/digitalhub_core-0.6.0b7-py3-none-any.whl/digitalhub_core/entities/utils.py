from __future__ import annotations

from digitalhub_core.entities.entity_types import EntityTypes


def parse_entity_key(key: str) -> tuple[str]:
    """
    Parse the entity key. Returns project, entity type, kind, name and uuid.

    Parameters
    ----------
    key : str
        The entity key.

    Returns
    -------
    tuple[str]
        Project, entity type, kind, name and uuid.
    """
    try:
        # Remove "store://" from the key
        key = key.replace("store://", "")

        # Split the key into parts
        parts = key.split("/")

        # The project is the first part
        project = parts[0]

        # The entity type is the second part
        entity_type = parts[1]

        # The kind is the third part
        kind = parts[2]

        # Tasks and runs have no name and uuid
        if entity_type in (EntityTypes.TASKS.value, EntityTypes.RUNS.value):
            name = None
            uuid = parts[3]

        # The name and uuid are separated by a colon in the last part
        else:
            name, uuid = parts[3].split(":")

        return project, entity_type, kind, name, uuid
    except Exception as e:
        raise ValueError("Invalid key format.") from e
