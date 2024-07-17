"""
Reconstruction of diffusion tensors from the diffusion signal using mrtrix3.
"""

import warnings
from pathlib import Path
from typing import Union

from nipype.interfaces.mrtrix3 import FitTensor, TensorMetrics

from neuroflow.files_mapper.files_mapper import FilesMapper
from neuroflow.recon_tensors.mrtrix3.outputs import OUTPUTS
from neuroflow.recon_tensors.recon_tensors import ReconTensors

warnings.filterwarnings("ignore")


class MRTrix3Tensors(ReconTensors):
    """
    Reconstruction of diffusion tensors from the diffusion signal using Dipy.
    """

    OUTPUTS = OUTPUTS

    def __init__(
        self,
        mapper: FilesMapper,
        output_directory: Union[str, Path],
        max_bvalue: int = 1000,
        bval_tol: int = 50,
        nthreas: int = 1,
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
        self.software = "mrtrix3"
        self.nthreads = nthreas

    def collect_inputs(self) -> dict:
        """
        Gather inputs for the DipyTensors workflow.

        Returns
        -------
        dict
            Inputs for the DipyTensors workflow.
        """
        inputs = {
            "in_file": self.filtered_files.get("dwi_file"),
            "grad_fsl": (
                self.filtered_files.get("bvec_file"),
                self.filtered_files.get("bval_file"),
            ),
            "in_mask": self.mapper.files.get("b0_brain_mask"),
            "out_dir": self.output_directory / self.software,
        }
        return {key: str(value) for key, value in inputs.items()}

    def fit_tensor(self, force: bool = False) -> Path:
        """
        Fit the diffusion tensor to the diffusion signal.
        """
        inputs = self.collect_inputs()
        out_dir = Path(inputs["out_dir"])
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = (
            out_dir / f"sub-{self.mapper.subject}_ses-{self.mapper.session}_tensor.mif"
        )
        if force:
            out_file.unlink(missing_ok=True)
        if out_file.exists():
            return out_file
        fit_tensor = FitTensor()
        fit_tensor.inputs.in_file = self.filtered_files.get("dwi_file")
        fit_tensor.inputs.grad_fsl = (
            self.filtered_files.get("bvec_file"),
            self.filtered_files.get("bval_file"),
        )
        fit_tensor.inputs.in_mask = self.mapper.files.get("b0_brain_mask")
        fit_tensor.inputs.out_file = out_file
        fit_tensor.inputs.nthreads = self.nthreads
        fit_tensor.run()
        return out_file

    def run(self, force: bool = False) -> dict:
        """
        Run the MRTrix3Tensors workflow.

        Returns
        -------
        dict
            Outputs for the MRTrix3Tensors workflow.
        """
        tensor = self.fit_tensor(force=force)
        outputs = self.collect_outputs()
        if force:
            for file in outputs.values():
                file.unlink(missing_ok=True)
        if all([output.exists() for output in outputs.values()]):  # noqa
            return outputs
        tensor_metrics = TensorMetrics(
            **{f"out_{key}": str(value) for key, value in outputs.items()}
        )
        tensor_metrics.inputs.in_file = tensor
        tensor_metrics.inputs.nthreads = self.nthreads
        tensor_metrics.run()
        return outputs
