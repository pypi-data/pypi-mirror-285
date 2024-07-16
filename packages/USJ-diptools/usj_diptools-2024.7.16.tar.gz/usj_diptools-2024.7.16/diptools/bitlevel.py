"""
-----------------------------------------------------------------------------------------
bitlevel module
-----------------------------------------------------------------------------------------
Provides functions for exploring bit-level representations of images. 
"""

import numpy as np


def bit_quantization(img: np.ndarray, num_bits: int = 8) -> np.ndarray:
    """Simulates the effect of bit-quantization on an image.

    Args:
        img (np.ndarray): Imput image.

        num_bits (int, optional): Number of bits to simulate quantization.
        Defaults to 8.

    Returns:
        np.ndarray: Output image.
    """
    return ((img >> (8 - num_bits)) / (2**num_bits)) * (2**8 - 1)


def bit_plane(img: np.ndarray, bit: int = 8) -> np.ndarray:
    """Get the nth bit plane.

    Args:
        img (np.ndarray): Imput image.

        bit (int, optional): Bit plane to obtain.
        Defaults to 8.

    Returns:
        np.ndarray: Output image.
    """
    return ((img >> bit) % 2) * (2**8 - 1)
