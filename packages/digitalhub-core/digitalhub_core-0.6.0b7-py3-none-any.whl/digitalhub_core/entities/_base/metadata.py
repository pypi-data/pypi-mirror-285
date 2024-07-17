from __future__ import annotations

from digitalhub_core.entities._base.base import ModelObj


class Metadata(ModelObj):
    """
    A class representing the metadata of an entity.
    Metadata is a collection of information about an entity thought
    to be modifiable by the user. The information contained in the
    metadata can be discordant with the actual state of the entity,
    for example the name of the entity in the database.
    """

    def __init__(
        self,
        project: str | None = None,
        name: str | None = None,
        version: str | None = None,
        description: str | None = None,
        source: str | None = None,
        labels: list[str] | None = None,
        created: str | None = None,
        created_by: str | None = None,
        updated: str | None = None,
        updated_by: str | None = None,
        embedded: bool | None = None,
        **kwargs,
    ) -> None:
        """
        Constructor.

        Parameters
        ----------
        project : str
            Project name.
        name : str
            Name the object.
        version : str
            Version of the object.
        description : str
            Description of the entity.
        source : str
            (Remote GIT) Source of the entity.
        labels : list[str]
            A list of labels to associate with the entity.
        created : str
            Created date.
        updated : str
            Updated date.
        created_by : str
            Created by user.
        updated_by : str
            Updated by user.
        embedded : bool
            Whether the entity specifications are embedded into a project.
        """
        self.project = project
        self.name = name
        self.version = version
        self.description = description
        self.source = source
        self.labels = labels
        self.created = created
        self.updated = updated
        self.created_by = created_by
        self.updated_by = updated_by
        self.embedded = embedded

        self._any_setter(**kwargs)

    @classmethod
    def from_dict(cls, obj: dict) -> Metadata:
        """
        Return entity metadata object from dictionary.

        Parameters
        ----------
        obj : dict
            A dictionary containing the attributes of the entity metadata.

        Returns
        -------
        Metadata
            An entity metadata object.
        """
        return cls(**obj)
