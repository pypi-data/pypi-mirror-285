from __future__ import annotations

import typing
from pathlib import Path
from urllib.parse import urlparse

from digitalhub_core.context.builder import get_context
from digitalhub_core.entities._base.crud import create_entity_api_ctx, read_entity_api_ctx, update_entity_api_ctx
from digitalhub_core.entities._base.entity import Entity
from digitalhub_core.entities._builders.metadata import build_metadata
from digitalhub_core.entities._builders.name import build_name
from digitalhub_core.entities._builders.spec import build_spec
from digitalhub_core.entities._builders.status import build_status
from digitalhub_core.entities._builders.uuid import build_uuid
from digitalhub_core.stores.builder import get_store
from digitalhub_core.utils.exceptions import EntityError
from digitalhub_core.utils.generic_utils import check_overwrite, get_timestamp
from digitalhub_core.utils.io_utils import write_yaml
from digitalhub_core.utils.uri_utils import check_local_path, map_uri_scheme
from digitalhub_data.entities.entity_types import EntityTypes

if typing.TYPE_CHECKING:
    from digitalhub_core.context.context import Context
    from digitalhub_core.entities._base.metadata import Metadata
    from digitalhub_data.entities.dataitems.spec import DataitemSpec
    from digitalhub_data.entities.dataitems.status import DataitemStatus


