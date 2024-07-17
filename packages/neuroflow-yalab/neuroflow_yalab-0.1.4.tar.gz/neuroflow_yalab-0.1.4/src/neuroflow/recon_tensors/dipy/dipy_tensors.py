"""
Reconstruction of diffusion tensors from the diffusion signal using Dipy.
"""

import warnings
from pathlib import Path
from typing import Optional, Union

from dipy.workflows.reconst import ReconstDtiFlow

from neuroflow.files_mapper.files_mapper import FilesMapper
from neuroflow.recon_tensors.dipy.outputs import OUTPUTS
from neuroflow.recon_tensors.recon_tensors import ReconTensors

warnings.filterwarnings("ignore")


class DipyTensors(ReconTensors):
    """
    Reconstruction of diffusion tensors from the diffusion signal using Dipy.
    """

    OUTPUTS = OUTPUTS

    def __init__(
        self,
        mapper: FilesMapper,
        output_directory: Union[str, Path],
        max_bvalue: Optional[int] = 1000,
        bval_tol: Optional[int] = 50,
        fit_method: Optional[str] = "NLLS",
    ):
        """
        Initialize the DipyTensors class.

        Parameters
        ----------
        mapper : FilesMapper
            An instance of FilesMapper class.
        out_dir : Union[str, Path]
            Path to the output directory.
        max_bvalue : int
            Maximum b-value to use for the reconstruction.
        """
        super().__init__(
            mapper=mapper,
            output_directory=output_directory,
            max_bvalue=max_bvalue,
            bval_tol=bval_tol,
        )
        self.fit_method = fit_method
        self.software = "dipy"

    def collect_inputs(self) -> dict:
        """
        Gather inputs for the DipyTensors workflow.

        Returns
        -------
        dict
            Inputs for the DipyTensors workflow.
        """
        inputs = {
            "input_files": self.filtered_files.get("dwi_file"),
            "bvalues_files": self.filtered_files.get("bval_file"),
            "bvectors_files": self.filtered_files.get("bvec_file"),
            "mask_files": self.mapper.files.get("b0_brain_mask"),
            "out_dir": self.output_directory / self.software,
            "fit_method": self.fit_method,
        }
        return {key: str(value) for key, value in inputs.items()}

    def run(self, force: bool = False) -> dict:
        """
        Run the DipyTensors workflow.

        Returns
        -------
        dict
            Outputs for the DipyTensors workflow.
        """
        inputs = self.collect_inputs()
        outputs = self.collect_outputs()
        out_dir = Path(inputs["out_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)
        if force:
            for file in outputs.values():
                file.unlink(missing_ok=True)
        flow = ReconstDtiFlow()
        flow.run(
            **inputs, **{f"out_{key}": str(value) for key, value in outputs.items()}
        )
        return outputs
