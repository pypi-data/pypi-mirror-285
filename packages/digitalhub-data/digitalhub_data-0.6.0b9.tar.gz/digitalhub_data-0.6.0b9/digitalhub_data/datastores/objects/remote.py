from __future__ import annotations

from typing import Any

from digitalhub_data.datastores.objects.base import Datastore


class RemoteDatastore(Datastore):
    """
    Remote Datastore class.
    """

    def write_df(self, df: Any, dst: str, extension: str | None = None, **kwargs) -> str:
        """
        Method to write a dataframe to a file. Note that this method is not implemented
        since the remote store is not meant to write dataframes.

        Raises
        ------
        NotImplementedError
            This method is not implemented.
        """
        raise NotImplementedError("Remote store does not support write_df.")
