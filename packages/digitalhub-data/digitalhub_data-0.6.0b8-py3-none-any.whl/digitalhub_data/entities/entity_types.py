from __future__ import annotations

from enum import Enum


class EntityTypes(Enum):
    """
    Entity types.
    """

    # Must redefine all entity types, no
    # inheritance on enums

    PROJECTS = "projects"
    ARTIFACTS = "artifacts"
    SECRETS = "secrets"
    SERVICES = "services"
    FUNCTIONS = "functions"
    WORKFLOWS = "workflows"
    TASKS = "tasks"
    RUNS = "runs"
    DATAITEMS = "dataitems"
