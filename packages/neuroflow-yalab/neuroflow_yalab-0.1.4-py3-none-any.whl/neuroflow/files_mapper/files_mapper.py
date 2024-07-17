"""
This module contains the FilesMapper class.

Example:
    >>> from neuroflow.files_mapper.files_mapper import FilesMapper
    >>> path = "data/0001/1"
    >>> mapper = FilesMapper(path)
    >>> print(mapper.subject)
    0001
"""

from pathlib import Path
from typing import Tuple, Union

from neuroflow.files_mapper.utils import load_json_file

PARENT = Path(__file__).resolve().parent


class FilesMapper:
    """
    A class used to map files to their respective patterns.
    """

    def __init__(
        self,
        path: str,
        patterns: Union[str, Path] = PARENT / "patterns.json",
    ):
        """
        Initialize the FilesMapper object.
        This object is used to map files to their respective patterns.

        Parameters
        ----------
        path : str
            Path to the directory containing the files to be mapped.
        patterns : dict
            Path to json file containing the patterns to be used for mapping.
            The keys are file types and the values are the corresponding patterns.
        """
        self.path = Path(path)
        self.patterns = load_json_file(patterns)
        self._subject, self._session = self._identify_entities()

    def _identify_entities(self) -> Tuple[str, str]:
        """
        Identify subject's and session's ID

        Returns
        -------
        Tuple[str,str]
            A tuple containing the subject's and session's ID.
        """
        subject = self.path.parent.name.zfill(4)
        session = self.path.name
        return subject, session

    def _map_files(self) -> dict:
        """
        Maps the files in the directory to their respective patterns.

        Returns
        -------
        dict
            A dictionary containing the files as keys
            and their corresponding patterns as values.
        """
        result = {}
        for key, pattern in self.patterns.items():
            file = self.path / pattern.format(
                subject=self.subject, session=self.session
            )
            if not file.exists():
                raise FileNotFoundError(f"File {file} not found. ({key} missing.)")
            result[key] = file
        return result

    @property
    def files(self) -> dict:
        """
        Returns the files mapped to their respective patterns.

        Returns
        -------
        dict
            A dictionary containing the files as keys
            and their corresponding patterns as values.
        """
        return self._map_files()

    @property
    def subject(self) -> str:
        """
        Returns the subject's ID.

        Returns
        -------
        str
            The subject's ID.
        """
        return self._subject

    @property
    def session(self) -> str:
        """
        Returns the session's ID.

        Returns
        -------
        str
            The session's ID.
        """
        return self._session
