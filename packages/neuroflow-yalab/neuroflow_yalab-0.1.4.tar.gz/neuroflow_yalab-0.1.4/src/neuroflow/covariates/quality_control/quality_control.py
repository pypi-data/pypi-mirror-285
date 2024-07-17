import json
import shutil
import warnings
from pathlib import Path
from typing import ClassVar, Optional, Union

from nipype.interfaces import fsl

from neuroflow.covariates import Covariate
from neuroflow.covariates.quality_control.qc_diffusion_data import DiffusionQC
from neuroflow.covariates.quality_control.utils import BASE_JSON_KEYS, QC_JSON
from neuroflow.files_mapper.files_mapper import FilesMapper


class QualityControl(Covariate):
    """
    Class to handle the quality control covariates

    Attributes
    ----------
    mapper : FilesMapper
        The mapper to the files

    Methods
    -------
    get_covariates() -> dict
        Get the quality control covariates
    """

    EDDY_QC_FLAG: ClassVar = "qc.json"

    EDDY_QC_JSON_PARSER: ClassVar = QC_JSON

    COVARIATE_SOURCE: ClassVar = "QC"
    DIRECTORY_NAME: ClassVar = "quality_control"

    def __init__(self, mapper: FilesMapper, output_directory: Union[str, Path]):
        """
        Constructor for the QualityControl class

        Parameters
        ----------
        mapper : FilesMapper
            The mapper to the files
        """
        super().__init__(mapper, output_directory)

    def _fix_file_name(self, file: Path):
        """
        Fix the file name

        Parameters
        ----------
        file : Path
            The file to fix the name
        """
        new_file = file.with_name(file.name.replace("data.nii.gz.", "data."))
        return new_file

    def _pre_eddy_qc(self):
        """
        Prepare the eddy quality control
        """
        base_dir = self.mapper.files.get("bval_file").parent
        changed_files = {}
        for file in base_dir.glob("data.nii.gz.*"):
            # Rename the files
            new_file = self._fix_file_name(file)
            changed_files[str(file)] = str(new_file)
            file.rename(new_file)
        return changed_files

    def _post_eddy_qc(self, changed_files: dict):
        """
        Post process the eddy quality control
        """
        for old_file, new_file in changed_files.items():
            file = Path(new_file)
            file.rename(old_file)

    def _prepare_inputs(
        self,
        diffusion_qc: DiffusionQC,
    ):
        inputs = {
            "bval_file": self._fix_file_name(self.mapper.files.get("bval_file")),
            "bvec_file": self._fix_file_name(self.mapper.files.get("bvec_file")),
            "mask_file": self._fix_file_name(self.mapper.files.get("b0_brain_mask")),
            "idx_file": self._fix_file_name(diffusion_qc.files.get("index_file")),
            "param_file": self._fix_file_name(self.mapper.files.get("param_file")),
        }
        inputs["base_name"] = str(inputs["bval_file"].parent / "data")
        return inputs

    def _run_eddy_qc(self, diffusion_qc: DiffusionQC, force: Optional[bool] = False):
        """
        Run the eddy quality control

        Parameters
        ----------
        force : Optional[bool], optional
            Force the processing of the data, by default False
        """
        output_directory = self.output_directory / "eddy_qc"
        if force and output_directory.exists():
            shutil.rmtree(str(output_directory))
        flag = Path(output_directory / self.EDDY_QC_FLAG)
        if flag.exists():
            return flag
        inputs = self._prepare_inputs(diffusion_qc=diffusion_qc)
        changed_files = self._pre_eddy_qc()
        try:
            eddy_qc = fsl.EddyQuad(**inputs)
            eddy_qc.inputs.output_dir = str(output_directory)
            res = eddy_qc.run()
        except Exception as e:
            warnings.warn(f"Failed to run eddy quality control: {e}")
            self._post_eddy_qc(changed_files)
            return None
        self._post_eddy_qc(changed_files)
        return Path(res.outputs.qc_json)

    def get_quality_control(self, force: Optional[bool] = False):
        """
        Parse the quality control json

        Parameters
        ----------
        qc_json : Path
            The path to the quality control json
        force : Optional[bool], optional
            Force the processing of the data, by default False
        """
        dqc = DiffusionQC(self.mapper.files)
        result = dqc.query()
        qc_json = self._run_eddy_qc(diffusion_qc=dqc, force=force)
        if qc_json is None:
            # update BASE_JSON_KEYS with None
            for key in BASE_JSON_KEYS:
                result[key] = None
            return result
        with qc_json.open("r") as f:
            qc_dict = json.load(f)
        for key, value in self.EDDY_QC_JSON_PARSER.items():
            value = value["func"](qc_dict, **value["keys"])
            if isinstance(value, dict):
                result.update(value)
            else:
                result[key] = value
        return result

    def get_covariates(self, force: Optional[bool] = False) -> dict:
        """
        Get the quality control covariates

        Returns
        -------
        dict
            The quality control covariates
        force : Optional[bool], optional
            Force the processing of the data, by default False
        """
        return {"quality_control": self.get_quality_control(force=force)}
