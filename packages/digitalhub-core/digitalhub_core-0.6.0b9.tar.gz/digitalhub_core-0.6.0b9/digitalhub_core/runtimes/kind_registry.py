from __future__ import annotations

from digitalhub_core.utils.exceptions import EntityError
from pydantic import BaseModel


class TaskModel(BaseModel):
    """
    Task model.
    """

    kind: str
    action: str


class RunModel(BaseModel):
    """
    Run model.
    """

    kind: str


class ExecutableModel(BaseModel):
    """
    Executable model.
    """

    kind: str


class DataModel(BaseModel):
    """
    Data model.
    """

    executable: ExecutableModel
    task: list[TaskModel]
    run: RunModel


class KindRegistry:

    """
    Kind registry module for runtimes.
    """

    def __init__(self, data: dict[str, dict[str, str]]) -> None:
        """
        Constructor.

        Parameters
        ----------
        data : dict[str, dict[str, str]]
            Data to validate.

        Examples
        --------
        >>> data = {
        ...     "executable": {
        ...         "kind": "executable-kind"
        ...     },
        ...     "run": {
        ...         "kind": "run-kind"
        ...     },
        ...     "task": [
        ...         {"kind": "task-kind-0", "action": "action-0"},
        ...         {"kind": "task-kind-1", "action": "action-1"},
        ...         {"kind": "task-kind-2", "action": "action-2"},
        ...     ]
        ... }
        """
        validated_data = self._validate_data(data)
        self.data = validated_data

    def _validate_data(self, data: dict[str, dict[str, str]]) -> DataModel:
        """
        Validate data.

        Parameters
        ----------
        data : dict[str, dict[str, str]]
            Data to validate.

        Raises
        ------
        EntityError
            If data is not valid.
        """
        try:
            return DataModel(**data)
        except Exception as e:
            raise EntityError("Invalid data.") from e

    def get_task_kind_from_action(self, action: str) -> str:
        """
        Get task kind from action.

        Parameters
        ----------
        action : str
            Task action.

        Returns
        -------
        str
            Task kind.

        Raises
        ------
        EntityError
            If action is not allowed.
        """
        try:
            for task in self.data.task:
                if task.action == action:
                    return task.kind
        except StopIteration:
            msg = f"Action {action} not allowed."
            raise EntityError(msg)

    def get_action_from_task_kind(self, kind: str) -> str:
        """
        Get action from task.

        Parameters
        ----------
        kind : str
            Task kind.

        Returns
        -------
        str
            Action.

        Raises
        ------
        EntityError
            If task is not allowed.
        """
        try:
            for task in self.data.task:
                if task.kind == kind:
                    return task.action
        except StopIteration:
            msg = f"Task {kind} not allowed."
            raise EntityError(msg)

    def get_run_kind(self) -> str:
        """
        Get run kind.

        Returns
        -------
        str
            Run kind.
        """
        return self.data.run.kind

    def get_executable_kind(self) -> str:
        """
        Get executable kind.

        Returns
        -------
        str
            Executable kind.
        """
        return self.data.executable.kind
