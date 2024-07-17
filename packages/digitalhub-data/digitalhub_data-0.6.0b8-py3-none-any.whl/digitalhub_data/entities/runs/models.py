from __future__ import annotations

from digitalhub_core.entities.runs.models import EntityInputsOutputs


class EntityInputsOutputsData(EntityInputsOutputs):
    """
    Inputs/outputs model for runs.
    """

    dataitems: list[str, dict] = None
    """List of dataitem names, keys or objects."""
