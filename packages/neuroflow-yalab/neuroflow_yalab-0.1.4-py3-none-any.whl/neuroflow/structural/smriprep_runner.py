import os
import shutil
import subprocess
import warnings
from copy import deepcopy
from pathlib import Path
from typing import ClassVar, Dict, Optional, Union

from neuroflow.files_mapper.files_mapper import FilesMapper
from neuroflow.structural.outputs import SMRIPREP_OUTPUTS as OUTPUTS
from neuroflow.structural.utils import build_smriprep_command


class SMRIPrepRunner:
    """
    Run the sMRIPrep pipeline on the input data.
    """

    DIRECTORY_NAME: ClassVar = "smriprep"
    BIDS_DIRECTORY: ClassVar = "bids"

    T1_DESTINATION: ClassVar = (
        "{bids_directory}/sub-{subject}/ses-{session}/anat/sub-{subject}_ses-{session}_T1w.nii.gz"  # noqa: E501
    )
    T1_key = "t1w"

    # Output files
    OUTPUTS: ClassVar = OUTPUTS.copy()

    def __init__(
        self,
        mapper: FilesMapper,
        output_directory: Union[str, Path],
        fs_license_file: Optional[Path] = None,
        nthreads: int = 1,
    ):
        self.mapper = mapper
        self.output_directory = self._gen_output_directory(output_directory)
        self.bids_directory = self._gen_bids_directory()
        self.fs_license_file = self._get_fs_license_file(fs_license_file)
        self.nthreads = nthreads

    def _get_fs_license_file(self, fs_license_file: Path) -> Path:
        """
        Get the FreeSurfer license file.

        Parameters
        ----------
        fs_license_file : Path
            Path to the FreeSurfer license file.

        Returns
        -------
        Path
            Path to the FreeSurfer license file.
        """
        if not fs_license_file:
            if os.getenv("FS_LICENSE"):
                return Path(os.getenv("FS_LICENSE"))
            else:
                fs_home = os.getenv("FREESURFER_HOME")
                fs_license_file = Path(fs_home) / "license.txt"
                if not fs_license_file.exists():
                    raise ValueError("FreeSurfer license file not found.")
        return Path(fs_license_file)

    def _gen_bids_directory(self) -> Path:
        """
        Generate the BIDS directory for the sMRIPrep pipeline.

        Returns
        -------
        Path
            Path to the BIDS directory.
        """
        bids_directory = Path(self.output_directory) / self.BIDS_DIRECTORY
        t1_destination = Path(
            self.T1_DESTINATION.format(
                bids_directory=bids_directory,
                subject=self.mapper.subject,
                session=self.mapper.session,
            )
        )
        if not t1_destination.exists():
            t1_destination.parent.mkdir(parents=True, exist_ok=True)
            # make a copy of the T1w image (not symlink)
            t1_source = self.mapper.files.get(self.T1_key)
            shutil.copy(t1_source, t1_destination)

        return bids_directory

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
        if not all(flags):
            output_directory = (
                Path(output_directory)
                / f"sub-{self.mapper.subject}"
                / f"ses-{self.mapper.session}"
            )
        output_directory.mkdir(parents=True, exist_ok=True)
        return output_directory

    def run(self, force: bool = False):
        """
        Run the sMRIPrep pipeline.
        """
        command = build_smriprep_command(
            bids_directory=self.bids_directory,
            output_directory=self.output_directory,
            fs_license_file=self.fs_license_file,
            subject_id=self.mapper.subject,
            nthreads=self.nthreads,
        )
        if not force:
            output_files = self.collect_output_paths(strict=False)
            if all(
                [output is not None for output in output_files.get("smriprep").values()]
            ):
                print(
                    f"Output files already exist for subject {self.mapper.subject}. Skipping sMRIPrep."  # noqa: E501
                )
                return
        print("Running sMRIPrep pipeline...")
        print(" ".join(command))
        try:
            result = subprocess.run(command, check=True, text=True, capture_output=True)
            print(
                f"sMRIPrep completed successfully for subject {self.mapper.subject}.\n{result.stdout}"  # noqa: E501
            )
        except subprocess.CalledProcessError as e:
            print(
                f"Error running sMRIPrep for subject {self.mapper.subject}.\n{e.stderr}"
            )

    def collect_output_paths(self, strict: bool = True) -> Dict[str, Path]:
        """
        Collect paths to the outputs generated by sMRIPrep.

        Parameters:
        strict : bool
            If True, raise an error if any of the output files are missing.

        Returns:
            A dictionary containing paths to the output files.
        """
        output_files = deepcopy(self.OUTPUTS)
        for base_path, outputs_format in self.OUTPUTS.items():
            for key, output in outputs_format.items():
                filename = output.format(
                    subject=self.mapper.subject, session=self.mapper.session
                )
                result = Path(self.output_directory / base_path / filename)
                if not result.exists():
                    if strict:
                        raise FileNotFoundError(f"File not found: {result}")
                    else:
                        warnings.warn(f"File not found: {result}")
                        result = None
                output_files[base_path][key] = result

        return output_files

    @property
    def outputs(self) -> Dict[str, Path]:
        """
        Get the output files generated by sMRIPrep.

        Returns:
            A dictionary containing paths to the output files.
        """
        return self.collect_output_paths(strict=False)
