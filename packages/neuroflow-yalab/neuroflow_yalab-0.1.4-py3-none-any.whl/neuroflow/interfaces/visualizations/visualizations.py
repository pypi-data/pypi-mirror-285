"""
This module contains a utility class for creating
publication-ready visualizations.
"""

from pathlib import Path
from typing import Union

import matlab
import matlab.engine
import nibabel as nib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from mne.viz import circular_layout
from mne_connectivity.viz import plot_connectivity_circle
from neuromaps.datasets import fetch_fslr
from neuromaps.transforms import mni152_to_fslr
from nipype.interfaces import fsl
from surfplot import Plot
from tqdm import tqdm


def map_groups_to_colors(group_labels):
    """
    Map group labels to RGBA colors.

    Parameters
    ----------
    group_labels : list
        List of group labels.

    Returns
    -------
    list
        List of RGBA colors.
    """
    unique_groups = np.unique(group_labels)
    num_unique_groups = len(unique_groups)
    rgba_colors = plt.cm.get_cmap("tab20", num_unique_groups)(
        np.linspace(0, 1, num_unique_groups)
    )
    color_mapping = {group: rgba_colors[i] for i, group in enumerate(unique_groups)}
    return [color_mapping[str(group)] for group in group_labels], color_mapping


def generate_template() -> str:
    """
    Generate a template for the surface plot.

    Returns
    -------
    str
        Template for the surface plot.
    """
    return fsl.Info.standard_image("MNI152_T1_1mm_brain.nii.gz")


