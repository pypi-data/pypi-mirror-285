"""
Command line interface for the neuroflow package.
"""

from pathlib import Path

import click

from neuroflow.atlases.atlases import Atlases
from neuroflow.connectome.connectome_reconstructor import ConnectomeReconstructor
from neuroflow.covariates.covariates_collector import CovariatesCollector
from neuroflow.files_mapper.files_mapper import FilesMapper
from neuroflow.parcellation.parcellation import Parcellation
from neuroflow.recon_tensors.dipy.dipy_tensors import DipyTensors
from neuroflow.recon_tensors.mrtrix3.mrtrix3_tensors import MRTrix3Tensors
from neuroflow.structural.smriprep_runner import SMRIPrepRunner

AVAILABLE_STEPS = [
    "dipy_tensors",
    "mrtrix3_tensors",
    "atlases",
    "parcellation_dipy",
    "parcellation_mrtrix3",
    "covariates",
    "connectome_recon",
]


# Example CLI script with a basic command structure
@click.group()  # This decorator defines a group of commands, allowing subcommands
def cli():
    """This is the main entry point for the CLI."""
    pass  # This is just a placeholder for the main CLI group


# Define a subcommand
@cli.command()  # This decorator creates a new command within the CLI group
@click.argument(
    "input_dir", type=click.Path(exists=True)
)  # Require an directory with preprocessing results
@click.argument(
    "output_dir",
    type=click.Path(),
    # help="Output directory for NeuroFlow's results",
)
@click.argument(
    "google_credentials",
    type=click.Path(exists=True),
    # help="Path to the Google credentials file",
)
@click.option(
    "--patterns_file",
    type=click.Path(exists=True),
    help="Path to the patterns file",
)
@click.option(
    "--atlases",
    type=str,
    help="The atlases to use for the analysis",
)
@click.option(
    "--crop_to_gm",
    is_flag=True,
    default=False,
    help="Crop the atlases to the gray matter",
)
@click.option(
    "--use_smriprep",
    is_flag=True,
    default=False,
    help="Use sMRIPrep for the atlases and structural data",
)
@click.option(
    "--fs_license_file",
    type=click.Path(exists=True),
    help="Path to the FreeSurfer license file",
)
@click.option(
    "--max_bval",
    type=int,
    default=1000,
    help="Maximum b-value for diffusion data",
)
@click.option(
    "--ignore_steps",
    type=str,
    help="Ignore specific steps",
)
@click.option(
    "--steps",
    type=str,
    help="Run specific steps",
)
@click.option(
    "--nthreads",
    type=int,
    default=1,
    help="Number of threads to use",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force the processing of the data",
)
def process(
    input_dir: str,
    output_dir: str,
    patterns_file: str,
    google_credentials: str,
    atlases: str,
    crop_to_gm: bool,
    use_smriprep: bool,
    fs_license_file: str,
    max_bval: int,
    ignore_steps: str,
    steps: str,
    nthreads: int,
    force: bool,
):
    """
    Process the preprocessed data for the participant.

    Parameters
    ----------
    input_dir : str
        The path to the preprocessed data
    output_directory : str
        The path to the output directory
    patterns_file : str
        The path to the patterns file
    google_credentials : str
        The path to the Google credentials
    atlases : list
        The atlases to use for the analysis
    max_bval : int
        The maximum b-value for diffusion data
    force : bool
        Force the processing of the data
    """
    atlases = atlases.split(",") if atlases else None
    steps = steps.split(",") if steps else AVAILABLE_STEPS
    ignore_steps = ignore_steps.split(",") if ignore_steps else []
    steps = [step for step in steps if step not in ignore_steps]
    preprocessed_directory = Path(input_dir)
    output_directory = Path(output_dir)
    google_credentials = Path(google_credentials)
    patterns_file = Path(patterns_file) if patterns_file else None
    print("Processing the data...")
    print(f"Preprocessed directory: {preprocessed_directory}")
    print(f"Output directory: {output_directory}")
    print(f"Patterns file: {patterns_file}")
    print(f"Google credentials: {google_credentials}")
    print(f"Atlases: {atlases}")
    print(f"Max b-value: {max_bval}")

    mapper = (
        FilesMapper(path=preprocessed_directory)
        if patterns_file is None
        else FilesMapper(path=preprocessed_directory, patterns=patterns_file)
    )
    if use_smriprep or "smriprep" in steps:
        smriprep_runner = SMRIPrepRunner(
            mapper=mapper,
            output_directory=output_directory,
            fs_license_file=fs_license_file,
            nthreads=nthreads,
        )
        print("Running sMRIPrep...")
        _ = smriprep_runner.run(force=force)
    else:
        smriprep_runner = None
    if "atlases" in steps:
        atlases = Atlases(
            mapper=mapper,
            output_directory=output_directory,
            atlases=atlases,
            crop_to_gm=crop_to_gm,
            use_smriprep=use_smriprep,
            smriprep_runner=smriprep_runner,
        )
        print("Running atlas registrations...")
        _ = atlases.register_atlas_to_t1w(force=force)
        _ = atlases.register_atlas_to_dwi(force=force)
    if "dipy_tensors" in steps:
        dipy_tensors = DipyTensors(
            mapper=mapper, output_directory=output_directory, max_bvalue=max_bval
        )
        parcellation_dipy = Parcellation(
            tensors_manager=dipy_tensors,
            atlases_manager=atlases,
            output_directory=output_directory,
        )
        print("Reconstructing tensors using Dipy...")
        _ = parcellation_dipy.run(force=force)
    if "mrtrix3_tensors" in steps:
        mrtrix3_tensors = MRTrix3Tensors(
            mapper=mapper,
            output_directory=output_directory,
            max_bvalue=max_bval,
            nthreas=nthreads,
        )
        parcellation_mrtrix3 = Parcellation(
            tensors_manager=mrtrix3_tensors,
            atlases_manager=atlases,
            output_directory=output_directory,
        )
        print(
            "Running atlas registrations and parcellations of MRtrix3-derived metrics..."  # noqa: E501
        )
        _ = parcellation_mrtrix3.run(force=force)
    if "covariates" in steps:
        covariates = CovariatesCollector(
            mapper=mapper,
            google_credentials_path=google_credentials,
            output_directory=output_directory,
            force=force,
        )
        print("Collecting covariates...")
        covariates.save_to_file()
    if "connectome_recon" in steps:
        connectome_recon = ConnectomeReconstructor(
            mapper=mapper,
            atlases_manager=atlases,
            output_directory=output_directory,
            nthreads=nthreads,
        )
        print("Reconstructing the connectome...")
        _ = connectome_recon.run(force=force)


if __name__ == "__main__":
    cli()
