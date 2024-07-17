import pickle
from pathlib import Path
from typing import ClassVar, Optional, Union

from neuroflow.covariates import Covariate
from neuroflow.covariates.available_qc_measures import get_available_measures
from neuroflow.files_mapper.files_mapper import FilesMapper


class CovariatesCollector(Covariate):
    """
    CovariatesCollector class is responsible for gathering all QC
    measures available for a participant.
    """

    DIRECTORY_NAME: ClassVar[str] = "covariates"

    def __init__(
        self,
        mapper: FilesMapper,
        google_credentials_path: Union[str, Path],
        location: str = "Tel Aviv University",
        output_directory: Optional[str] = None,
        sources: Optional[Union[str, list]] = None,
        force: bool = False,
    ):
        """
        Constructor for the QCManager class.

        Parameters
        ----------
        mapper : FilesMapper
            The mapper to the files
        google_credentials_path : Union[str, Path]
            The path to the Google credentials
        output_directory : Optional[str], optional
            Path to the output directory, by default None
        sources : Optional[Union[str, list]], optional
            The sources of the QC measures, by default None
        force : bool, optional
            Force the processing of the data, by default False
        """
        super().__init__(mapper, output_directory)
        self.google_credentials_path = Path(google_credentials_path)
        self.location = location
        self.qc_measures = self._get_covariates(sources)
        self.force = force

    def _get_covariates(self, sources: Optional[Union[str, list]] = None):
        """
        Get the QC measures for the participant.

        Parameters
        ----------
        sources : Optional[Union[str, list]], optional
            The sources of the QC measures, by default None
        """
        available_measures = get_available_measures()
        if sources is None:
            return available_measures
        if isinstance(sources, str):
            sources = [sources]
        results = {}
        for source in sources:
            if source in available_measures:
                results[source] = available_measures[source]
            else:
                raise ValueError(
                    f"Source {source} is not available in the QC measures."
                )
        return results

    def _collect_inputs(self, inputs: list):
        """
        Collect inputs for the QC measures.
        """
        # return a dictionary with the inputs from self
        return {input: getattr(self, input, None) for input in inputs}

    def _collect_covariates(self):
        """
        Collect QC measures for the participant.
        """
        results = {}
        for qc_measures in self.qc_measures.values():
            runner = qc_measures["runner"]
            inputs = self._collect_inputs(qc_measures["inputs"])
            runner = runner(**inputs)
            results.update(runner.get_covariates(force=self.force))
        return results

    def save_to_file(self):
        """
        Save the covariates to a pickle file.

        Parameters
        ----------
        force : bool, optional
            Force the saving of the covariates, by default False
        """
        with Path.open(self.output_directory / "covariates.pkl", "wb") as file:
            pickle.dump(self.covariates, file)

    @property
    def covariates(self):
        """
        Get the quality control covariates
        """
        return self._collect_covariates()
