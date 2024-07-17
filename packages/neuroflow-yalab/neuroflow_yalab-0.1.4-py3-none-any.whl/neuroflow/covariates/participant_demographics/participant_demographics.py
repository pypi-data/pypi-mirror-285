"""
Participant Demographics Covariate Class
"""

from pathlib import Path
from typing import ClassVar, Optional, Union

import pandas as pd

from neuroflow.covariates.covariate import Covariate
from neuroflow.covariates.participant_demographics.utils import (
    CRF_COLUMNS_TO_KEEP,
    CRF_TRANSFORMATIONS,
    get_worksheet,
    load_or_request_credentials,
)
from neuroflow.files_mapper.files_mapper import FilesMapper


class ParticipantDemographics(Covariate):
    """
    Class to handle the participant demographics data

    Attributes
    ----------
    mapper : FilesMapper
        The mapper to the files

    Methods
    -------
    _get_timestamp_from_session(session_id:str) -> datetime
        Parse the timestamp of a session from the session id
    """

    SUBJECT_ID_COLUMN: ClassVar = "Questionnaire"
    CRF_COLUMNS: ClassVar = CRF_COLUMNS_TO_KEEP.copy()
    TRANSFORMATIONS: ClassVar = CRF_TRANSFORMATIONS.copy()

    COVARIATE_SOURCE: ClassVar = "demographics"
    DIRECTORY_NAME: ClassVar = "demographics"

    _crf = None

    def __init__(
        self,
        mapper: FilesMapper,
        google_credentials_path: Union[str, Path],
        output_directory: Optional[Union[str, Path]] = None,
    ):
        """
        Constructor for the ParticipantDemographics class

        Parameters
        ----------
        mapper : FilesMapper
            The mapper to the files
        """
        super().__init__(mapper, output_directory)
        self.google_credentials_path = google_credentials_path

    def _load_crf(self, google_credentials_path: Union[str, Path]):
        """
        Load the CRF data from a Google Sheet

        Parameters
        ----------
        google_credentials_path : Union[str, Path]
            The path to the Google credentials
        """
        credentials = load_or_request_credentials(google_credentials_path)
        return get_worksheet(credentials)

    def locate_subject_row(self):
        """
        Locate the row of the subject in the CRF data
        """
        fixed_crf_subjects = (
            self.crf[self.SUBJECT_ID_COLUMN]
            .astype(str)
            .str.lower()
            .str.zfill(4)
            .str.replace("_", "")
        )
        mask = fixed_crf_subjects == self.mapper.subject.lower()
        return self.crf.loc[mask]

    def _calculate_age_from_dob(self, subject_row: pd.DataFrame):
        """
        Calculate the age from the date of birth

        Parameters
        ----------
        dob : str
            The date of birth

        Returns
        -------
        int
            The age
        """
        dob = subject_row["dob"].iloc[0]
        return (self.session_timestamp - dob).days // 365

    def get_covariates(self, force: Optional[bool] = False):
        """
        Get the data of the subject from the CRF data

        Parameters
        ----------
        force : Optional[bool], optional
            Force the processing of the data, by default False
        """
        _ = force
        subject_row = self.locate_subject_row()
        subject_row = subject_row[list(self.CRF_COLUMNS.keys())].rename(
            columns=self.CRF_COLUMNS
        )
        for column, transformation in self.TRANSFORMATIONS.items():
            subject_row[column] = subject_row[column].apply(transformation)
        subject_row["age_at_scan"] = self._calculate_age_from_dob(subject_row)
        subject_row = subject_row.reset_index().rename({"index": "crf_index"})
        covariate = subject_row.iloc[0].to_dict()
        return {self.COVARIATE_SOURCE: covariate}

    @property
    def crf(self):
        """
        The CRF data
        """
        if self._crf is None:
            self._crf = self._load_crf(self.google_credentials_path)
        return self._crf
