from datetime import datetime
from pathlib import Path
from typing import ClassVar, Optional

from neuroflow.files_mapper.files_mapper import FilesMapper


class Covariate:
    """
    Class to handle the covariate data
    """

    TIMESTAMP_FORMAT: ClassVar = "%Y%m%d%H%M"
    COVARIATE_SOURCE: ClassVar = None
    DIRECTORY_NAME: ClassVar = "covariates"

    def __init__(self, mapper: FilesMapper, output_directory: Optional[str] = None):
        """
        Constructor for the Covariate class

        Parameters
        ----------
        mapper : FilesMapper
            The mapper to the files
        """
        self.mapper = mapper
        self.session_timestamp = self._get_timestamp_from_session(self.mapper.session)
        self.output_directory = self._gen_output_directory(output_directory)

    def _gen_output_directory(self, output_directory: Optional[str] = None) -> Path:
        """
        Generate output directory for QC measures.

        Parameters
        ----------
        output_directory : Optional[str], optional
            Path to the output directory, by default None

        Returns
        -------
        Path
            Path to the output directory
        """
        if output_directory is None:
            return None
        output_directory = Path(output_directory)
        flags = [
            output_directory.parent.name == f"ses-{self.mapper.session}",
            output_directory.parent.parent.name == f"sub-{self.mapper.subject}",
        ]
        if all(flags):
            output_directory = output_directory / self.DIRECTORY_NAME
        else:
            output_directory = (
                Path(output_directory)
                / f"sub-{self.mapper.subject}"
                / f"ses-{self.mapper.session}"
                / self.DIRECTORY_NAME
            )
        output_directory.mkdir(parents=True, exist_ok=True)
        return output_directory

    def _get_timestamp_from_session(self, session_id: str) -> datetime:
        """
        Parse the timestamp of a session from the session id

        Parameters
        ----------
        session_id : str
            The id of the session

        Returns
        -------
        datetime
            The timestamp of the session
        """
        try:
            return datetime.strptime(session_id, self.TIMESTAMP_FORMAT)  # noqa: DTZ007
        except ValueError:
            return None

    def get_covariates(self):
        """
        Get the covariate data

        Returns
        -------
        dict
            The covariate data
        """
        raise NotImplementedError
