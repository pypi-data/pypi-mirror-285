from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from scipy.fft import fft, fftfreq


def calculate_strip_score(
    input_file: Union[str, Path],
    axis=2,
    target_freq=0.25,
    freq_tolerance=0.05,
    visualize=False,
) -> float:
    """
    Calculate the striping score of a given NIfTI file along a given axis.

    Parameters
    ----------
    input_file : Union[str, Path]
        The input NIfTI file
    axis : int, optional
        The axis along which to calculate the striping score, by default 2
    target_freq : float, optional
        The target frequency to detect striping, by default 0.25
    freq_tolerance : float, optional
        The frequency tolerance to detect striping, by default 0.05

    Returns
    -------
    float
        The striping score
    """
    if isinstance(input_file, str) or isinstance(input_file, Path):
        input_file = nib.load(input_file)
    data = input_file.get_fdata()

    # Load the NIfTI file
    # Compute the mean signal profile along the given axis
    mean_profile = np.mean(data, axis=tuple(i for i in range(data.ndim) if i != axis))

    # Perform Fourier transform to compute the power spectrum
    N = len(mean_profile)
    yf = fft(mean_profile)
    xf = fftfreq(N, 1)[: N // 2]

    # Compute the power spectrum
    power_spectrum = 2.0 / N * np.abs(yf[: N // 2])

    # Find the indices of the frequencies that match the target frequency
    freq_indices = np.where(
        (xf >= target_freq - freq_tolerance) & (xf <= target_freq + freq_tolerance)
    )[0]

    # Calculate the sum of the power spectrum at the target frequency
    strip_score = np.sum(power_spectrum[freq_indices])

    # Optional visualization
    if not visualize:
        return strip_score
    plt.plot(xf, power_spectrum)
    plt.axvline(
        target_freq - freq_tolerance,
        color="r",
        linestyle="--",
        label="Frequency Tolerance",
    )
    plt.axvline(target_freq + freq_tolerance, color="r", linestyle="--")
    plt.title("Power Spectrum (Striping Detection)")
    plt.xlabel("Frequency")
    plt.ylabel("Power")
    plt.legend()
    plt.grid(True)
    plt.show()

    return strip_score
