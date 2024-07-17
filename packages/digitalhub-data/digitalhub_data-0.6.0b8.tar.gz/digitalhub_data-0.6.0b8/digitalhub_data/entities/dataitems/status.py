from __future__ import annotations

from digitalhub_core.entities._base.status import Status


class DataitemStatus(Status):
    """
    Status class for dataitem entities.
    """

    def __init__(
        self,
        state: str,
        message: str | None = None,
        files: list[dict] | None = None,
        preview: dict | None = None,
        **kwargs,
    ) -> None:
        """
        Constructor.

        Parameters
        ----------
        preview : dict
            Preview of the data.
        """
        super().__init__(state, message)
        self.files = files
        self.preview = preview

    def add_file(self, file: dict) -> None:
        """
        Add a file to the status.

        Parameters
        ----------
        file : dict
            File to add.

        Returns
        -------
        None
        """

        # Add the file to the list
        if self.files is None:
            self.files = []

        # Remove the file info if it already exists
        self.files = [f for f in self.files if f["path"] != file["path"]]

        # Add the new file
        self.files.append(file)


class DataitemStatusDataitem(DataitemStatus):
    """
    Status class for dataitem dataitem entities.
    """


class DataitemStatusTable(DataitemStatus):
    """
    Status class for dataitem table entities.
    """


class DataitemStatusIceberg(DataitemStatus):
    """
    Status class for dataitem iceberg entities.
    """
