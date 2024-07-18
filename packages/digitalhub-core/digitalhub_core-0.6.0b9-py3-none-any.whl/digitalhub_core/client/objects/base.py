from __future__ import annotations

from abc import abstractmethod


class Client:
    """
    Base Client class interface.

    The client is an interface that handles the CRUD of an object during
    a session. It manages the creation, reading, updating, deleting and
    listing of objects and comes into two subclasses: Local and DHCore.
    """

    @abstractmethod
    def create_object(self, api: str, obj: dict, **kwargs) -> dict:
        """
        Create object method.
        """

    @abstractmethod
    def read_object(self, api: str, **kwargs) -> dict:
        """
        Read object method.
        """

    @abstractmethod
    def update_object(self, api: str, obj: dict, **kwargs) -> dict:
        """
        Update object method.
        """

    @abstractmethod
    def delete_object(self, api: str, **kwargs) -> dict:
        """
        Delete object method.
        """

    @abstractmethod
    def list_objects(self, api: str, **kwargs) -> dict:
        """
        Generic call method.
        """

    @staticmethod
    @abstractmethod
    def is_local() -> bool:
        """
        Flag to check if client is local.
        """
