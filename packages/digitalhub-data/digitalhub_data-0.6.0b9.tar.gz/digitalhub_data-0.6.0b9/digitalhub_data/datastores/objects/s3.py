from __future__ import annotations

from io import BytesIO
from typing import Any

from digitalhub_data.datastores.objects.base import Datastore
from digitalhub_data.readers.builder import get_reader_by_object


class S3Datastore(Datastore):
    """
    S3 Datastore class.
    """

    def write_df(self, df: Any, dst: str, extension: str | None = None, **kwargs) -> str:
        """
        Write a dataframe to S3 based storage. Kwargs are passed to df.to_parquet().

        Parameters
        ----------
        df : Any
            The dataframe.
        dst : str
            The destination path on S3 based storage.
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        str
            The path S3 path where the dataframe was saved.
        """
        fileobj = BytesIO()
        reader = get_reader_by_object(df)
        reader.write_df(df, fileobj, extension=extension, **kwargs)

        key = self.store._get_key(dst)
        return self.store._upload_fileobj(fileobj, key)
