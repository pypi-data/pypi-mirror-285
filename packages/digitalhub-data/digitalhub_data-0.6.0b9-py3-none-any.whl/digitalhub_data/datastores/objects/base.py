from __future__ import annotations

import typing
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any

from digitalhub_core.utils.exceptions import StoreError
from digitalhub_core.utils.uri_utils import map_uri_scheme
from digitalhub_data.readers.builder import get_reader_by_engine

if typing.TYPE_CHECKING:
    from digitalhub_core.stores.objects.base import Store


class Datastore(metaclass=ABCMeta):
    """
    Datastore abstract class.
    """

    def __init__(self, store: Store, **kwargs) -> None:
        self.store = store

    ############################
    # IO methods
    ############################

    def download(self, src: str, dst: str | None = None) -> str:
        """
        Download file from source to destination. Invokes store's download method.

        Parameters
        ----------
        src : str
            Source path.
        dst : str
            Destination path.

        Returns
        -------
        None
        """
        return self.store.download(src, dst)

    @abstractmethod
    def write_df(self, df: Any, dst: str, extension: str | None = None, **kwargs) -> str:
        """
        Write DataFrame as parquet or csv.
        """

    def read_df(self, path: str, extension: str, engine: str | None = "pandas", **kwargs) -> Any:
        """
        Read DataFrame from path.

        Parameters
        ----------
        path : str
            Path to read DataFrame from.
        extension : str
            Extension of the file.
        engine : str
            Dataframe engine (pandas, polars, etc.).
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        Any
            DataFrame.
        """
        reader = get_reader_by_engine(engine)
        self._validate_extension(extension)
        return reader.read_df(path, extension, **kwargs)

    ############################
    # Helper methods
    ############################

    @staticmethod
    def _validate_extension(extension: str) -> None:
        """
        Validate extension.

        Parameters
        ----------
        extension : str
            Extension of the file.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If extension is not supported.
        """
        if extension not in ["csv", "parquet"]:
            raise ValueError(f"Extension {extension} not supported.")

    def _check_local_dst(self, dst: str) -> None:
        """
        Check if the local destination directory exists. Create in case it does not.

        Parameters
        ----------
        dst : str
            The destination directory.

        Returns
        -------
        None

        Raises
        ------
        StoreError
            If the destination is not a local path.
        """
        if map_uri_scheme(dst) != "local":
            raise StoreError(f"Destination '{dst}' is not a local path.")
        self._build_path(dst)

    @staticmethod
    def _build_path(path: str) -> None:
        """
        Get path from store path and path.

        Parameters
        ----------
        path : str
            The path to build.

        Returns
        -------
        None
        """
        pth = Path(path)
        if pth.suffix != "":
            pth = pth.parent
        pth.mkdir(parents=True, exist_ok=True)
