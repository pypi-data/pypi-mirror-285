from __future__ import annotations

import typing

from digitalhub_core.context.builder import get_context
from digitalhub_core.entities._base.api import (
    api_base_create,
    api_base_delete,
    api_base_list,
    api_base_read,
    api_base_update,
    api_ctx_create,
    api_ctx_delete,
    api_ctx_list,
    api_ctx_read,
    api_ctx_update,
)
from digitalhub_core.entities.utils import parse_entity_key

if typing.TYPE_CHECKING:
    from digitalhub_core.client.objects.base import Client


def create_entity_api_base(
    client: Client,
    entity_type: str,
    entity_dict: dict,
    **kwargs,
) -> dict:
    """
    Create object in backend.

    Parameters
    ----------
    client : Client
        Client instance.
    entity_type : str
        Entity type.
    entity_dict : dict
        Object instance.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Object instance.
    """
    api = api_base_create(entity_type)
    return client.create_object(api, entity_dict, **kwargs)


def read_entity_api_base(
    client: Client,
    entity_type: str,
    entity_name: str,
    **kwargs,
) -> dict:
    """
    Read object from backend.

    Parameters
    ----------
    client : Client
        Client instance.
    entity_type : str
        Entity type.
    entity_name : str
        Entity name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Object instance.
    """
    api = api_base_read(entity_type, entity_name)
    return client.read_object(api, **kwargs)


def update_entity_api_base(
    client: Client,
    entity_type: str,
    entity_name: str,
    entity_dict: dict,
    **kwargs,
) -> dict:
    """
    Update object in backend.

    Parameters
    ----------
    client : Client
        Client instance.
    entity_type : str
        Entity type.
    entity_name : str
        Entity name.
    entity_dict : dict
        Object instance.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Object instance.
    """
    api = api_base_update(entity_type, entity_name)
    return client.update_object(api, entity_dict, **kwargs)


def delete_entity_api_base(
    client: Client,
    entity_type: str,
    entity_name: str,
    **kwargs,
) -> dict:
    """
    Delete object from backend.

    Parameters
    ----------
    client : Client
        Client instance.
    entity_type : str
        Entity type.
    entity_name : str
        Entity name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Object instance.
    """
    if "params" not in kwargs:
        kwargs["params"] = {}
    if "cascade" in kwargs["params"]:
        kwargs["params"]["cascade"] = str(kwargs["cascade"]).lower()
    api = api_base_delete(entity_type, entity_name)
    return client.delete_object(api, **kwargs)


def list_entity_api_base(
    client: Client,
    entity_type: str,
    **kwargs,
) -> list[dict]:
    """
    List objects from backend.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    list[dict]
        List of objects.
    """
    api = api_base_list(entity_type)
    return client.list_objects(api, **kwargs)


def create_entity_api_ctx(
    project: str,
    entity_type: str,
    entity_dict: dict,
    **kwargs,
) -> dict:
    """
    Create object in backend.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    entity_dict : dict
        Object instance.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Object instance.
    """
    api = api_ctx_create(project, entity_type)
    return get_context(project).create_object(api, entity_dict, **kwargs)


def read_entity_api_ctx(
    identifier: str,
    entity_type: str | None = None,
    project: str | None = None,
    entity_id: str | None = None,
    **kwargs,
) -> dict:
    """
    Get object from backend.

    Parameters
    ----------
    identifier : str
        Entity key or name.
    entity_type : str
        Entity type.
    project : str
        Project name.
    entity_id : str
        Entity ID.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Object instance.
    """

    if identifier.startswith("store://"):
        project, entity_type, _, _, entity_id = parse_entity_key(identifier)
        api = api_ctx_read(project, entity_type, entity_id)
        return get_context(project).read_object(api, **kwargs)

    if project is None or entity_type is None:
        raise ValueError("Project and entity type must be specified.")

    if "params" not in kwargs:
        kwargs["params"] = {}

    if entity_id is None:
        kwargs["params"]["name"] = identifier
        api = api_ctx_list(project, entity_type)
        return get_context(project).list_objects(api, **kwargs)[0]

    api = api_ctx_read(project, entity_type, entity_id)
    return get_context(project).read_object(api, **kwargs)


def update_entity_api_ctx(
    project: str,
    entity_type: str,
    entity_id: str,
    entity_dict: dict,
    **kwargs,
) -> dict:
    """
    Update object in backend.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    entity_id : str
        Entity ID.
    entity_dict : dict
        Entity dictionary.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.
    """
    api = api_ctx_update(project, entity_type, entity_id=entity_id)
    return get_context(project).update_object(api, entity_dict, **kwargs)


def delete_entity_api_ctx(
    identifier: str,
    entity_type: str,
    project: str | None = None,
    entity_id: str | None = None,
    **kwargs,
) -> dict:
    """
    Delete object from backend.

    Parameters
    ----------
    identifier : str
        Entity key or name.
    entity_type : str
        Entity type.
    project : str
        Project name.
    entity_id : str
        Entity ID.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.
    """
    if "params" not in kwargs:
        kwargs["params"] = {}
    if "cascade" in kwargs["params"]:
        kwargs["params"]["cascade"] = str(kwargs["cascade"]).lower()

    delete_all_versions: bool = kwargs.pop("delete_all_versions", False)

    if identifier.startswith("store://"):
        project, _, _, _, entity_id = parse_entity_key(identifier)
        api = api_ctx_delete(project, entity_type, entity_id)
        return get_context(project).delete_object(api, **kwargs)

    if project is None:
        raise ValueError("Project must be provided.")

    if entity_id is not None:
        api = api_ctx_delete(project, entity_type, entity_id)
    else:
        kwargs["params"]["name"] = identifier
        api = api_ctx_list(project, entity_type)
        if delete_all_versions:
            return get_context(project).delete_object(api, **kwargs)
        obj = get_context(project).list_objects(api, **kwargs)[0]
        entity_id = obj["id"]

    api = api_ctx_delete(project, entity_type, entity_id)
    return get_context(project).delete_object(api, **kwargs)


def list_entity_api_ctx(
    project: str,
    entity_type: str,
    **kwargs,
) -> list[dict]:
    """
    List objects from backend.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    list[dict]
        List of objects.
    """
    api = api_ctx_list(project, entity_type)
    return get_context(project).list_objects(api, **kwargs)


def set_data_api(
    project: str,
    entity_type: str,
    data: dict,
    **kwargs,
) -> None:
    """
    Set data in backend.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    data : dict
        Data dictionary.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.
    """
    api = api_ctx_list(project, entity_type) + "/data"
    get_context(project).update_object(api, data, **kwargs)


def get_data_api(
    project: str,
    entity_type: str,
    **kwargs,
) -> dict:
    """
    Read data from backend.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.
    """
    api = api_ctx_list(project, entity_type) + "/data"
    return get_context(project).read_object(api, **kwargs)


def logs_api(
    project: str,
    entity_type: str,
    entity_id: str,
    **kwargs,
) -> dict:
    """
    Read logs from backend.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    entity_id : str
        Entity ID.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.
    """
    api = api_ctx_read(project, entity_type, entity_id) + "/logs"
    return get_context(project).read_object(api)


def stop_api(
    project: str,
    entity_type: str,
    entity_id: str,
    **kwargs,
) -> None:
    """
    Stop object in backend.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    entity_id : str
        Entity ID.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.
    """
    api = api_ctx_create(project, entity_type) + f"/{entity_id}/stop"
    get_context(project).create_object(api)
