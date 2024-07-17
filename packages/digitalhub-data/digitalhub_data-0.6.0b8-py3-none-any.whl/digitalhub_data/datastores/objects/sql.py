from __future__ import annotations

from typing import Any

from digitalhub_core.entities._builders.uuid import build_uuid
from digitalhub_data.datastores.objects.base import Datastore
from digitalhub_data.readers.builder import get_reader_by_object


class SqlDatastore(Datastore):
    """
    Sql Datastore class.
    """

    def write_df(self, df: Any, dst: str, extension: str | None = None, **kwargs) -> str:
        """
        Write a dataframe to a database. Kwargs are passed to df.to_sql().

        Parameters
        ----------
        df : Any
            The dataframe to write.
        dst : str
            The destination of the dataframe.
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        str
            Path of written dataframe.
        """
        if dst is None:
            schema = str(self.store.config.pg_schema)
            table = build_uuid()
        else:
            schema = self.store._get_schema(dst)
            table = self.store._get_table_name(dst)
        return self._upload_table(df, schema, table, **kwargs)

    def _upload_table(self, df: Any, schema: str, table: str, **kwargs) -> str:
        """
        Upload a table to SQL based storage.

        Parameters
        ----------
        df : DataFrame
            The dataframe.
        schema : str
            Destination schema.
        table : str
            Destination table.
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        str
            The SQL URI where the dataframe was saved.
        """
        reader = get_reader_by_object(df)
        engine = self.store._check_factory()
        reader.write_table(df, table, engine, schema, **kwargs)
        engine.dispose()
        return f"sql://{engine.url.database}/{schema}/{table}"
