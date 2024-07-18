from __future__ import annotations

import typing

from digitalhub_core.entities._builders.metadata import build_metadata
from digitalhub_core.entities._builders.name import build_name
from digitalhub_core.entities._builders.spec import build_spec
from digitalhub_core.entities._builders.status import build_status
from digitalhub_core.entities._builders.uuid import build_uuid
from digitalhub_core.utils.env_utils import get_s3_bucket
from digitalhub_core.utils.exceptions import EntityError
from digitalhub_data.entities.entity_types import EntityTypes

if typing.TYPE_CHECKING:
    from digitalhub_data.entities.dataitems.entity._base import Dataitem

# Manage class mapper
cls_mapper = {}
try:
    from digitalhub_data.entities.dataitems.entity.dataitem import DataitemDataitem

    cls_mapper["dataitem"] = DataitemDataitem
except ImportError:
    ...
try:
    from digitalhub_data.entities.dataitems.entity.table import DataitemTable

    cls_mapper["table"] = DataitemTable
except ImportError:
    ...
try:
    from digitalhub_data.entities.dataitems.entity.iceberg import DataitemIceberg

    cls_mapper["iceberg"] = DataitemIceberg
except ImportError:
    pass


def _choose_dataitem_type(kind: str) -> type[Dataitem]:
    """
    Choose class based on kind.

    Parameters
    ----------
    kind : str
        Kind the object.

    Returns
    -------
    type[Dataitem]
        Class of the dataitem.
    """
    try:
        return cls_mapper[kind]
    except KeyError:
        raise EntityError(f"Unknown dataitem kind: {kind}")


def dataitem_from_parameters(
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
    name = build_name(name)
    uuid = build_uuid(uuid)
    if path is None:
        bucket = get_s3_bucket()
        entity_type = EntityTypes.DATAITEMS.value
        path = f"s3://{bucket}/{project}/{entity_type}/{name}/{uuid}/data.parquet"
    metadata = build_metadata(
        kind,
        project=project,
        name=name,
        version=uuid,
        description=description,
        source=git_source,
        labels=labels,
        embedded=embedded,
    )
    spec = build_spec(
        kind,
        path=path,
        **kwargs,
    )
    status = build_status(kind)
    cls = _choose_dataitem_type(kind)
    return cls(
        project=project,
        name=name,
        uuid=uuid,
        kind=kind,
        metadata=metadata,
        spec=spec,
        status=status,
    )


def dataitem_from_dict(obj: dict) -> Dataitem:
    """
    Create dataitem from dictionary.

    Parameters
    ----------
    obj : dict
        Dictionary to create object from.

    Returns
    -------
    Dataitem
        Dataitem object.
    """
    kind = obj.get("kind")
    cls = _choose_dataitem_type(kind)
    return cls.from_dict(obj)
