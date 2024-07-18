from __future__ import annotations

import importlib
import importlib.metadata
import pkgutil
import re
from types import ModuleType


def import_module(package: str) -> ModuleType:
    """
    Import modules from package name.

    Parameters
    ----------
    package : str
        Package name.

    Returns
    -------
    ModuleType
        Module.
    """
    try:
        return importlib.import_module(package)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"Package {package} not found.")
    except Exception as e:
        raise e


def import_class(module_to_import: str, class_name: str) -> type:
    """
    Import class from implemented module.

    Parameters
    ----------
    module_to_import : str
        Module name.
    class_name : str
        Class name.

    Returns
    -------
    type
        Class.
    """
    module = import_module(module_to_import)
    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ModuleNotFoundError(f"Module {module_to_import} has no '{class_name}' class.")


def list_runtimes() -> list[str]:
    """
    List installed runtimes for digitalhub.

    Returns
    -------
    list
        List of installed runtimes names.
    """
    pattern = r"digitalhub_runtime_.*"
    runtimes = []
    try:
        for _, name, _ in pkgutil.iter_modules():
            if re.match(pattern, name):
                runtimes.append(name)
        return runtimes
    except Exception:
        raise RuntimeError("Error listing installed runtimes.")


def register_runtimes_entities() -> None:
    """
    Register runtimes and related entities into registry.

    Returns
    -------
    None
    """
    for package in list_runtimes():
        import_module(package)


def register_layer_entities() -> None:
    """
    Register layer and related entities into registry.

    Returns
    -------
    None
    """
    for layer in ["core", "data", "ml", "ai"]:
        # Check if package exists
        package = f"digitalhub_{layer}"
        try:
            importlib.metadata.distribution(package)
        except importlib.metadata.PackageNotFoundError:
            # Return because the layers are pyramidal from
            # core to ai
            return

        # Try ot import registry from entities.registries module
        try:
            import_module(f"{package}.entities.registries")
        except Exception:
            pass


def create_info(
    root: str,
    entity_type: str,
    prefix: str,
    suffix: str | None = "",
    runtime_info: dict | None = None,
) -> dict:
    """
    Create entity info.

    Parameters
    ----------
    root : str
        Root module.
    entity_type : str
        Entity type.
    prefix : str
        Entity prefix.
    suffix : str
        Entity suffix.
    runtime_info : dict
        Runtime info.

    Returns
    -------
    dict
        Entity info.
    """
    dict_ = {
        "entity_type": entity_type,
        "spec": {
            "module": f"{root}.{entity_type}.spec",
            "class_name": f"{prefix}Spec{suffix}",
            "parameters_validator": f"{prefix}Params{suffix}",
        },
        "status": {
            "module": f"{root}.{entity_type}.status",
            "class_name": f"{prefix}Status{suffix}",
        },
        "metadata": {
            "module": "digitalhub_core.entities._base.metadata",
            "class_name": "Metadata",
        },
    }
    # Add runtime only if provided
    # (in functions, tasks, runs and workflows)
    if runtime_info is not None:
        dict_["runtime"] = runtime_info
    return dict_