class Dataitem(Entity):
    """
    A class representing a dataitem.
    """

    ENTITY_TYPE = EntityTypes.DATAITEMS.value

    def __init__(
        self,
        project: str,
        name: str,
        uuid: str,
        kind: str,
        metadata: Metadata,
        spec: DataitemSpec,
        status: DataitemStatus,
        user: str | None = None,
    ) -> None:
        """
        Constructor.

        Parameters
        ----------
        project : str
            Project name.
        name : str
            Name of the object.
        uuid : str
            Version of the object.
        kind : str
            Kind the object.
        metadata : Metadata
            Metadata of the object.
        spec : DataitemSpec
            Specification of the object.
        status : DataitemStatus
            Status of the object.
        user : str
            Owner of the object.
        """
        super().__init__()
        self.project = project
        self.name = name
        self.id = uuid
        self.kind = kind
        self.key = f"store://{project}/{self.ENTITY_TYPE}/{kind}/{name}:{uuid}"
        self.metadata = metadata
        self.spec = spec
        self.status = status
        self.user = user

        # Add attributes to be used in the to_dict method
        self._obj_attr.extend(["project", "name", "id", "key"])

    #############################
    #  Save / Refresh / Export
    #############################

    def save(self, update: bool = False) -> Dataitem:
        """
        Save entity into backend.

        Parameters
        ----------
        update : bool
            Flag to indicate update.

        Returns
        -------
        Dataitem
            Entity saved.
        """
        obj = self.to_dict()

        if not update:
            new_obj = create_entity_api_ctx(self.project, self.ENTITY_TYPE, obj)
            self._update_attributes(new_obj)
            return self

        self.metadata.updated = obj["metadata"]["updated"] = get_timestamp()
        new_obj = update_entity_api_ctx(self.project, self.ENTITY_TYPE, self.id, obj)
        self._update_attributes(new_obj)
        return self

    def refresh(self) -> Dataitem:
        """
        Refresh object from backend.

        Returns
        -------
        Dataitem
            Entity refreshed.
        """
        new_obj = read_entity_api_ctx(self.key)
        self._update_attributes(new_obj)
        return self

    def export(self, filename: str | None = None) -> None:
        """
        Export object as a YAML file.

        Parameters
        ----------
        filename : str
            Name of the export YAML file. If not specified, the default value is used.

        Returns
        -------
        None
        """
        obj = self.to_dict()
        if filename is None:
            filename = f"{self.kind}_{self.name}_{self.id}.yml"
        pth = self._context().root / filename
        pth.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(pth, obj)

    #############################
    #  Context
    #############################

    def _context(self) -> Context:
        """
        Get context.

        Returns
        -------
        Context
            Context.
        """
        return get_context(self.project)

    #############################
    #  Dataitem methods
    #############################

    def as_file(self) -> str:
        """
        Get dataitem as file. In the case of a local store, the store returns the current
        path of the dataitem. In the case of a remote store, the dataitem is downloaded in
        a temporary directory.

        Returns
        -------
        str
            Path of the dataitem.
        """
        path = self.spec.path
        store = get_store(path)
        if store.is_local():
            return path
        return store.download(path)

    def download(
        self,
        destination: str | None = None,
        overwrite: bool = False,
    ) -> str:
        """
        Download dataitem from remote storage.

        Parameters
        ----------
        destination : str
            Destination path as filename.
        overwrite : bool
            Specify if overwrite an existing file. Default value is False.

        Returns
        -------
        str
            Path of the downloaded dataitem.
        """

        # Check if target path is remote
        path = self.spec.path
        store = get_store(path)
        if store.is_local():
            raise RuntimeError("Local files cannot be downloaded. Use as_file().")

        # Check if download destination path is specified and rebuild it if necessary
        if destination is None:
            filename = Path(urlparse(path).path).name
            destination = f"{self.project}/{self.ENTITY_TYPE}/{self.name}/{self.id}/{filename}"

        # Check if destination path is local
        self._check_local(destination)

        # Check if destination path exists for overwrite
        check_overwrite(destination, overwrite)

        # Download dataitem and return path
        return store.download(path, destination)

    def write_file(self, src: str) -> str:
        """
        Write file into dataitem path.

        Parameters
        ----------
        src : str
            Local path of the file to write.

        Returns
        -------
        str
            Path to the written file.
        """
        path = self.spec.path
        store = get_store(path)
        if store.is_local():
            raise RuntimeError("Only remote paths are supported for upload.")

        # Get store and upload file and return remote path
        target = store.upload(src, path)
        file_info = store.get_file_info(target, src)

        if file_info is not None:
            self.refresh()
            self.status.add_file(file_info)
            self.save(update=True)

        return target

    #############################
    #  Helper Methods
    #############################

    @staticmethod
    def _check_local(path: str) -> bool:
        """
        Check if path is local.

        Parameters
        ----------
        path : str
            Path to check.

        Returns
        -------
        bool
            True if local, False otherwise.
        """
        return check_local_path(path)

    @staticmethod
    def _get_extension(path: str, file_format: str | None = None) -> str:
        """
        Get extension of path.

        Parameters
        ----------
        path : str
            Path to get extension from.
        file_format : str
            File format.

        Returns
        -------
        str
            File extension.

        Raises
        ------
        EntityError
            If file format is not supported.
        """
        if file_format is not None:
            return file_format

        scheme = map_uri_scheme(path)
        if scheme == "sql":
            return "parquet"

        ext = Path(path).suffix[1:]
        if ext is not None:
            return ext
        raise EntityError("Unknown file format. Only csv and parquet are supported.")

    #############################
    #  Static interface methods
    #############################

    @staticmethod
    def _parse_dict(obj: dict, validate: bool = True) -> dict:
        """
        Get dictionary and parse it to a valid entity dictionary.

        Parameters
        ----------
        entity : str
            Entity type.
        obj : dict
            Dictionary to parse.

        Returns
        -------
        dict
            A dictionary containing the attributes of the entity instance.
        """
        project = obj.get("project")
        name = build_name(obj.get("name"))
        kind = obj.get("kind")
        uuid = build_uuid(obj.get("id"))
        metadata = build_metadata(kind, **obj.get("metadata", {}))
        spec = build_spec(kind, validate=validate, **obj.get("spec", {}))
        status = build_status(kind, **obj.get("status", {}))
        user = obj.get("user")
        return {
            "project": project,
            "name": name,
            "uuid": uuid,
            "kind": kind,
            "metadata": metadata,
            "spec": spec,
            "status": status,
            "user": user,
        }
