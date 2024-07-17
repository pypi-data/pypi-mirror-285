from pathlib import Path
from typing import Callable, Union

import nibabel as nib
import numpy as np
import pandas as pd


def parcellate(
    atlas_entities: dict, metric_image: Union[str, Path], measure: Callable
) -> pd.DataFrame:
    """
    Collects a measure for each region of an atlas.

    Parameters
    ----------
    atlas_entities : dict
        Dictionary with the entities of the atlas.
    metric_image : Union[str,Path]
        Path to the metric image.
    measure : Callable
        Measure function.

    Returns
    -------
    pd.DataFrame
        Dataframe with the measure for each region of the atlas.
    """
    atlas_description = pd.read_csv(
        atlas_entities["description_file"], index_col=atlas_entities["index_col"]
    ).copy()
    atlas_description["value"] = np.nan
    atlas_data = nib.load(atlas_entities["nifti"]).get_fdata()
    metric_data = nib.load(metric_image).get_fdata()
    for i, row in atlas_description.iterrows():
        region = int(row[atlas_entities["region_col"]])
        roi_mask = atlas_data == region
        measure_value = measure(metric_data[roi_mask])
        atlas_description.loc[i, "value"] = measure_value
    return atlas_description
