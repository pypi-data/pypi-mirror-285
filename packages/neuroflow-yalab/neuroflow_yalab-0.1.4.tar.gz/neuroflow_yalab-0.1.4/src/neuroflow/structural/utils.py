from pathlib import Path


def build_smriprep_command(
    bids_directory: Path,
    output_directory: Path,
    fs_license_file: Path,
    subject_id: str,
    nthreads: int = 1,
):
    """
    Build the sMRIPrep command.

    Parameters
    ----------
    bids_directory : Path
        Path to the BIDS directory.
    output_directory : Path
        Path to the output directory.
    fs_license_file : Path
        Path to the FreeSurfer license file.
    subject_id : str
        Subject ID to process.

    Returns
    -------
    _type_
        _description_
    """
    return [
        "docker",
        "run",
        "--rm",
        # "-it",
        "-v",
        f"{Path(bids_directory).resolve()}:/data:ro",
        "-v",
        f"{output_directory.resolve()}:/out",
        "-v",
        f"{Path(fs_license_file).resolve()}:/fs_license",
        "nipreps/smriprep:0.15.0",
        "/data",
        "/out",
        "participant",
        "--participant-label",
        subject_id,
        "--fs-license-file",
        "/fs_license",
        "--output-spaces",
        "MNI152NLin2009cAsym",
        "--nthreads",
        str(nthreads),
    ]
