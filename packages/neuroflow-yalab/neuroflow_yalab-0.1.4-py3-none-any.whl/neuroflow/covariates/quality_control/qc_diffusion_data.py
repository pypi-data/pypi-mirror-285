import nibabel as nib
import pandas as pd

from neuroflow.covariates.quality_control.striping_effect import calculate_strip_score


class DiffusionQC:
    def __init__(
        self,
        files: dict,
    ):
        self.files = files
        self._update_index_file()

    def _read_index_file(self) -> list:
        """
        Read the index file.

        Returns
        -------
        list
            List of lines in the index file.
        """
        index_file = self.files.get("index_file")
        with open(index_file, "r") as f:
            return f.readlines()

    def _read_bval_file(self) -> list:
        """
        Read the bval file.

        Returns
        -------
        list
            List of b-values.
        """
        bval_file = self.files.get("bval_file")
        return (
            pd.read_csv(bval_file, header=None, sep=" ", index_col=None)
            .values[0]
            .tolist()
        )

    def _read_bvec_file(self) -> list:
        """
        Read the bvec file.

        Returns
        -------
        list
            List of b-vectors.
        """
        bvec_file = self.files.get("bvec_file")
        res = pd.read_csv(bvec_file, header=None, sep=" ", index_col=None).dropna(
            axis=1
        )
        return [
            tuple([res.iloc[0, i], res.iloc[1, i], res.iloc[2, i]])
            for i in range(res.shape[1])
        ]

    def validate_index_file(self):
        """
        Validate the index file.

        Returns
        -------
        bool
            True if the index file is valid.
        """
        n_index = len(self.index)
        n_bval = len(self.bvalues)
        return n_index == n_bval

    def _update_index_file(self):
        """
        Update the index file.
        If the number of indices is different from the number of b-values,
        create a new index file with the correct number of indices.
        """
        if self.validate_index_file():
            return
        updated_index_file = self.files.get("index_file").with_name("index_updated.txt")
        n_bval = len(self.bvalues)
        with open(updated_index_file, "w") as f:
            for i in range(n_bval):
                f.write("1\n")
        self.files["index_file"] = updated_index_file

    def query_bval(self) -> dict:
        """
        Query the b-values.

        Returns
        -------
        dict
            Dictionary with the b-values.
        """
        bval = self.bvalues
        return {
            "max_bval": max(bval),
            "min_bval": min(bval),
            "n_unique_bvals": len(set(bval)),
        }

    def query_bvec(self) -> dict:
        """
        Query the b-vectors.

        Returns
        -------
        dict
            Dictionary with the b-vectors.
        """
        bvec = self.bvectors
        return {
            "n_directions": len(set(bvec)),
        }

    def query_striping_score(self):
        """
        Query the striping score.

        Returns
        -------
        float
            Striping score.
        """
        return {"striping_score": calculate_strip_score(self.b0_brain)}

    def query_diffusion_nifti(self):
        """
        Query the diffusion NIfTI file.

        Returns
        -------
        nibabel.nifti1.Nifti1Image
            Diffusion NIfTI file.
        """
        header = self.b0_brain.header
        zooms = header.get_zooms()
        result = {}
        for dim, dim_number in zip(["x", "y", "z"], zooms):
            result[f"voxel_size_{dim}"] = dim_number
        return result

    def query(self):
        """
        Query the diffusion data.

        Returns
        -------
        dict
            Dictionary with the diffusion data.
        """
        return {
            **self.query_bval(),
            **self.query_bvec(),
            **self.query_striping_score(),
            **self.query_diffusion_nifti(),
        }

    @property
    def index(self) -> list:
        """
        Get the index file.

        Returns
        -------
        list
            List of lines in the index file.
        """
        return self._read_index_file()

    @property
    def bvalues(self) -> list:
        """
        Get the bval file.

        Returns
        -------
        list
            List of b-values.
        """
        return self._read_bval_file()

    @property
    def bvectors(self):
        return self._read_bvec_file()

    @property
    def b0_brain(self):
        return nib.load(self.files.get("b0_brain"))

    @property
    def diffusion_nifti(self):
        return nib.load(self.files.get("dwi_file"))