class Visualizations:
    """
    A utility class for creating publication-ready visualizations.
    """

    @staticmethod
    def df_to_nifti(
        df: pd.DataFrame,
        labeled_img_path: Union[Path, str],
        value_column: str,
        match_by: str = "Label",
        silent=True,
    ) -> nib.Nifti1Image:
        """
        Convert a dataframe to a nifti image.

        Parameters
        ----------
        df : pd.DataFrame
            Dataframe to convert.
        labeled_img_path : Path
            Path to the labeled image.
        value_column : str
            Column name of the value to use.
        match_by : str
            Column name to match the dataframe to the labeled image, by default "Label".

        Returns
        -------
        nib.Nifti1Image
            Nifti image with the labels replaced with those in *df*.
        """
        if not silent:
            print(
                f"""Converting dataframe to nifti...
                Matching column: {match_by}.
                Value column: {value_column}."""
            )
        labeled_img = nib.load(str(labeled_img_path))
        labeled_img_data = labeled_img.get_fdata()
        template_data = np.zeros_like(labeled_img_data)
        for _, row in tqdm(df.iterrows()):
            label = row[match_by]
            value = row[value_column]
            template_data[labeled_img_data == label] = value
        return nib.Nifti1Image(template_data, labeled_img.affine, labeled_img.header)

    @staticmethod
    def nifti_to_surface_matlab(
        values: list,
        atlas_path: Union[str, Path],
        save_path: Union[str, Path],
        template_path: Union[str, Path] = None,
        cmap: str = "RdBu_r",
        vmin: float = None,
        vmax: float = None,
    ):
        """
        Plot surface plot of nifti image using MATLAB.

        Parameters
        ----------
        nifti : Union[str, Path, nib.Nifti1Image]
            Nifti image to plot.
        template_path : Union[str, Path], optional
            Path to the template, by default None
        cmap : str, optional
            Colormap to use, by default "RdBu_r"
        save_path : Union[str, Path], optional
            Path to save the plot, by default None
        vmin : float, optional
            Minimum value for the colormap, by default None
        vmax : float, optional
            Maximum value for the colormap, by default None
        """
        Path(save_path).mkdir(parents=True, exist_ok=True)
        template_path = template_path or generate_template()
        eng = matlab.engine.start_matlab()
        eng.addpath(str(Path(__file__).parent / "matlab_scripts"))
        eng.addpath(str(Path(__file__).parent / "matlab_scripts" / "slanCM"))
        res = eng.df_to_volume(matlab.double(values), str(atlas_path))
        inputs = [res, str(template_path), str(save_path), cmap]
        if (vmin is not None) and (vmax is not None):
            inputs += [matlab.double(vmin), matlab.double(vmax)]
        eng.visualize_surface(
            *inputs,
        )
        eng.quit()

    @staticmethod
    def nifti_to_surface(
        nifti: Union[str, Path, nib.Nifti1Image],
        atlas_path: Union[str, Path],
        cmap: str = "RdBu_r",
        save_path: Union[str, Path] = None,
        vmin: float = None,
        vmax: float = None,
    ):
        """
        Plot surface plot of nifti image.

        Parameters
        ----------
        nifti : Union[str, Path, nib.Nifti1Image]
            Nifti image to plot.
        atlas_path : Union[str, Path]
            Path to the atlas.
        cmap : str
            Colormap to use, by default "RdBu_r".
        save_path : Union[str, Path]
            Path to save the plot, by default None.
        vmin : float
            Minimum value for the colormap, by default None.
        vmax : float
            Maximum value for the colormap, by default None.
        """

        atlas_lh, atlas_rh = mni152_to_fslr(
            atlas_path, fslr_density="164k", method="nearest"
        )
        surf_data_lh, surf_data_rh = mni152_to_fslr(nifti, fslr_density="164k")
        surfaces = fetch_fslr(density="164k")
        lh, rh = surfaces["inflated"]
        p = Plot(
            surf_lh=lh,
            surf_rh=rh,
            size=(1200, 1000),
        )
        # show figure, as you typically would with matplotlib
        sulc_lh, sulc_rh = surfaces["sulc"]
        # p.add_layer({'left': sulc_lh, 'right': sulc_rh}, cmap='binary_r', cbar=False)
        p.add_layer(
            {"left": surf_data_lh, "right": surf_data_rh},
            cmap=cmap,
            cbar=True,
            color_range=(vmin, vmax),
        )
        p.add_layer(
            {"left": atlas_lh, "right": atlas_rh},
            cbar=False,
            as_outline=True,
            cmap="gray",
        )
        fig = p.build()
        if save_path is not None:
            fig.savefig(
                save_path,
                transparent=True,
                dpi=300,
            )
            plt.close()

    @staticmethod
    def plot_connectome_circle(
        parcels: pd.DataFrame, parcellation: str, con: np.ndarray, threshold: float
    ):
        """
        Plot a connectome circle plot.

        Parameters
        ----------
        con : np.ndarray
            Connectivity matrix.
        labels : list
            List of labels.
        save_path : Union[str, Path], optional
            Path to save the plot, by default None
        """
        p = parcels.copy()
        if parcellation == "huang2022":
            p["Hemi"] = p["RegionName1"].apply(lambda x: x.split("_")[0])
            lobes_identifier = "CortexDivision_name"
            hemispheres_identifier = "Hemi"
            node_labels_identifier = "Long_name"
            lobes = p[lobes_identifier].to_list()
            # hemispheres = p[hemispheres_identifier].to_list()
            node_labels = p[node_labels_identifier].to_list()
            lh_labels = [
                p.loc[i, node_labels_identifier]
                for i in p.index
                if p.loc[i, hemispheres_identifier] == "L"
            ]
            rh_labels = [
                p.loc[i, node_labels_identifier]
                for i in p.index
                if p.loc[i, hemispheres_identifier] == "R"
            ]
            node_order = lh_labels[::-1] + rh_labels
            label_names = ["_".join(label.split("_")[:-1]) for label in node_labels]
            node_angles = circular_layout(
                node_labels,
                node_order,
                start_pos=90,
                group_boundaries=[0, len(node_labels) / 2],
            )

        elif parcellation == "fan2016":
            lobes_identifier = "Yeo_7network_name"
            hemispheres_identifier = "Hemi"
            node_labels_identifier = "Label"
            p_vis = p.sort_values(by=[hemispheres_identifier, lobes_identifier])
            lobes = p[lobes_identifier].to_list()
            # hemispheres = p[hemispheres_identifier].to_list()
            node_labels = p[node_labels_identifier].to_list()
            lh_labels = [
                p.loc[i, "Label"] for i in p_vis.index if p.loc[i, "Hemi"] == "L"
            ]
            rh_labels = [
                p.loc[i, "Label"] for i in p_vis.index if p.loc[i, "Hemi"] == "R"
            ]
            cereb_labels = [
                p.loc[i, "Label"] for i in p_vis.index if pd.isna(p.loc[i, "Hemi"])
            ]
            node_order = lh_labels[::-1] + rh_labels + cereb_labels
            rh_boudary = len(lh_labels)
            cereb_boundary = len(lh_labels) + len(rh_labels)
            node_angles = circular_layout(
                node_labels,
                node_order,
                start_pos=-67,
                group_boundaries=[0, rh_boudary, cereb_boundary],
            )
            label_names = node_labels

        elif "schaefer" in parcellation:
            lobes_identifier = "network"
            hemispheres_identifier = "hemisphere"
            node_labels_identifier = "index"
            p_vis = p.sort_values(by=[hemispheres_identifier, lobes_identifier])
            lobes = p[lobes_identifier].to_list()
            # hemispheres = p[hemispheres_identifier].to_list()
            node_labels = p[node_labels_identifier].to_list()
            lh_labels = [
                p.loc[i, "index"] for i in p_vis.index if p.loc[i, "hemisphere"] == "L"
            ]
            rh_labels = [
                p.loc[i, "index"] for i in p_vis.index if p.loc[i, "hemisphere"] == "R"
            ]
            cereb_labels = [
                p.loc[i, "index"]
                for i in p_vis.index
                if pd.isna(p.loc[i, "hemisphere"])
            ]
            node_order = lh_labels[::-1] + rh_labels + cereb_labels
            rh_boudary = len(lh_labels)
            node_angles = circular_layout(
                node_labels, node_order, start_pos=90, group_boundaries=[0, rh_boudary]
            )
            label_names = node_labels
        # p = p.sort_values(by=["Hemi","CortexDivision_name"])

        con = pd.DataFrame(con).loc[p.index, p.index].values.astype(float)

        label_names = [
            label if np.any(np.abs(con[i, :]) > threshold) else ""
            for i, label in enumerate(label_names)
        ]
        # set node angels so that the hemispheres are next to each other
        con = np.nan_to_num(con).copy()

        # Automatically map group labels to RGBA colors
        node_colors, color_mapping = map_groups_to_colors(
            lobes
        )  # Customize this line for lobes or other levels

        fig, ax = plt.subplots(
            figsize=(20, 20), facecolor="white", subplot_kw=dict(projection="polar")
        )
        # Create a circular connectome plot using MNE-Python's plot_connectivity_circle
        plot_connectivity_circle(
            con,
            label_names,
            n_lines=100,
            node_angles=node_angles,
            node_colors=node_colors,
            # title="Edge-wise Effects with Automatic Node Colors",
            ax=ax,
            colormap="Reds_r",
            padding=0,
            fontsize_names=0,
            linewidth=10,
            # vmin=-3,
            # vmax=3,
            facecolor="white",
            textcolor="black",
            show=False,
            colorbar=False,
        )

        # Add hemispheric labels and a title
        ax.text(
            0,
            0,
            "L",
            transform=ax.transAxes,
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=50,
            fontweight="bold",
        )
        ax.text(
            1,
            0,
            "R",
            transform=ax.transAxes,
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=50,
            fontweight="bold",
        )

        plt.show()
