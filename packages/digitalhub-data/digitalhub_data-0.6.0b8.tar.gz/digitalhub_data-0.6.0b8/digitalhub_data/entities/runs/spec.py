from __future__ import annotations

from digitalhub_core.entities.runs.spec import ENTITY_FUNC, RunParams, RunSpec
from digitalhub_data.entities.dataitems.crud import get_dataitem

ENTITY_FUNC["dataitems"] = get_dataitem


class RunSpecData(RunSpec):
    """Run specification."""


class RunParamsData(RunParams):
    """
    Run parameters.
    """
