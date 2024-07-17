from __future__ import annotations

import typing

from digitalhub_core.context.builder import get_context
from digitalhub_core.entities._base.crud import (
    create_entity_api_ctx,
    list_entity_api_ctx,
    read_entity_api_ctx,
    update_entity_api_ctx,
)
from digitalhub_core.entities._base.entity import Entity
from digitalhub_core.entities._builders.metadata import build_metadata
from digitalhub_core.entities._builders.name import build_name
from digitalhub_core.entities._builders.spec import build_spec
from digitalhub_core.entities._builders.status import build_status
from digitalhub_core.entities._builders.uuid import build_uuid
from digitalhub_core.entities.entity_types import EntityTypes
from digitalhub_core.entities.tasks.crud import create_task, create_task_from_dict, delete_task
from digitalhub_core.runtimes.builder import get_kind_registry
from digitalhub_core.utils.exceptions import BackendError, EntityError
from digitalhub_core.utils.generic_utils import get_timestamp
from digitalhub_core.utils.io_utils import write_yaml

if typing.TYPE_CHECKING:
    from digitalhub_core.context.context import Context
    from digitalhub_core.entities._base.metadata import Metadata
    from digitalhub_core.entities.runs.entity import Run
    from digitalhub_core.entities.tasks.entity import Task
    from digitalhub_core.entities.workflows.spec import WorkflowSpec
    from digitalhub_core.entities.workflows.status import WorkflowStatus


