"""
ConnectomeReconstructor class for NeuroFlow.
"""

from pathlib import Path
from typing import ClassVar, Optional

import pandas as pd

from neuroflow.atlases.atlases import Atlases
from neuroflow.connectome.utils import COMBINATIONS
from neuroflow.files_mapper import FilesMapper
from neuroflow.interfaces.mrtrix3.mrtrix3 import BuildConnectome


class ConnectomeReconstructor:
    """
    ConnectomeReconstructor class for NeuroFlow.
    A class to reconstruct connectomes from tractography data.
    """

    OUTPUT_TEMPLATE: ClassVar = (
        "{atlas}/sub-{subject}_ses-{session}_space-dwi_label-{label}_atlas-{atlas}_scale-{scale}_meas-{stat_edge}_{suffix}.csv"  # noqa: E501
    )
    RECONSTRUCTION_COMBINATIONS: ClassVar = COMBINATIONS.copy()
    OUTPUT_FLAG: ClassVar = "out_connectome"

    DIRECTORY_NAME: ClassVar = "connectomes"

    def __init__(
        self,
        mapper: FilesMapper,
        atlases_manager: Atlases,
        output_directory: Optional[str] = None,
        nthreads: int = 1,
    ):
        """
        Initialize the ConnectomeReconstructor class.

        Parameters
        ----------
        mapper : FilesMapper
            An instance of FilesMapper class.
        atlases_manager : Atlases
            An instance of Atlases class.
        output_directory : str
            Path to the output directory.
        """
        self.mapper = mapper
        self.atlases_manager = atlases_manager
        self.atlases_manager.crop_to_gm = False
        self.output_directory = self._gen_output_directory(output_directory)
        self.nthreads = nthreads

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

    def _generate_inputs_grid(self) -> list:
        """
        Generate the inputs grid for the connectome reconstruction.

        Returns
        -------
        list
            Inputs grid for the connectome reconstruction.
        """
        grid = {}
        for atlas, atlas_data in self.atlases_manager.dwi_atlases.items():
            combinations = self._generate_inputs()
            for combination in combinations:
                combination["in_nodes"] = atlas_data.get("nifti")
                combination.update(self._build_output_paths(combination, atlas))
            grid[atlas] = combinations
        return grid

    def _build_output_paths(self, inputs: dict, atlas_name: str) -> dict:
        """
        Build the output paths for the connectome reconstruction.

        Parameters
        ----------
        inputs : dict
            Inputs for the connectome reconstruction.
        atlas_name : str
            Name of the atlas.

        Returns
        -------
        dict
            Output paths for the connectome reconstruction.
        """
        result = {}
        for suffix in ["connectome", "assignments"]:
            result[f"out_{suffix}"] = (
                self.output_directory
                / self.OUTPUT_TEMPLATE.format(
                    atlas=atlas_name,
                    subject=self.mapper.subject,
                    session=self.mapper.session,
                    label=self.atlases_manager.label,
                    scale=inputs.get("scale", "none"),
                    stat_edge=inputs["stat_edge"],
                    suffix=suffix,
                )
            )
        return result

    def _generate_inputs(self) -> dict:
        """
        Generate the inputs for the connectome reconstruction.

        Returns
        -------
        dict
            Inputs for the connectome reconstruction.
        """
        inputs = []
        for combination in self.RECONSTRUCTION_COMBINATIONS:
            inputs.append({**self.base_inputs, **combination})
        return inputs

    def _reconstruct_connectome(
        self, inputs: dict, force: Optional[bool] = False
    ) -> dict:
        """
        Reconstruct the connectome.

        Parameters
        ----------
        inputs : dict
            Inputs for the connectome reconstruction.
        force : Optional[bool], optional
            Force the generation of the connectome, by default False

        Returns
        -------
        dict
            Outputs for the connectome reconstruction.

        """
        updated_inputs = inputs.copy()
        # remove the scale key if it is not set
        if updated_inputs.get("scale") is None:
            updated_inputs.pop("scale")
        connectome = BuildConnectome(**updated_inputs, force=force)
        return connectome.run()

    def run(self, force: bool = False) -> dict:
        """
        Run the connectome reconstruction.

        Parameters
        ----------
        force : bool
            Force the generation of the connectome, by default False

        Returns
        -------
        dict
            Outputs for the connectome reconstruction.
        """
        grid = self._generate_inputs_grid()
        outputs = pd.DataFrame(
            columns=["atlas", "scale", "stat_edge", "connectome", "assignments"]
        )
        for atlas, inputs in grid.items():
            for input_data in inputs:
                flag = input_data.get(self.OUTPUT_FLAG)
                if not flag.exists() or force:
                    # flag.unlink(missing_ok=True)
                    flag.parent.mkdir(parents=True, exist_ok=True)
                    _ = self._reconstruct_connectome(input_data, force=force)
                outputs = pd.concat(
                    [
                        outputs,
                        pd.DataFrame(
                            {
                                "atlas": atlas,
                                "scale": input_data.get("scale", "none"),
                                "stat_edge": input_data["stat_edge"],
                                "connectome": flag,
                                "assignments": input_data.get("out_assignments"),
                            },
                            index=[0],
                        ),
                    ],
                    ignore_index=True,
                )

        return outputs

    def get(
        self, atlas: str, scale: str, stat_edge: str, return_connectome: bool = True
    ) -> dict:
        """
        Get the connectome for a specific atlas, scale and statistic.

        Parameters
        ----------
        atlas : str
            Name of the atlas.
        scale : str
            Scale of the connectome.
        stat_edge : str
            Statistic of the connectome.
        return_connectome : bool
            Return the connectome, by default True

        Returns
        -------
        dict
            Connectome for the specific atlas, scale and statistic.
        """
        outputs = self.outputs
        scale_mask = (
            outputs["scale"] == scale if scale is not None else outputs["scale"].isna()
        )
        connectome = outputs[
            (outputs["atlas"] == atlas)
            & scale_mask
            & (outputs["stat_edge"] == stat_edge)
        ]
        if return_connectome:
            return pd.read_csv(connectome["connectome"].values[0], header=None)
        return Path(connectome["connectome"].values[0])

    @property
    def base_inputs(self) -> dict:
        """
        Return the base inputs for the connectome reconstruction.

        Returns
        -------
        dict
            Base inputs for the connectome reconstruction.
        """
        return {
            "in_tracts": self.mapper.files.get("tracts"),
            "in_nodes": self.mapper.files.get("nodes"),
            "nthreads": self.nthreads,
        }

    @property
    def outputs(self) -> dict:
        """
        Return the outputs for the connectome reconstruction.

        Returns
        -------
        dict
            Outputs for the connectome reconstruction.
        """
        return self.run()
