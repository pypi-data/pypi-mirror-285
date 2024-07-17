from __future__ import annotations

import typing
from pathlib import Path

from digitalhub_core.client.builder import get_client
from digitalhub_core.context.builder import set_context
from digitalhub_core.entities._base.crud import (
    create_entity_api_base,
    read_entity_api_base,
    read_entity_api_ctx,
    update_entity_api_base,
)
from digitalhub_core.entities._base.entity import Entity
from digitalhub_core.entities._builders.metadata import build_metadata
from digitalhub_core.entities._builders.name import build_name
from digitalhub_core.entities._builders.spec import build_spec
from digitalhub_core.entities._builders.status import build_status
from digitalhub_core.entities.artifacts.crud import (
    create_artifact_from_dict,
    delete_artifact,
    get_artifact,
    list_artifacts,
    log_artifact,
    new_artifact,
)
from digitalhub_core.entities.entity_types import EntityTypes
from digitalhub_core.entities.functions.crud import (
    create_function_from_dict,
    delete_function,
    get_function,
    list_functions,
    new_function,
)
from digitalhub_core.entities.secrets.crud import (
    create_secret_from_dict,
    delete_secret,
    get_secret,
    list_secrets,
    new_secret,
)
from digitalhub_core.entities.workflows.crud import (
    create_workflow_from_dict,
    delete_workflow,
    get_workflow,
    list_workflows,
    new_workflow,
)
from digitalhub_core.utils.exceptions import BackendError
from digitalhub_core.utils.generic_utils import get_timestamp
from digitalhub_core.utils.io_utils import write_yaml

if typing.TYPE_CHECKING:
    from digitalhub_core.entities._base.metadata import Metadata
    from digitalhub_core.entities.artifacts.entity import Artifact
    from digitalhub_core.entities.functions.entity import Function
    from digitalhub_core.entities.projects.spec import ProjectSpec
    from digitalhub_core.entities.projects.status import ProjectStatus
    from digitalhub_core.entities.secrets.entity import Secret
    from digitalhub_core.entities.workflows.entity import Workflow


ARTIFACTS = EntityTypes.ARTIFACTS.value
FUNCTIONS = EntityTypes.FUNCTIONS.value
WORKFLOWS = EntityTypes.WORKFLOWS.value
SECRETS = EntityTypes.SECRETS.value

CTX_ENTITIES = [
    ARTIFACTS,
    FUNCTIONS,
    WORKFLOWS,
    SECRETS,
]
FUNC_MAP = {
    ARTIFACTS: create_artifact_from_dict,
    FUNCTIONS: create_function_from_dict,
    WORKFLOWS: create_workflow_from_dict,
    SECRETS: create_secret_from_dict,
}


