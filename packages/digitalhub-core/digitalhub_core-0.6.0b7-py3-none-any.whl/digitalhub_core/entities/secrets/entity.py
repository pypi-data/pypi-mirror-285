from __future__ import annotations

import typing

from digitalhub_core.context.builder import get_context
from digitalhub_core.entities._base.crud import (
    create_entity_api_ctx,
    get_data_api,
    read_entity_api_ctx,
    set_data_api,
    update_entity_api_ctx,
)
from digitalhub_core.entities._base.entity import Entity
from digitalhub_core.entities._builders.metadata import build_metadata
from digitalhub_core.entities._builders.name import build_name
from digitalhub_core.entities._builders.spec import build_spec
from digitalhub_core.entities._builders.status import build_status
from digitalhub_core.entities._builders.uuid import build_uuid
from digitalhub_core.entities.entity_types import EntityTypes
from digitalhub_core.utils.generic_utils import get_timestamp
from digitalhub_core.utils.io_utils import write_yaml

if typing.TYPE_CHECKING:
    from digitalhub_core.context.context import Context
    from digitalhub_core.entities._base.metadata import Metadata
    from digitalhub_core.entities.secrets.spec import SecretSpec
    from digitalhub_core.entities.secrets.status import SecretStatus


class Secret(Entity):
    """
    A class representing a secret.
    """

    ENTITY_TYPE = EntityTypes.SECRETS.value

    def __init__(
        self,
        project: str,
        name: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: SecretSpec,
        status: SecretStatus,
        user: str | None = None,
    ) -> None:
        """
        Constructor.

        Parameters
        ----------
        project : str
            Project name.
        name : str
            Name of the object.
        uuid : str
            Version of the object.
        kind : str
            Kind the object.
        metadata : Metadata
            Metadata of the object.
        spec : SecretSpec
            Specification of the object.
        status : SecretStatus
            Status of the object.
        user : str
            Owner of the object.
        """
        super().__init__()
        self.project = project
        self.name = name
        self.id = uuid
        self.kind = kind
        self.key = f"store://{project}/{self.ENTITY_TYPE}/{kind}/{name}:{uuid}"
        self.metadata = metadata
        self.spec = spec
        self.status = status
        self.user = user

        # Add attributes to be used in the to_dict method
        self._obj_attr.extend(["project", "name", "id", "key"])

    #############################
    #  Save / Refresh / Export
    #############################

    def save(self, update: bool = False) -> Secret:
        """
        Save entity into backend.

        Parameters
        ----------
        update : bool
            Flag to indicate update.

        Returns
        -------
        Secret
            Entity saved.
        """
        obj = self.to_dict()

        if not update:
            new_obj = create_entity_api_ctx(self.project, self.ENTITY_TYPE, obj)
            self._update_attributes(new_obj)
            return self

        self.metadata.updated = obj["metadata"]["updated"] = get_timestamp()
        new_obj = update_entity_api_ctx(self.project, self.ENTITY_TYPE, self.id, obj)
        self._update_attributes(new_obj)
        return self

    def refresh(self) -> Secret:
        """
        Refresh object from backend.

        Returns
        -------
        Secret
            Entity refreshed.
        """
        new_obj = read_entity_api_ctx(self.key)
        self._update_attributes(new_obj)
        return self

    def export(self, filename: str | None = None) -> None:
        """
        Export object as a YAML file.

        Parameters
        ----------
        filename : str
            Name of the export YAML file. If not specified, the default value is used.

        Returns
        -------
        None
        """
        obj = self.to_dict()
        if filename is None:
            filename = f"{self.kind}_{self.name}_{self.id}.yml"
        pth = self._context().root / filename
        pth.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(pth, obj)

    #############################
    #  Context
    #############################

    def _context(self) -> Context:
        """
        Get context.

        Returns
        -------
        Context
            Context.
        """
        return get_context(self.project)

    #############################
    #  Secret methods
    #############################

    def set_secret_value(self, value: str) -> None:
        """
        Set a secret.

        Parameters
        ----------
        value : str
            Value of the secret.

        Returns
        -------
        None
        """
        if self._context().local:
            raise NotImplementedError("set_secret() is not implemented for local projects.")

        obj = {self.name: value}
        set_data_api(self.project, self.ENTITY_TYPE, obj)

    def read_secret_value(self) -> dict:
        """
        Read a secret from backend.

        Returns
        -------
        str
            Value of the secret.
        """
        if self._context().local:
            raise NotImplementedError("read_secret() is not implemented for local projects.")

        params = {"keys": self.name}
        return get_data_api(self.project, self.ENTITY_TYPE, params)

    #############################
    #  Static interface methods
    #############################

    @staticmethod
    def _parse_dict(obj: dict, validate: bool = True) -> dict:
        """
        Get dictionary and parse it to a valid entity dictionary.

        Parameters
        ----------
        obj : dict
            Dictionary to parse.

        Returns
        -------
        dict
            A dictionary containing the attributes of the entity instance.
        """
        project = obj.get("project")
        name = build_name(obj.get("name"))
        kind = obj.get("kind")
        uuid = build_uuid(obj.get("id"))
        metadata = build_metadata(kind, **obj.get("metadata", {}))
        spec = build_spec(kind, validate=validate, **obj.get("spec", {}))
        status = build_status(kind, **obj.get("status", {}))
        user = obj.get("user")
        return {
            "project": project,
            "name": name,
            "uuid": uuid,
            "kind": kind,
            "metadata": metadata,
            "spec": spec,
            "status": status,
            "user": user,
        }


def secret_from_parameters(
    project: str,
    name: str,
    kind: str,
    uuid: str | None = None,
    description: str | None = None,
    git_source: str | None = None,
    labels: list[str] | None = None,
    embedded: bool = True,
    **kwargs,
) -> Secret:
    """
    Create a new Secret instance with the specified parameters.

    Parameters
    ----------
    project : str
        Project name.
    name : str
        Object name.
    kind : str
        Kind the object.
    uuid : str
        ID of the object (UUID4).
    git_source : str
        Remote git source for object.
    labels : list[str]
        List of labels.
    description : str
        Description of the object (human readable).
    embedded : bool
        Flag to determine if object must be embedded in project.
    **kwargs : dict
        Spec keyword arguments.

    Returns
    -------
    Secret
        An instance of the created secret.
    """
    name = build_name(name)
    uuid = build_uuid(uuid)
    metadata = build_metadata(
        kind,
        project=project,
        name=name,
        version=uuid,
        description=description,
        source=git_source,
        labels=labels,
        embedded=embedded,
    )
    path = f"kubernetes://dhcore-proj-secrets-{project}/{name}"
    provider = "kubernetes"
    spec = build_spec(
        kind,
        path=path,
        provider=provider,
        **kwargs,
    )
    status = build_status(kind)
    return Secret(
        project=project,
        name=name,
        uuid=uuid,
        kind=kind,
        metadata=metadata,
        spec=spec,
        status=status,
    )


def secret_from_dict(obj: dict) -> Secret:
    """
    Create Secret instance from a dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create object from.

    Returns
    -------
    Secret
        Secret instance.
    """
    return Secret.from_dict(obj)
