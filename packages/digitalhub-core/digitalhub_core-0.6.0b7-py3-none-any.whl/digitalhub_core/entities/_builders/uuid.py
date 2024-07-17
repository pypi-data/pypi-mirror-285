from __future__ import annotations

from uuid import uuid4

from pydantic import UUID4, BaseModel


class UUIDValidator(BaseModel):
    """
    Validate UUID format.
    """

    uuid: UUID4


def build_uuid(uuid: str | None = None) -> str:
    """
    Create a uuid if not given. If given, validate it.

    Parameters
    ----------
    uuid : str
        ID of the object (UUID4). Optional.

    Returns
    -------
    str
        The uuid.
    """
    if uuid is not None:
        UUIDValidator(uuid=uuid)
        return uuid
    return str(uuid4())