class Project(Entity):
    """
    A class representing a project.
    """

    ENTITY_TYPE = EntityTypes.PROJECTS.value

    def __init__(
        self,
        name: str,
        kind: str,
        metadata: Metadata,
        spec: ProjectSpec,
        status: ProjectStatus,
        user: str | None = None,
        local: bool = False,
    ) -> None:
        """
        Constructor.

        Parameters
        ----------
        name : str
            Name of the object.
        kind : str
            Kind the object.
        metadata : Metadata
            Metadata of the object.
        spec : ProjectSpec
            Specification of the object.
        status : ProjectStatus
            Status of the object.
        user : str
            Owner of the object.
        local: bool
            If True, export locally.
        """
        super().__init__()
        self.id = name
        self.name = name
        self.kind = kind
        self.key = f"store://{name}"
        self.metadata = metadata
        self.spec = spec
        self.status = status
        self.user = user

        # Add attributes to be used in the to_dict method
        self._obj_attr.extend(["id", "name", "key"])

        # Set client
        self._client = get_client(local)

        # Set context
        set_context(self)

    #############################
    #  Save / Refresh / Export
    #############################

    def save(self, update: bool = False) -> Project:
        """
        Save entity into backend.

        Parameters
        ----------
        update : bool
            If True, the object will be updated.

        Returns
        -------
        Project
            Entity saved.
        """
        obj = self._refresh_to_dict()

        if not update:
            new_obj = create_entity_api_base(self._client, self.ENTITY_TYPE, obj)
            new_obj["local"] = self._client.is_local()
            self._update_attributes(new_obj)
            return self

        self.metadata.updated = obj["metadata"]["updated"] = get_timestamp()
        new_obj = update_entity_api_base(self._client, self.ENTITY_TYPE, obj)
        new_obj["local"] = self._client.is_local()
        self._update_attributes(new_obj)
        return self

    def refresh(self) -> Project:
        """
        Refresh object from backend.

        Returns
        -------
        Project
            Project object.
        """
        new_obj = read_entity_api_base(self._client, self.ENTITY_TYPE, self.name)
        new_obj["local"] = self._client.is_local()
        self._update_attributes(new_obj)
        return self

    def export(self, filename: str | None = None) -> None:
        """
        Export object as a YAML file. If the objects are not embedded, the objects are
        exported as a YAML file.

        Parameters
        ----------
        filename : str
            Name of the export YAML file. If not specified, the default value is used.

        Returns
        -------
        None
        """
        obj = self._refresh_to_dict()

        if filename is None:
            filename = f"{self.kind}_{self.name}.yml"
        pth = Path(self.spec.context) / filename
        pth.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(pth, obj)

        for entity_type in CTX_ENTITIES:
            entity_list = obj.get("spec", {}).get(entity_type, [])
            if not entity_list:
                continue
            self._export_not_embedded(entity_list, entity_type)

    def _refresh_to_dict(self) -> dict:
        """
        Try to refresh object to collect entities related to project.

        Returns
        -------
        dict
            Entity object in dictionary format.
        """
        try:
            return self.refresh().to_dict()
        except BackendError:
            return self.to_dict()

    def _export_not_embedded(self, entity_list: list, entity_type: str) -> None:
        """
        Export project objects if not embedded.

        Parameters
        ----------
        entity_list : list
            Entity list.

        Returns
        -------
        None
        """
        for entity in entity_list:
            if not entity["metadata"]["embedded"]:
                obj: dict = read_entity_api_ctx(entity["key"])
                ent = FUNC_MAP[entity_type](obj)
                ent.export()

    #############################
    #  Artifacts
    #############################

    def new_artifact(
        self,
        name: str,
        kind: str,
        uuid: str | None = None,
        description: str | None = None,
        git_source: str | None = None,
        labels: list[str] | None = None,
        embedded: bool = True,
        path: str | None = None,
        src_path: str | None = None,
        **kwargs,
    ) -> Artifact:
        """
        Create an instance of the Artifact class with the provided parameters.

        Parameters
        ----------
        name : str
            Object name.
        kind : str
            Kind the object.
        uuid : str
            ID of the object (UUID4).
        description : str
            Description of the object (human readable).
        git_source : str
            Remote git source for object.
        labels : list[str]
            List of labels.
        embedded : bool
            Flag to determine if object must be embedded in project.
        path : str
            Object path on local file system or remote storage.
            If not provided, it's generated.
        src_path : str
            Local object path.
        **kwargs : dict
            Spec keyword arguments.

        Returns
        -------
        Artifact
            Object instance.
        """
        obj = new_artifact(
            project=self.name,
            name=name,
            kind=kind,
            uuid=uuid,
            description=description,
            git_source=git_source,
            labels=labels,
            embedded=embedded,
            path=path,
            src_path=src_path,
            **kwargs,
        )
        self.refresh()
        return obj

    def get_artifact(
        self,
        identifier: str,
        entity_id: str | None = None,
        **kwargs,
    ) -> Artifact:
        """
        Get object from backend.

        Parameters
        ----------
        identifier : str
            Entity key or name.
        entity_id : str
            Entity ID.
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        Artifact
            Instance of Artifact class.
        """
        obj = get_artifact(
            identifier=identifier,
            project=self.name,
            entity_id=entity_id,
            **kwargs,
        )
        self.refresh()
        return obj

    def delete_artifact(
        self,
        identifier: str,
        entity_id: str | None = None,
        delete_all_versions: bool = False,
        **kwargs,
    ) -> None:
        """
        Delete a Artifact from project.

        Parameters
        ----------
        identifier : str
            Entity key or name.
        project : str
            Project name.
        entity_id : str
            Entity ID.
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        None
        """
        delete_artifact(
            identifier=identifier,
            project=self.name,
            entity_id=entity_id,
            delete_all_versions=delete_all_versions,
            **kwargs,
        )
        self.refresh()

    def list_artifacts(self, **kwargs) -> list[dict]:
        """
        List artifacts associated with the project.

        Parameters
        ----------
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        list[dict]
            List of objects related to project.
        """
        return list_artifacts(self.name, **kwargs)

    def log_artifact(
        self,
        name: str,
        kind: str,
        path: str | None = None,
        source_path: str | None = None,
        **kwargs,
    ) -> Artifact:
        """
        Create and upload an artifact.

        Parameters
        ----------
        name : str
            Object name.
        kind : str
            Kind the object.
        path : str
            Destination path of the artifact.
        source_path : str
            Artifact location on local machine.
        **kwargs : dict
            New artifact parameters.

        Returns
        -------
        Artifact
            Instance of Artifact class.
        """
        obj = log_artifact(
            project=self.name,
            name=name,
            kind=kind,
            path=path,
            source_path=source_path,
            **kwargs,
        )
        self.refresh()
        return obj

    #############################
    #  Functions
    #############################

    def new_function(
        self,
        name: str,
        kind: str,
        uuid: str | None = None,
        description: str | None = None,
        git_source: str | None = None,
        labels: list[str] | None = None,
        embedded: bool = True,
        **kwargs,
    ) -> Function:
        """
        Create a Function instance with the given parameters.

        Parameters
        ----------
        name : str
            Object name.
        kind : str
            Kind the object.
        uuid : str
            ID of the object (UUID4).
        description : str
            Description of the object (human readable).
        git_source : str
            Remote git source for object.
        labels : list[str]
            List of labels.
        embedded : bool
            Flag to determine if object must be embedded in project.
        **kwargs : dict
            Spec keyword arguments.

        Returns
        -------
        Function
            Object instance.
        """
        obj = new_function(
            project=self.name,
            name=name,
            kind=kind,
            uuid=uuid,
            description=description,
            git_source=git_source,
            labels=labels,
            embedded=embedded,
            **kwargs,
        )
        self.refresh()
        return obj

    def get_function(
        self,
        identifier: str,
        entity_id: str | None = None,
        **kwargs,
    ) -> Function:
        """
        Get object from backend.

        Parameters
        ----------
        identifier : str
            Entity key or name.
        project : str
            Project name.
        entity_id : str
            Entity ID.
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        Function
            Instance of Function class.
        """
        obj = get_function(
            identifier=identifier,
            project=self.name,
            entity_id=entity_id,
            **kwargs,
        )
        self.refresh()
        return obj

    def delete_function(
        self,
        identifier: str,
        entity_id: str | None = None,
        delete_all_versions: bool = False,
        cascade: bool = False,
        **kwargs,
    ) -> None:
        """
        Delete a Function from project.

        Parameters
        ----------
        identifier : str
            Entity key or name.
        project : str
            Project name.
        entity_id : str
            Entity ID.
        delete_all_versions : bool
            Delete all versions of the named entity.
            Use entity name instead of entity key as identifier.
        cascade : bool
            Cascade delete.
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        None
        """
        delete_function(
            identifier=identifier,
            project=self.name,
            entity_id=entity_id,
            delete_all_versions=delete_all_versions,
            cascade=cascade,
            **kwargs,
        )
        self.refresh()

    def list_functions(self, **kwargs) -> list[dict]:
        """
        List functions associated with the project.

        Parameters
        ----------
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        list[dict]
            List of objects related to project.
        """
        return list_functions(self.name, **kwargs)

    #############################
    #  Workflows
    #############################

    def new_workflow(
        self,
        name: str,
        kind: str,
        uuid: str | None = None,
        description: str | None = None,
        git_source: str | None = None,
        labels: list[str] | None = None,
        embedded: bool = True,
        **kwargs,
    ) -> Workflow:
        """
        Create a new Workflow instance with the specified parameters.

        Parameters
        ----------
        project : str
            Project name.
        name : str
            Object name.
        uuid : str
            ID of the object (UUID4).
        description : str
            Description of the object (human readable).
        git_source : str
            Remote git source for object.
        labels : list[str]
            List of labels.
        embedded : bool
            Flag to determine if object must be embedded in project.
        **kwargs : dict
            Spec keyword arguments.

        Returns
        -------
        Workflow
            An instance of the created workflow.
        """
        obj = new_workflow(
            project=self.name,
            name=name,
            kind=kind,
            uuid=uuid,
            description=description,
            git_source=git_source,
            labels=labels,
            embedded=embedded,
            **kwargs,
        )
        self.refresh()
        return obj

    def get_workflow(
        self,
        identifier: str,
        entity_id: str | None = None,
        **kwargs,
    ) -> Workflow:
        """
        Get object from backend.

        Parameters
        ----------
        identifier : str
            Entity key or name.
        project : str
            Project name.
        entity_id : str
            Entity ID.
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        Workflow
            Instance of Workflow class.
        """
        obj = get_workflow(
            identifier=identifier,
            project=self.name,
            entity_id=entity_id,
            **kwargs,
        )
        self.refresh()
        return obj

    def delete_workflow(
        self,
        identifier: str,
        entity_id: str | None = None,
        delete_all_versions: bool = False,
        cascade: bool = False,
        **kwargs,
    ) -> None:
        """
        Delete a Workflow from project.

        Parameters
        ----------
        identifier : str
            Entity key or name.
        project : str
            Project name.
        entity_id : str
            Entity ID.
        delete_all_versions : bool
            Delete all versions of the named entity.
            Use entity name instead of entity key as identifier.
        cascade : bool
            Cascade delete.
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        None
        """
        delete_workflow(
            identifier=identifier,
            project=self.name,
            entity_id=entity_id,
            delete_all_versions=delete_all_versions,
            cascade=cascade,
            **kwargs,
        )
        self.refresh()

    def list_workflows(self, **kwargs) -> list[dict]:
        """
        List workflows associated with the project.

        Parameters
        ----------
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        list[dict]
            List of objects related to project.
        """
        return list_workflows(self.name, **kwargs)

    #############################
    #  Secrets
    #############################

    def new_secret(
        self,
        name: str,
        uuid: str | None = None,
        description: str | None = None,
        git_source: str | None = None,
        labels: list[str] | None = None,
        embedded: bool = True,
        secret_value: str | None = None,
        **kwargs,
    ) -> Secret:
        """
        Create a new Secret instance with the specified parameters.

        Parameters
        ----------
        name : str
            Object name.
        uuid : str
            ID of the object (UUID4).
        description : str
            Description of the object (human readable).
        git_source : str
            Remote git source for object.
        labels : list[str]
            List of labels.
        embedded : bool
            Flag to determine if object must be embedded in project.
        secret_value : str
            Value of the secret.
        **kwargs : dict
            Spec keyword arguments.

        Returns
        -------
        Secret
            An instance of the created secret.
        """
        obj = new_secret(
            project=self.name,
            name=name,
            kind="secret",
            uuid=uuid,
            description=description,
            git_source=git_source,
            labels=labels,
            embedded=embedded,
            secret_value=secret_value,
            **kwargs,
        )
        self.refresh()
        return obj

    def get_secret(
        self,
        identifier: str,
        entity_id: str | None = None,
        **kwargs,
    ) -> Secret:
        """
        Get object from backend.

        Parameters
        ----------
        identifier : str
            Entity key or name.
        project : str
            Project name.
        entity_id : str
            Entity ID.
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        Secret
            Instance of Secret class.
        """
        obj = get_secret(
            identifier=identifier,
            project=self.name,
            entity_id=entity_id,
            **kwargs,
        )
        self.refresh()
        return obj

    def delete_secret(
        self,
        identifier: str,
        entity_id: str | None = None,
        delete_all_versions: bool = False,
        **kwargs,
    ) -> None:
        """
        Delete a Secret from project.

        Parameters
        ----------
        identifier : str
            Entity key or name.
        project : str
            Project name.
        entity_id : str
            Entity ID.
        delete_all_versions : bool
            Delete all versions of the named entity.
            Use entity name instead of entity key as identifier.
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        None
        """
        delete_secret(
            identifier=identifier,
            project=self.name,
            entity_id=entity_id,
            delete_all_versions=delete_all_versions,
            **kwargs,
        )
        self.refresh()

    def list_secrets(self, **kwargs) -> list[dict]:
        """
        List secrets associated with the project.

        Parameters
        ----------
        **kwargs : dict
            Parameters to pass to the API call.

        Returns
        -------
        list[dict]
            List of objects related to project.
        """
        return list_secrets(self.name, **kwargs)

    #############################
    #  Static interface methods
    #############################

    @staticmethod
    def _parse_dict(obj: dict, validate: bool = True) -> dict:
        """
        Get dictionary and parse it to a valid entity dictionary.

        Parameters
        ----------
        entity : str
            Entity type.
        obj : dict
            Dictionary to parse.

        Returns
        -------
        dict
            A dictionary containing the attributes of the entity instance.
        """
        name = build_name(obj.get("name"))
        kind = obj.get("kind")
        metadata = build_metadata(kind, **obj.get("metadata", {}))
        spec = build_spec(kind, validate=validate, **obj.get("spec", {}))
        status = build_status(kind, **obj.get("status", {}))
        user = obj.get("user")
        local = obj.get("local", False)
        return {
            "name": name,
            "kind": kind,
            "metadata": metadata,
            "spec": spec,
            "status": status,
            "user": user,
            "local": local,
        }


def project_from_parameters(
    name: str,
    kind: str,
    description: str | None = None,
    git_source: str | None = None,
    labels: list[str] | None = None,
    local: bool = False,
    context: str | None = None,
    **kwargs,
) -> Project:
    """
    Create project.

    Parameters
    ----------
    name : str
        Object name.
    kind : str
        Kind the object.
    description : str
        Description of the object (human readable).
    git_source : str
        Remote git source for object.
    labels : list[str]
        List of labels.
    local : bool
        Flag to determine if object will be exported to backend.
    context : str
        The context of the project.
    **kwargs : dict
        Spec keyword arguments.

    Returns
    -------
    Project
        Project object.
    """
    name = build_name(name)
    spec = build_spec(
        kind,
        context=context,
        **kwargs,
    )
    metadata = build_metadata(
        kind,
        project=name,
        name=name,
        description=description,
        labels=labels,
        source=git_source,
    )
    status = build_status(kind)
    return Project(
        name=name,
        kind=kind,
        metadata=metadata,
        spec=spec,
        status=status,
        local=local,
    )


def project_from_dict(obj: dict) -> Project:
    """
    Create project from dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create object from.

    Returns
    -------
    Project
        Project object.
    """
    return Project.from_dict(obj)
