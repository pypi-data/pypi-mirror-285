"""
-----------------------------------------------------------------------------------------
freqfilters module
-----------------------------------------------------------------------------------------
Provides basic frequency domain filters. 
"""

import numpy as np


def ideal_lpf(size: tuple, distance: float) -> np.ndarray:
    """Ideal low-pass filter in the frequency domain.

    Args:
        size (tuple): Size of the filter.

        distance (float): Distance to the center frequency.

    Returns:
        np.ndarray: Filter image in the frequency domain.
    """

    x_grid, y_grid = np.meshgrid(np.arange(size[1]), np.arange(size[0]))

    d = np.sqrt((x_grid - (size[1] // 2)) ** 2 + (y_grid - (size[0] // 2)) ** 2)

    return (d < distance) * 1


def butterworth_lpf(size: tuple, d0: float, order: int = 2) -> np.ndarray:
    """Butterworth low-pass filter in the frequency domain.

    Args:
        size (tuple): Size of the filter.

        d0 (float): Distance threshold.

        order (int, optional): Filter order.
        Defaults to 2.

    Returns:
        np.ndarray: Filter image in the frequency domain.
    """
    x_grid, y_grid = np.meshgrid(np.arange(size[1]), np.arange(size[0]))

    d = np.sqrt((x_grid - size[1] // 2) ** 2 + (y_grid - size[0] // 2) ** 2)

    return 1 / (1 + np.float_power(d / d0, 2 * order))


def gaussian_lpf(size: tuple, d0: float) -> np.ndarray:
    """Gaussian low-pass filter in the frequency domain.

    Args:
        size (tuple): Size of the filter.

        d0 (float): Distance threshold.

    Returns:
        np.ndarray: Filter image in the frequency domain.
    """
    x_grid, y_grid = np.meshgrid(np.arange(size[1]), np.arange(size[0]))

    d = np.sqrt((x_grid - size[1] // 2) ** 2 + (y_grid - size[0] // 2) ** 2)

    return np.exp((-(d**2)) / (2 * (d0**2)))
