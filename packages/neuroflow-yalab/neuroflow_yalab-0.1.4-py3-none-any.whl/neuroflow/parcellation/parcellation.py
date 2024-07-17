"""
Parcellation module for NeuroFlow.
"""

from pathlib import Path
from typing import Callable, ClassVar, Optional, Union

import pandas as pd

from neuroflow.atlases.atlases import Atlases
from neuroflow.parcellation.available_measures import AVAILABLE_MEASURES
from neuroflow.parcellation.utils import parcellate
from neuroflow.recon_tensors.recon_tensors import ReconTensors


class Parcellation:
    """
    Parcellation class for NeuroFlow.
    """

    OUTPUT_TEMPLATE: ClassVar = (
        "{atlas}/sub-{subject}_ses-{session}_space-dwi_label-{label}_acq-shell{acq}_rec-{software}_atlas-{atlas}_desc-{metric}_parc.pkl"  # noqa: E501
    )
    MEASURES: ClassVar = AVAILABLE_MEASURES

    DIRECTORY_NAME: ClassVar = "parcellations"

    def __init__(
        self,
        tensors_manager: ReconTensors,
        atlases_manager: Atlases,
        output_directory: Union[str, Path],
        measures: Optional[Union[str, list]] = None,
    ):
        """
        Initialize the Parcellation class.

        Parameters
        ----------
        tensors_manager : ReconTensors
            An instance of ReconTensors class.
        atlases_manager : Atlases
            An instance of Atlases class.
        out_dir : Union[str, Path]
            Path to the output directory.
        """
        self.tensors_manager = tensors_manager
        self.atlases_manager = atlases_manager
        self.mapper = self.tensors_manager.mapper
        self.output_directory = self._gen_output_directory(output_directory)
        self.measures = self._validate_measures(measures)

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

    def _validate_measures(self, measures: Union[str, list]) -> Callable:
        """
        Validate the measure.

        Parameters
        ----------
        measure : str
            Measure to validate.

        Returns
        -------
        Callable
            Measure function.
        """
        if measures is None:
            return self.MEASURES
        if isinstance(measures, str):
            measures = [measures]
        for measure in measures:
            if measure not in self.MEASURES:
                raise ValueError(f"Invalid measure: {measure}.")
        return {measure: self.MEASURES[measure] for measure in measures}

    def run(self, force: bool = False) -> dict:
        """
        Run the parcellation workflow.

        Parameters
        ----------
        force : bool
            Force the generation of the parcellation, by default True

        Returns
        -------
        dict
            Outputs for the parcellation workflow.
        """
        outputs = {}
        for atlas_name, atlas_entities in self.atlases_manager.dwi_atlases.items():
            outputs[atlas_name] = {}
            for metric, metric_image in self.tensors_manager.outputs.items():
                outputs[atlas_name][metric] = {}
                out_file = self.output_directory / self.OUTPUT_TEMPLATE.format(
                    atlas=atlas_name,
                    subject=self.mapper.subject,
                    session=self.mapper.session,
                    metric=metric,
                    label=self.atlases_manager.label,
                    acq=self.tensors_manager.max_bvalue,
                    software=self.tensors_manager.software,
                )
                if out_file.exists():
                    if force:
                        out_file.unlink()
                    else:
                        # validate that all measures are present
                        data = pd.read_pickle(out_file)  # noqa
                        if all(
                            [measure in data.columns for measure in self.measures]
                        ):  # noqa
                            outputs[atlas_name][metric] = out_file
                            continue
                out_file.parent.mkdir(parents=True, exist_ok=True)
                df = pd.read_csv(
                    atlas_entities["description_file"],
                    index_col=atlas_entities["index_col"],
                ).copy()
                for measure_name, measure in self.measures.items():
                    df[measure_name] = parcellate(
                        atlas_entities,
                        metric_image,
                        measure,
                    )["value"]
                df.to_pickle(out_file)
                outputs[atlas_name][metric] = out_file
        return outputs
