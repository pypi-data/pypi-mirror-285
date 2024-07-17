from __future__ import annotations

from enum import Enum

from digitalhub_core.entities._base.base import ModelObj


class State(Enum):
    """
    State enumeration.
    """

    BUILT = "BUILT"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    CREATED = "CREATED"
    CREATING = "CREATING"
    DELETED = "DELETED"
    ERROR = "ERROR"
    FSM_ERROR = "FSM_ERROR"
    IDLE = "IDLE"
    NONE = "NONE"
    ONLINE = "ONLINE"
    PENDING = "PENDING"
    READY = "READY"
    RUN_ERROR = "RUN_ERROR"
    RUNNING = "RUNNING"
    STOP = "STOP"
    STOPPED = "STOPPED"
    SUCCESS = "SUCCESS"
    UNKNOWN = "UNKNOWN"


class Status(ModelObj):
    """
    Base Status class.
    The status class contains information about the state of an entity,
    for example, the state of a RUNNING run, and eventual error message.
    """

    def __init__(self, state: str, message: str | None = None) -> None:
        """
        Constructor.

        Parameters
        ----------
        state : str
            The state of the entity.
        message : str
            Error message.
        """
        self.state = state
        self.message = message

    @classmethod
    def from_dict(cls, obj: dict) -> Status:
        """
        Return entity status object from dictionary.

        Parameters
        ----------
        obj : dict
            A dictionary containing the attributes of the entity status.

        Returns
        -------
        EntityStatus
            An entity status object.
        """
        return cls(**obj)
