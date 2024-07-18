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
from digitalhub_core.entities.entity_types import EntityTypes
from digitalhub_core.entities.workflows.entity import workflow_from_dict, workflow_from_parameters
from digitalhub_core.utils.io_utils import read_yaml

if typing.TYPE_CHECKING:
    from digitalhub_core.entities.workflows.entity import Workflow


ENTITY_TYPE = EntityTypes.WORKFLOWS.value


def create_workflow(**kwargs) -> Workflow:
    """
    Create a new Workflow instance with the specified parameters.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments.

    Returns
    -------
    Workflow
        An instance of the created workflow.
    """
    return workflow_from_parameters(**kwargs)


def create_workflow_from_dict(obj: dict) -> Workflow:
    """
    Create a new Workflow instance from a dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create object from.

    Returns
    -------
    Workflow
        Workflow object.
    """
    check_context(obj.get("project"))
    return workflow_from_dict(obj)


def new_workflow(
    project: str,
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
    obj = create_workflow(
        project=project,
        name=name,
        kind=kind,
        uuid=uuid,
        description=description,
        git_source=git_source,
        labels=labels,
        embedded=embedded,
        **kwargs,
    )
    obj.save()
    return obj


def get_workflow(
    identifier: str,
    project: str | None = None,
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
        Object instance.
    """
    obj = read_entity_api_ctx(
        identifier,
        ENTITY_TYPE,
        project=project,
        entity_id=entity_id,
        **kwargs,
    )
    return workflow_from_dict(obj)


def get_workflow_versions(
    identifier: str,
    project: str | None = None,
    **kwargs,
) -> list[Workflow]:
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
    list[Workflow]
        List of object instances.
    """
    obj = read_entity_api_ctx_versions(
        identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        **kwargs,
    )
    return [workflow_from_dict(o) for o in obj]


def import_workflow(file: str) -> Workflow:
    """
    Import an Workflow object from a file using the specified file path.

    Parameters
    ----------
    file : str
        Path to the file.

    Returns
    -------
    Workflow
        Object instance.
    """
    obj: dict = read_yaml(file)
    if isinstance(obj, list):
        wf_dict = obj[0]
        task_dicts = obj[1:]
    else:
        wf_dict = obj
        task_dicts = []

    check_context(obj.get("project"))
    workflow = create_workflow_from_dict(wf_dict)
    workflow.import_tasks(task_dicts)
    return workflow


def delete_workflow(
    identifier: str,
    project: str | None = None,
    entity_id: str | None = None,
    delete_all_versions: bool = False,
    cascade: bool = True,
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
    cascade : bool
        Cascade delete.
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
        cascade=cascade,
        **kwargs,
    )


def update_workflow(entity: Workflow, **kwargs) -> Workflow:
    """
    Update object in backend.

    Parameters
    ----------
    entity : Workflow
        The object to update.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    Workflow
        Entity updated.
    """
    obj = update_entity_api_ctx(
        project=entity.project,
        entity_type=ENTITY_TYPE,
        entity_id=entity.id,
        entity_dict=entity.to_dict(),
        **kwargs,
    )
    return workflow_from_dict(obj)


def list_workflows(project: str, **kwargs) -> list[Workflow]:
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
    list[Workflow]
        List of workflows.
    """
    objs = list_entity_api_ctx(
        project=project,
        entity_type=ENTITY_TYPE,
        **kwargs,
    )
    return [workflow_from_dict(obj) for obj in objs]
