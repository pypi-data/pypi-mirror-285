from __future__ import annotations

API_BASE = "/api/v1"
API_CONTEXT = f"{API_BASE}/-"


####################
# Context APIs
####################


def api_ctx_list(project: str, entity_type: str) -> str:
    """
    List context API.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.

    Returns
    -------
    str
        The API string formatted.
    """
    return f"{API_CONTEXT}/{project}/{entity_type}"


def api_ctx_create(
    project: str,
    entity_type: str,
) -> str:
    """
    Create context API.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        The name of the entity_type.

    Returns
    -------
    str
        The API string formatted.
    """
    return f"{API_CONTEXT}/{project}/{entity_type}"


def api_ctx_read(project: str, entity_type: str, entity_id: str) -> str:
    """
    Read context API.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    entity_id : str
        Entity ID.

    Returns
    -------
    str
        The API string formatted.
    """
    return f"{API_CONTEXT}/{project}/{entity_type}/{entity_id}"


def api_ctx_update(
    project: str,
    entity_type: str,
    entity_id: str,
) -> str:
    """
    Update context API.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    entity_id : str
        Entity ID.

    Returns
    -------
    str
        The API string formatted.
    """
    return f"{API_CONTEXT}/{project}/{entity_type}/{entity_id}"


def api_ctx_delete(project: str, entity_type: str, entity_id: str) -> str:
    """
    Delete context API.

    Parameters
    ----------
    project : str
        Project name.
    entity_type : str
        Entity type.
    entity_id : str
        Entity ID.

    Returns
    -------
    str
        The API string formatted.
    """
    return f"{API_CONTEXT}/{project}/{entity_type}/{entity_id}"


####################
# Base APIs
####################


def api_base_list(entity_type: str) -> str:
    """
    List base API.

    Parameters
    ----------
    entity_type : str
        Entity type.

    Returns
    -------
    str
        The API string formatted.
    """
    return f"{API_BASE}/{entity_type}"


def api_base_create(entity_type: str) -> str:
    """
    Create base API.

    Parameters
    ----------
    entity_type : str
        Entity type.

    Returns
    -------
    str
        The API string formatted.
    """
    return f"{API_BASE}/{entity_type}"


def api_base_read(entity_type: str, entity_id: str) -> str:
    """
    Read base API.

    Parameters
    ----------
    entity_type : str
        Entity type.
    entity_id : str
        Entity ID.

    Returns
    -------
    str
        The API string formatted.
    """
    return f"{API_BASE}/{entity_type}/{entity_id}"


def api_base_update(entity_type: str, entity_id: str) -> str:
    """
    Update base API.

    Parameters
    ----------
    entity_type : str
        Entity type.
    entity_id : str
        Entity ID.

    Returns
    -------
    str
        The API string formatted.
    """
    return f"{API_BASE}/{entity_type}/{entity_id}"


def api_base_delete(entity_type: str, entity_id: str) -> str:
    """
    Delete base API.

    Parameters
    ----------
    entity_type : str
        Entity type.
    entity_id : str
        Entity ID.

    Returns
    -------
    str
        The API string formatted.
    """
    return f"{API_BASE}/{entity_type}/{entity_id}"
