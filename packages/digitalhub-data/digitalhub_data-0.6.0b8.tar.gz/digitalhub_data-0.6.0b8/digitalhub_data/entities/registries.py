from __future__ import annotations

from digitalhub_core.registry.registry import registry
from digitalhub_core.registry.utils import create_info
from digitalhub_data.entities.entity_types import EntityTypes

root = "digitalhub_data.entities"

# Projects ovverride
entity_type = EntityTypes.PROJECTS.value
registry.project.spec.module = f"{root}.{entity_type}.spec"
registry.project.spec.class_name = "ProjectSpecData"
registry.project.spec.parameters_validator = "ProjectParamsData"

# Dataitems
entity_type = EntityTypes.DATAITEMS.value
for i in ["dataitem", "table", "iceberg"]:
    prefix = entity_type.removesuffix("s").capitalize()
    suffix = i.capitalize()
    dataitem_info = create_info(root, entity_type, prefix, suffix)
    registry.register(i, dataitem_info)