class Workflow(Entity):
    """
    A class representing a workflow.
    """

    ENTITY_TYPE = EntityTypes.WORKFLOWS.value

    def __init__(
        self,
        project: str,
        name: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: WorkflowSpec,
        status: WorkflowStatus,
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
        spec : WorkflowSpec
            Specification of the object.
        status : WorkflowStatus
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

        # Initialize tasks
        self._tasks: dict[str, Task] = {}

    #############################
    #  Save / Refresh / Export
    #############################

    def save(self, update: bool = False) -> Workflow:
        """
        Save entity into backend.

        Parameters
        ----------
        update : bool
            Flag to indicate update.

        Returns
        -------
        Workflow
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

    def refresh(self) -> Workflow:
        """
        Refresh object from backend.

        Returns
        -------
        Workflow
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

        # Embed tasks in file
        if self._tasks:
            obj = [obj] + [v.to_dict() for _, v in self._tasks.items()]

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
    #  Workflow Methods
    #############################

    def run(self, **kwargs) -> Run:
        """
        Run workflow.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments passed to Task and Run builders.

        Returns
        -------
        Run
            Run instance.
        """

        # Get kind registry
        kind_reg = get_kind_registry(self.kind)

        # Get task and run kind
        task_kind = kind_reg.get_task_kind_from_action(action="pipeline")
        run_kind = kind_reg.get_run_kind()

        # Create or update new task
        task = self.new_task(task_kind, **kwargs)

        # Raise error if execution is not done by DHCore backend
        if self._context().local:
            raise BackendError("Cannot run workflow with local backend.")

        return task.run(run_kind, local_execution=False, **kwargs)

    #############################
    #  Helpers
    #############################

    def _get_workflow_string(self) -> str:
        """
        Get workflow string.

        Returns
        -------
        str
            Workflow string.
        """
        return f"{self.kind}://{self.project}/{self.name}:{self.id}"

    def import_tasks(self, tasks: list[dict]) -> None:
        """
        Import tasks from yaml.

        Parameters
        ----------
        tasks : list[dict]
            List of tasks to import.

        Returns
        -------
        None
        """
        # Loop over tasks list, in the case where the function
        # is imported from local file.
        for task in tasks:
            # If task is not a dictionary, skip it
            if not isinstance(task, dict):
                continue

            # Create the object instance from dictionary,
            # the form in which tasks are stored in function
            # status
            task_obj = create_task_from_dict(task)

            # Try to save it in backend to been able to use
            # it for launching runs. In fact, tasks must be
            # persisted in backend to be able to launch runs.
            # Ignore if task already exists
            try:
                task_obj.save()
            except BackendError:
                pass

            # Set task if function is the same. Overwrite
            # status task dict with the new task object
            if task_obj.spec.function == self._get_workflow_string():
                self._tasks[task_obj.kind] = task_obj

    def new_task(self, task_kind: str, **kwargs) -> Task:
        """
        Create new task.

        Parameters
        ----------
        task_kind : str
            Kind the object.
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        Task
            New task.
        """
        # Override kwargs
        kwargs["project"] = self.project
        kwargs["function"] = self._get_workflow_string()
        kwargs["kind"] = task_kind

        # Create object instance
        task = create_task(**kwargs)

        exists, task_id = self._check_task_in_backend(task_kind)

        # Save or update task
        if not exists:
            task.save()
        else:
            task.id = task_id
            task.save(update=True)

        self._tasks[task_kind] = task
        return task

    def update_task(self, kind: str, **kwargs) -> None:
        """
        Update task.

        Parameters
        ----------
        kind : str
            Kind the object.
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        None

        Raises
        ------
        EntityError
            If task does not exist.
        """
        self._raise_if_not_exists(kind)

        # Update kwargs
        kwargs["project"] = self.project
        kwargs["kind"] = kind
        kwargs["function"] = self._get_workflow_string()
        kwargs["uuid"] = self._tasks[kind].id

        # Update task
        task = create_task(**kwargs)
        task.save(update=True)
        self._tasks[kind] = task

    def get_task(self, kind: str) -> Task:
        """
        Get task.

        Parameters
        ----------
        kind : str
            Kind the object.

        Returns
        -------
        Task
            Task.

        Raises
        ------
        EntityError
            If task is not created.
        """
        self._raise_if_not_exists(kind)
        return self._tasks[kind]

    def delete_task(self, kind: str, cascade: bool = True) -> None:
        """
        Delete task.

        Parameters
        ----------
        kind : str
            Kind the object.
        cascade : bool
            Flag to determine if cascade deletion must be performed.

        Returns
        -------
        None

        Raises
        ------
        EntityError
            If task is not created.
        """
        self._raise_if_not_exists(kind)
        delete_task(self._tasks[kind].key, cascade=cascade)
        self._tasks.pop(kind, None)

    def _check_task_in_backend(self, kind: str) -> tuple[bool, str | None]:
        """
        Check if task exists in backend.

        Parameters
        ----------
        kind : str
            Kind the object.

        Returns
        -------
        tuple[bool, str | None]
            Flag to determine if task exists in backend and ID if exists.
        """
        # List tasks from backend filtered by function and kind
        params = {"function": self._get_workflow_string(), "kind": kind}
        objs = list_entity_api_ctx(self.project, EntityTypes.TASKS.value, params=params)
        try:
            return True, objs[0]["id"]
        except IndexError:
            return False, None

    def _raise_if_not_exists(self, kind: str) -> None:
        """
        Raise error if task is not created.

        Parameters
        ----------
        kind : str
            Kind the object.

        Returns
        -------
        None

        Raises
        ------
        EntityError
            If task does not exist.
        """
        if self._tasks.get(kind) is None:
            raise EntityError("Task does not exist.")

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
        validate : bool
            Flag to determine if validation must be performed.

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


def workflow_from_parameters(
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
    Workflow
        An instance of the created workflow.
    """
    name = build_name(name)
    uuid = build_uuid(uuid)
    spec = build_spec(
        kind,
        **kwargs,
    )
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
    status = build_status(
        kind,
    )
    return Workflow(
        project=project,
        name=name,
        uuid=uuid,
        kind=kind,
        metadata=metadata,
        spec=spec,
        status=status,
    )


def workflow_from_dict(obj: dict) -> Workflow:
    """
    Create Workflow instance from a dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create object from.

    Returns
    -------
    Workflow
        Workflow instance.
    """
    return Workflow.from_dict(obj)


def kind_to_runtime(kind: str) -> str:
    """
    Get the framework runtime from the workflow kind.

    Parameters
    ----------
    kind : str
        Kind the object.

    Returns
    -------
    str
        Framework runtime.
    """
    # Extract the framework runtime from the workflow kind
    # Currently the assumption is htat kind is equal to framework
    return kind
