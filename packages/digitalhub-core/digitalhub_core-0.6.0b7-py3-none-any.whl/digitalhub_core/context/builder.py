from __future__ import annotations

import typing

from digitalhub_core.context.context import Context

if typing.TYPE_CHECKING:
    from digitalhub_core.entities.projects.entity import Project


class ContextBuilder:
    """
    ContextBuilder class.
    It implements the builder pattern to create a context instance.
    It allows to use multiple projects as context at the same time
    by adding them to the _instances registry with their name.
    """

    def __init__(self) -> None:
        self._instances: dict[str, Context] = {}

    def build(self, project_object: Project) -> None:
        """
        Add a project as context.

        Parameters
        ----------
        project_object : Project
            The project to add.

        Returns
        -------
        None
        """
        self._instances[project_object.name] = Context(project_object)

    def get(self, project: str) -> Context:
        """
        Get a context from project name if it exists.

        Parameters
        ----------
        project : str
            The project name.

        Returns
        -------
        Context
            The project context.

        Raises
        ------
        ValueError
            If the project is not in the context.
        """
        ctx = self._instances.get(project)
        if ctx is None:
            raise ValueError(
                f"Context '{project}' not found. Please get or create a project named '{project}' to access its objects."
            )
        return ctx

    def remove(self, project: str) -> None:
        """
        Remove a project from the context.

        Parameters
        ----------
        project : str
            The project name.

        Returns
        -------
        None
        """
        self._instances.pop(project, None)

    def set(self, context: Context) -> None:
        """
        Set the context.

        Parameters
        ----------
        context : Context
            The context to set.

        Returns
        -------
        None
        """
        self._instances[context.name] = context


def set_context(project: Project) -> None:
    """
    Wrapper for ContextBuilder.build().

    Parameters
    ----------
    project : Project
        The project object used to set the current context.

    Returns
    -------
    None
    """
    context_builder.build(project)


def set_context_object(context: Context) -> None:
    """
    Wrapper for ContextBuilder.set().

    Parameters
    ----------
    context : Context
        The context to set.

    Returns
    -------
    None
    """
    context_builder.set(context)


def get_context(project: str) -> Context:
    """
    Wrapper for ContextBuilder.get().

    Parameters
    ----------
    project : str
        Project name.

    Returns
    -------
    Context
        The context for the given project name.
    """
    return context_builder.get(project)


def delete_context(project: str) -> None:
    """
    Wrapper for ContextBuilder.remove().

    Parameters
    ----------
    project : str
        Project name.

    Returns
    -------
    None
    """
    context_builder.remove(project)


def check_context(project: str) -> None:
    """
    Check if the given project is in the context.

    Parameters
    ----------
    project : str
        Project name.

    Returns
    -------
    bool
        True if the project is in the context, False otherwise.
    """
    if project not in context_builder._instances:
        msg = f"Context missing. Set context by creating or importing a project named '{project}'."
        raise RuntimeError(msg)


context_builder = ContextBuilder()
