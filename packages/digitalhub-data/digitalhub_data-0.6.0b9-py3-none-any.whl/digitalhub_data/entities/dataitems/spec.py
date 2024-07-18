from __future__ import annotations

from digitalhub_core.entities._base.spec import Spec, SpecParams
from digitalhub_data.entities.dataitems.models import TableSchema
from pydantic import Field


class DataitemSpec(Spec):
    """
    Dataitem specifications.
    """

    def __init__(self, path: str) -> None:
        self.path = path


class DataitemParams(SpecParams):
    """
    Dataitem parameters.
    """

    path: str
    "The path of the dataitem."


class DataitemSpecDataitem(DataitemSpec):
    """
    Dataitem dataitem specifications.
    """


class DataitemParamsDataitem(DataitemParams):
    """
    Dataitem dataitem parameters.
    """


class DataitemSpecTable(DataitemSpec):
    """
    Dataitem table specifications.
    """

    def __init__(self, path: str, schema: dict | None = None) -> None:
        super().__init__(path)
        self.schema = schema


class DataitemParamsTable(DataitemParams):
    """
    Dataitem table parameters.
    """

    schema_: TableSchema = Field(default=None, alias="schema")
    """The schema of the dataitem in table schema format."""


class DataitemSpecIceberg(DataitemSpec):
    """
    Dataitem iceberg specifications.
    """


class DataitemParamsIceberg(DataitemParams):
    """
    Dataitem iceberg parameters.
    """
