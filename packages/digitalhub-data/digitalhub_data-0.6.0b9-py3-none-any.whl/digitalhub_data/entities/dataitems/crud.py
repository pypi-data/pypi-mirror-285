from __future__ import annotations

import typing
from typing import Any

from digitalhub_core.context.builder import check_context
from digitalhub_core.entities._base.crud import (
    delete_entity_api_ctx,
    list_entity_api_ctx,
    read_entity_api_ctx,
    read_entity_api_ctx_versions,
    update_entity_api_ctx,
)
from digitalhub_core.utils.io_utils import read_yaml
from digitalhub_data.entities.dataitems.builder import dataitem_from_dict, dataitem_from_parameters
from digitalhub_data.entities.entity_types import EntityTypes
from digitalhub_data.readers.builder import get_reader_by_object

if typing.TYPE_CHECKING:
    from digitalhub_data.entities.dataitems.entity._base import Dataitem


ENTITY_TYPE = EntityTypes.DATAITEMS.value


def create_dataitem(**kwargs) -> Dataitem:
    """
    Create a new data item with the provided parameters.

    Parameters
    ----------
    **kwargs : dict
        Keyword arguments.

    Returns
    -------
    Dataitem
        Object instance.
    """
    return dataitem_from_parameters(**kwargs)


def create_dataitem_from_dict(obj: dict) -> Dataitem:
    """
    Create a new Dataitem instance from a dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create object from.

    Returns
    -------
    Dataitem
        Dataitem object.
    """
    check_context(obj.get("project"))
    return dataitem_from_dict(obj)


def new_dataitem(
    project: str,
    name: str,
    kind: str,
    uuid: str | None = None,
    description: str | None = None,
    git_source: str | None = None,
    labels: list[str] | None = None,
    embedded: bool = True,
    path: str | None = None,
    **kwargs,
) -> Dataitem:
    """
    Create a new object instance.

    Parameters
    ----------
    project : str
        Project name.
    name : str
        Object name.
    kind : str
        Kind the object.
    uuid : str
        ID of the object (UUID4).
    description : str
        Description of the object (human readable).
    git_source : str
        Remote git source for object.
    labels : list[str]
        List of labels.
    embedded : bool
        Flag to determine if object must be embedded in project.
    path : str
        Object path on local file system or remote storage.
        If not provided, it's generated.
    **kwargs : dict
        Spec keyword arguments.

    Returns
    -------
    Dataitem
        Object instance.
    """
    obj = create_dataitem(
        project=project,
        name=name,
        kind=kind,
        path=path,
        uuid=uuid,
        description=description,
        git_source=git_source,
        labels=labels,
        embedded=embedded,
        **kwargs,
    )
    obj.save()
    return obj


def get_dataitem(
    identifier: str,
    project: str | None = None,
    entity_id: str | None = None,
    **kwargs,
) -> Dataitem:
    """
    Get object from backend.

    Parameters
    ----------
    identifier : str
        Entity key or name.
    project : str
        Project name.
    entity_id : str
        Entity ID.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    Dataitem
        Object instance.
    """
    obj = read_entity_api_ctx(
        identifier,
        ENTITY_TYPE,
        project=project,
        entity_id=entity_id,
        **kwargs,
    )
    return dataitem_from_dict(obj)


def get_dataitem_versions(
    identifier: str,
    project: str | None = None,
    **kwargs,
) -> list[Dataitem]:
    """
    Get object versions from backend.

    Parameters
    ----------
    identifier : str
        Entity key or name.
    project : str
        Project name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    list[Dataitem]
        List of object instances.
    """
    obj = read_entity_api_ctx_versions(
        identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        **kwargs,
    )
    return [dataitem_from_dict(o) for o in obj]


def import_dataitem(file: str) -> Dataitem:
    """
    Get object from file.

    Parameters
    ----------
    file : str
        Path to the file.

    Returns
    -------
    Dataitem
        Object instance.
    """
    obj: dict = read_yaml(file)
    return create_dataitem_from_dict(obj)


def delete_dataitem(
    identifier: str,
    project: str | None = None,
    entity_id: str | None = None,
    delete_all_versions: bool = False,
    **kwargs,
) -> dict:
    """
    Delete object from backend.

    Parameters
    ----------
    identifier : str
        Entity key or name.
    project : str
        Project name.
    entity_id : str
        Entity ID.
    delete_all_versions : bool
        Delete all versions of the named entity.
        Use entity name instead of entity key as identifier.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    dict
        Response from backend.
    """
    return delete_entity_api_ctx(
        identifier=identifier,
        entity_type=ENTITY_TYPE,
        project=project,
        entity_id=entity_id,
        delete_all_versions=delete_all_versions,
        **kwargs,
    )


def update_dataitem(entity: Dataitem, **kwargs) -> Dataitem:
    """
    Update object in backend.

    Parameters
    ----------
    entity : Dataitem
        The object to update.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    Dataitem
        Entity updated.
    """
    obj = update_entity_api_ctx(
        project=entity.project,
        entity_type=ENTITY_TYPE,
        entity_id=entity.id,
        entity_dict=entity.to_dict(),
        **kwargs,
    )
    return dataitem_from_dict(obj)


def list_dataitems(project: str, **kwargs) -> list[Dataitem]:
    """
    List all objects from backend.

    Parameters
    ----------
    project : str
        Project name.
    **kwargs : dict
        Parameters to pass to the API call.

    Returns
    -------
    list[Dataitem]
        List of dataitems.
    """
    objs = list_entity_api_ctx(
        project=project,
        entity_type=ENTITY_TYPE,
        **kwargs,
    )
    return [dataitem_from_dict(obj) for obj in objs]


def log_dataitem(
    project: str,
    name: str,
    kind: str,
    path: str | None = None,
    data: Any | None = None,
    extension: str | None = None,
    **kwargs,
) -> Dataitem:
    """
    Log a dataitem to the project.

    Parameters
    ----------
    project : str
        Project name.
    name : str
        Object name.
    kind : str
        Kind the object.
    path : str
        Destination path of the dataitem.
    data : Any
        Dataframe to log.
    extension : str
        Extension of the dataitem.
    **kwargs : dict
        New dataitem parameters.

    Returns
    -------
    Dataitem
        Object instance.
    """
    dataitem = create_dataitem(project=project, name=name, kind=kind, path=path, **kwargs)
    if kind == "table":
        dataitem.write_df(df=data, extension=extension)
        reader = get_reader_by_object(data)
        dataitem.spec.schema = reader.get_schema(data)
        dataitem.status.preview = reader.get_preview(data)
    dataitem.save()
    return dataitem
