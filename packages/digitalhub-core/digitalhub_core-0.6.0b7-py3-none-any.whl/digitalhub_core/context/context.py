from __future__ import annotations

import typing
from pathlib import Path

if typing.TYPE_CHECKING:
    from digitalhub_core.entities.projects.entity import Project


class Context:
    """
    Context class built forom a `Project` instance. It contains
    some information about the project, such as the project name,
    a client instance (local or non-local), the local context
    project path and information about client locality.
    It exposes CRUD operations for the entities and act as a layer
    between the project object and its client.
    """

    def __init__(self, project: Project) -> None:
        self.name = project.name
        self.client = project._client
        self.local = project._client.is_local()
        self.root = Path(project.spec.context)
        self.runtime_dir = self.root / "runtime"
        self.tmp_dir = self.root / "tmp"

    def create_object(self, api: str, obj: dict, **kwargs) -> dict:
        """
        Create an object.

        Parameters
        ----------
        api : str
            Create API.
        obj : dict
            The object to create.
        **kwargs : dict
            Keyword arguments passed to the request.

        Returns
        -------
        dict
            Response object.
        """
        return self.client.create_object(api, obj, **kwargs)

    def read_object(self, api: str, **kwargs) -> dict:
        """
        Read an object.

        Parameters
        ----------
        api : str
            Read API.
        **kwargs : dict
            Keyword arguments passed to the request.

        Returns
        -------
        dict
            Response object.
        """
        return self.client.read_object(api, **kwargs)

    def update_object(self, api: str, obj: dict, **kwargs) -> dict:
        """
        Update an object.

        Parameters
        ----------
        api : str
            Update API.
        obj : dict
            The object to update.
        **kwargs : dict
            Keyword arguments passed to the request.

        Returns
        -------
        dict
            Response object.
        """
        return self.client.update_object(api, obj, **kwargs)

    def delete_object(self, api: str, **kwargs) -> dict:
        """
        Delete an object.

        Parameters
        ----------
        api : str
            Delete API.
        **kwargs : dict
            Keyword arguments passed to the request.

        Returns
        -------
        dict
            Response object.
        """
        return self.client.delete_object(api, **kwargs)

    def list_objects(self, api: str, **kwargs) -> dict:
        """
        List objects.

        Parameters
        ----------
        api : str
            The api to list the objects with.
        **kwargs : dict
            Keyword arguments passed to the request.

        Returns
        -------
        dict
            The list of objects.
        """
        return self.client.list_objects(api, **kwargs)
