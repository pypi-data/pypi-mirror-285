from __future__ import annotations

import typing
from typing import Any

from digitalhub_data.readers.registry import REGISTRY

if typing.TYPE_CHECKING:
    from digitalhub_data.readers.objects.base import DataframeReader


def get_reader_by_engine(engine: str) -> DataframeReader:
    """
    Get Dataframe reader.

    Parameters
    ----------
    engine : str
        Dataframe engine (pandas, polars, etc.).

    Returns
    -------
    DataframeReader
        Reader object.
    """
    try:
        return REGISTRY[engine]()
    except KeyError:
        raise ValueError(f"Unsupported dataframe engine: {engine}. Make sure it is installed.")


def get_reader_by_object(obj: Any) -> DataframeReader:
    """
    Get Dataframe reader by object.

    Parameters
    ----------
    obj : Any
        Object to get reader from.

    Returns
    -------
    DataframeReader
        Reader object.
    """
    try:
        obj_name = f"{obj.__class__.__module__}.{obj.__class__.__name__}"
        return get_reader_by_engine(obj_name)
    except KeyError:
        raise ValueError(f"Unsupported dataframe type: {obj}. Make sure it is installed.")
