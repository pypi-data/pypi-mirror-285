from __future__ import annotations

import typing
from abc import abstractmethod
from typing import Any, Callable

from digitalhub_core.utils.exceptions import EntityError
from digitalhub_core.utils.logger import LOGGER

if typing.TYPE_CHECKING:
    from digitalhub_core.runtimes.kind_registry import KindRegistry


class Runtime:
    """
    Base Runtime class.

    Runtimes are the entities responsible for the actual execution
    of a given run. They are highly specialized components which
    can translate the representation of a given execution as expressed
    in the run into an actual execution operation performed via
    libraries, code, external tools etc.
    """

    def __init__(self, kind_registry: KindRegistry, project: str) -> None:
        self.kind_registry = kind_registry
        self.project = project

    @abstractmethod
    def build(self, executable: dict, task: dict, run: dict) -> dict:
        """
        Build run spec.
        """

    @abstractmethod
    def run(self, run: dict) -> dict:
        """
        Execute run task.
        """

    @staticmethod
    @abstractmethod
    def _get_executable(action: str) -> Callable:
        """
        Get executable from action.
        """

    ##################################
    # Private methods
    ##################################

    def _validate_task(self, run: dict) -> str:
        """
        Check if task is allowed. This presumes that the
        runtime holds a list of allowed actions in the self.allowed_actions
        attribute.

        Parameters
        ----------
        run : dict
            Run object dictionary.

        Returns
        -------
        str
            Action to execute.
        """
        try:
            task_kind = run["spec"]["task"].split(":")[0]
        except (KeyError, IndexError):
            msg = "Malformed run spec."
            LOGGER.exception(msg)
            raise RuntimeError(msg)

        try:
            return self.get_action_from_task_kind(task_kind)
        except EntityError:
            msg = f"Task {task_kind} not allowed."
            LOGGER.exception(msg)
            raise RuntimeError(msg)

    @staticmethod
    def _execute(func: Callable, *args, **kwargs) -> Any:
        """
        Execute function.

        Parameters
        ----------
        func : Callable
            Function to execute.
        *args
            Function arguments.
        **kwargs : dict
            Function keyword arguments.

        Returns
        -------
        Any
            Function result.
        """
        try:
            return func(*args, **kwargs)
        except Exception:
            msg = "Something got wrong during function execution."
            LOGGER.exception(msg)
            raise RuntimeError(msg)

    ##################################
    # Wrapper registry methods
    ##################################

    def get_executable_kind(self) -> str:
        """
        Get executable kind.

        Returns
        -------
        str
            Executable kind.
        """
        return self.kind_registry.get_executable_kind()

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
        """
        return self.kind_registry.get_task_kind_from_action(action)

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
        """
        return self.kind_registry.get_action_from_task_kind(kind)

    def get_run_kind(self) -> str:
        """
        Get run kind.

        Returns
        -------
        str
            Run kind.
        """
        return self.kind_registry.get_run_kind()
