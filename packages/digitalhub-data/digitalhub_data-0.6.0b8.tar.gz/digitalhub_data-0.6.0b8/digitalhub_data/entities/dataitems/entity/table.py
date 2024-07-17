from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from digitalhub_core.stores.builder import get_store
from digitalhub_data.datastores.builder import get_datastore
from digitalhub_data.entities.dataitems.entity._base import Dataitem


class DataitemTable(Dataitem):

    """
    Table dataitem.
    """

    def as_df(self, file_format: str | None = None, **kwargs) -> Any:
        """
        Read dataitem as a DataFrame. If the dataitem is not local, it will be downloaded
        to a temporary folder and deleted after the method is executed. If no file_format is passed,
        the function will try to infer it from the dataitem.spec.path attribute.
        The path of the dataitem is specified in the spec attribute, and must be a store aware path.
        If the dataitem is stored on s3 bucket, the path must be s3://<bucket>/<path_to_dataitem>.
        If the dataitem is stored on database (Postgres is the only one supported), the path must
        be sql://postgres/<database>/<schema>/<table/view>.

        Parameters
        ----------
        file_format : str
            Format of the file. (Supported csv and parquet).
        **kwargs : dict
            Keyword arguments passed to the read_df function.

        Returns
        -------
        Any
            DataFrame.
        """
        datastore = get_datastore(self.spec.path)
        tmp_path = False

        # Download dataitem if not local
        if not self._check_local(self.spec.path):
            path = datastore.download(self.spec.path)
            tmp_path = True
        else:
            path = self.spec.path

        # Get file info
        store = get_store(path)
        file_info = store.get_file_info(self.spec.path, path)
        if file_info is not None:
            self.refresh()
            self.status.add_file(file_info)
            self.save(update=True)

        # Check file format and get dataitem as DataFrame
        extension = self._get_extension(self.spec.path, file_format)
        df = datastore.read_df(path, extension, **kwargs)

        # Delete tmp folder
        if tmp_path:
            pth = Path(path)
            if pth.is_file():
                pth = pth.parent
            shutil.rmtree(pth)

        return df

    def write_df(
        self,
        df: Any,
        extension: str | None = None,
        **kwargs,
    ) -> str:
        """
        Write DataFrame as parquet/csv/table into dataitem path.

        Parameters
        ----------
        df : Any
            DataFrame to write.
        extension : str
            Extension of the file.
        **kwargs : dict
            Keyword arguments passed to the write_df function.

        Returns
        -------
        str
            Path to the written dataframe.
        """
        datastore = get_datastore(self.spec.path)
        target = datastore.write_df(df, self.spec.path, extension=extension, **kwargs)

        # Get file info
        store = get_store(target)
        file_info = store.get_file_info(target, self.spec.path)
        if file_info is not None:
            self.status.add_file(file_info)
        return target
