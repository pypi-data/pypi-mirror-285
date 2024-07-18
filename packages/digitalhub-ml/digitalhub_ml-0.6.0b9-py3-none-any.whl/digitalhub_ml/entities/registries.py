from __future__ import annotations

from digitalhub_core.registry.registry import registry
from digitalhub_core.registry.utils import create_info
from digitalhub_ml.entities.entity_types import EntityTypes

root = "digitalhub_ml.entities"

# Projects ovverride
entity_type = EntityTypes.PROJECTS.value
registry.project.spec.module = f"{root}.{entity_type}.spec"
registry.project.spec.class_name = "ProjectSpecMl"
registry.project.spec.parameters_validator = "ProjectParamsMl"

# Models
entity_type = EntityTypes.MODELS.value
for i in ["model"]:
    prefix = entity_type.removesuffix("s").capitalize()
    suffix = i.capitalize()
    model_info = create_info(root, entity_type, prefix, suffix)
    registry.register(i, model_info)
