from __future__ import annotations

from digitalhub_core.entities.entity_types import EntityTypes
from digitalhub_core.registry.registry import registry
from digitalhub_core.registry.utils import create_info

# Root module
root = "digitalhub_core.entities"

# Projects
entity_type = EntityTypes.PROJECTS.value
prefix = entity_type.removesuffix("s").capitalize()
project_info = create_info(root, entity_type, prefix)
registry.register("project", project_info)


# Secrets
entity_type = EntityTypes.SECRETS.value
prefix = entity_type.removesuffix("s").capitalize()
secret_info = create_info(root, entity_type, prefix)
registry.register("secret", secret_info)


# Artifacts
entity_type = EntityTypes.ARTIFACTS.value
for i in ["artifact"]:
    prefix = entity_type.removesuffix("s").capitalize()
    suffix = i.capitalize()
    artifact_info = create_info(root, entity_type, prefix, suffix)
    registry.register(i, artifact_info)
