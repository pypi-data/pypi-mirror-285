"""
-----------------------------------------------------------------------------------------
filters module
-----------------------------------------------------------------------------------------
Provides basic spatial filters. 
"""

import numpy as np


def average_filter(k: int = 3) -> np.ndarray:
    """Returns the k x k average filter.

    Args:
        k (int): size of the filter (odd).
        Defaults to 3.

    Returns:
        np.ndarray: 'k'x'k' average filter kernel.
    """
    if k % 2 == 1:
        return np.ones((k, k)) / (k**2)
    else:
        raise (ValueError(f"k = {k} must be an odd integer."))


def gauss_filter(k: int = 3, s: float = 1) -> np.ndarray:
    """Provides the k x k Gaussian weighted average filter.
    It is calculated using the separation principle.

    Args:
        k (int, optional): Size of the kernel (odd).
        Defaults to 3.

        s (float, optional): Standard deviation.
        Defaults to 1.

    Returns:
        np.ndarray: 'k'x'k' gaussian weighted average filter kernel.
    """
    if k % 2 == 1:
        g = np.exp(-(np.arange(-(k // 2), (k // 2) + 1) ** 2) / (2 * (s**2)))[
            np.newaxis, :
        ]
        g = g / np.sum(g)

        return g.T * g
    else:
        raise (ValueError(f"k = {k} must be an odd integer."))
