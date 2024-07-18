from __future__ import annotations

import typing

from digitalhub_core.context.builder import check_context
from digitalhub_core.entities._base.crud import (
    delete_entity_api_ctx,
    list_entity_api_ctx,
    read_entity_api_ctx,
    read_entity_api_ctx_versions,
    update_entity_api_ctx,
)
from digitalhub_core.entities._builders.uuid import build_uuid
from digitalhub_core.entities.artifacts.entity import artifact_from_dict, artifact_from_parameters
from digitalhub_core.entities.entity_types import EntityTypes
from digitalhub_core.utils.env_utils import get_s3_bucket
from digitalhub_core.utils.file_utils import get_file_name
from digitalhub_core.utils.io_utils import read_yaml

if typing.TYPE_CHECKING:
    from digitalhub_core.entities.artifacts.entity import Artifact


ENTITY_TYPE = EntityTypes.ARTIFACTS.value


def create_artifact(**kwargs) -> Artifact:
    """
    Create a new artifact with the provided parameters.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments.

    Returns
    -------
    Artifact
        Object instance.
    """
    return artifact_from_parameters(**kwargs)


def create_artifact_from_dict(obj: dict) -> Artifact:
    """
    Create a new Artifact instance from a dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create object from.

    Returns
    -------
    Artifact
        Artifact object.
    """
    check_context(obj.get("project"))
    return artifact_from_dict(obj)


def new_artifact(
    project: str,
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
    project : str
        Project name.
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
    obj = create_artifact(
        project=project,
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
    obj.save()
    return obj


def get_artifact(
    identifier: str,
    project: str | None = None,
    entity_id: str | None = None,
    **kwargs,
) -> Artifact:
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
    Artifact
        Object instance.
    """
    obj = read_entity_api_ctx(
        identifier,
        ENTITY_TYPE,
        project=project,
        entity_id=entity_id,
        **kwargs,
    )
    return artifact_from_dict(obj)


def get_artifact_versions(
    identifier: str,
    project: str | None = None,
    **kwargs,
) -> list[Artifact]:
    """
    Get object versions from backend.

    Parameters
    ----------
    identifier : str
        Entity key or name.
    project : str
        Project name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    list[Artifact]
        List of object instances.
    """
    obj = read_entity_api_ctx_versions(
        identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        **kwargs,
    )
    return [artifact_from_dict(o) for o in obj]


def import_artifact(file: str) -> Artifact:
    """
    Import an Artifact object from a file using the specified file path.

    Parameters
    ----------
    file : str
        Path to the file.

    Returns
    -------
    Artifact
        Object instance.
    """
    obj: dict = read_yaml(file)
    return create_artifact_from_dict(obj)


def delete_artifact(
    identifier: str,
    project: str | None = None,
    entity_id: str | None = None,
    delete_all_versions: bool = False,
    **kwargs,
) -> dict:
    """
    Delete object from backend.

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
    dict
        Response from backend.
    """
    return delete_entity_api_ctx(
        identifier=identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        entity_id=entity_id,
        delete_all_versions=delete_all_versions,
        **kwargs,
    )


def update_artifact(entity: Artifact, **kwargs) -> Artifact:
    """
    Update object in backend.

    Parameters
    ----------
    entity : Artifact
        The object to update.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    Artifact
        Entity updated.
    """
    obj = update_entity_api_ctx(
        project=entity.project,
        entity_type=ENTITY_TYPE,
        entity_id=entity.id,
        entity_dict=entity.to_dict(),
        **kwargs,
    )
    return artifact_from_dict(obj)


def list_artifacts(project: str, **kwargs) -> list[Artifact]:
    """
    List all objects from backend.

    Parameters
    ----------
    project : str
        Project name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    list[Artifact]
        List of artifacts.
    """
    objs = list_entity_api_ctx(
        project=project,
        entity_type=ENTITY_TYPE,
        **kwargs,
    )
    return [artifact_from_dict(obj) for obj in objs]


def log_artifact(
    project: str,
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
    project : str
        Project name.
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
    if path is None:
        if source_path is None:
            raise Exception("Either path or source_path must be provided.")

        # Build path if not provided from source filename
        filename = get_file_name(source_path)
        uuid = build_uuid()
        kwargs["uuid"] = uuid
        path = f"s3://{get_s3_bucket()}/{project}/{ENTITY_TYPE}/{name}/{uuid}/{filename}"

    obj = new_artifact(project=project, name=name, kind=kind, path=path, **kwargs)
    obj.upload(source_path)
    return obj
