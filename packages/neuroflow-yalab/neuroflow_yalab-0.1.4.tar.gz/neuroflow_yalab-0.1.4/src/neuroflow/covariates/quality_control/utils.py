import numpy as np


def calculate_snr(data: np.ndarray, mask: np.ndarray) -> float:
    """
    Calculate the signal-to-noise ratio of the data.

    Parameters
    ----------
    data : np.ndarray
        The data
    mask : np.ndarray
        The mask

    Returns
    -------
    float
        The signal-to-noise ratio
    """
    signal = data[mask]
    noise = np.std(data[~mask])
    return np.nanmean(signal) / noise


def parse_pct_b_outliers(
    qc_dict: dict,
    key: str = "qc_outliers_b",
    pct_key: str = "pct_outliers_b",
    unique_b_key="data_unique_bvals",
):
    """
    Parse the percentage of outliers per b value.

    Parameters
    ----------
    pcts : list
        The list of percentages
    """
    result = {}
    pcts = qc_dict[key]
    bvalues = qc_dict[unique_b_key]
    for bval, pct in zip(bvalues, pcts):
        result[f"{pct_key}{bval}"] = pct
    return result


def parse_params_avg(qc_dict: dict, key: str = "qc_params_avg"):
    """
    Parse the average parameters
    """
    result = {}
    keys = []
    for i in ["translation", "rotation"]:
        for j in ["x", "y", "z"]:
            keys.append(f"avg_{i}_{j}")
    keys += [f"std_ec_term_{j}" for j in ["x", "y", "z"]]
    params = qc_dict[key]
    for key, param in zip(keys, params):
        result[key] = param
    return result


def get(qc_dict: dict, key: str):
    """
    Get the value from the dictionary
    """
    return qc_dict[key]


QC_JSON = {
    "avg_abs_mot": {"func": get, "keys": {"key": "qc_mot_abs"}},
    "avg_rel_mot": {"func": get, "keys": {"key": "qc_mot_rel"}},
    "pct_outliers_b": {"func": parse_pct_b_outliers, "keys": {"key": "qc_outliers_b"}},
    "pct_outliers_total": {"func": get, "keys": {"key": "qc_outliers_tot"}},
    "qc_params_avg": {"func": parse_params_avg, "keys": {"key": "qc_params_avg"}},
}

BASE_JSON_KEYS = [
    "avg_abs_mot",
    "avg_rel_mot",
    "pct_outliers_b1000",
    "pct_outliers_b2000",
    "pct_outliers_b4000",
    "pct_outliers_total",
    "avg_translation_x",
    "avg_translation_y",
    "avg_translation_z",
    "avg_rotation_x",
    "avg_rotation_y",
    "avg_rotation_z",
    "std_ec_term_x",
    "std_ec_term_y",
    "std_ec_term_z",
]
