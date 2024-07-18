"""
-----------------------------------------------------------------------------------------
region module
-----------------------------------------------------------------------------------------
Provides region based segmentation algorithms. 
"""

import numpy as np
import cv2 as cv


def region_filling(
    img: np.ndarray, point: tuple, kernel: np.ndarray = None
) -> np.ndarray:
    """A simple region filling algorithm.

    Args:
        img (np.ndarray): Imput image.

        point (tuple): Starting point.

        kernel (np.ndarray, optional): Growing kernel.
        Defaults to None (Uses cross kernel).

    Returns:
        np.ndarray: Region filled image.
    """

    if kernel is None:  # Growing kernel (loading default)
        kernel = cv.getStructuringElement(cv.MORPH_CROSS, (3, 3))

    current = np.zeros_like(img)
    last = current
    last[point] = 1

    img = (img / img.max()).astype("uint8")

    noimg = np.where(img == 1, 0, 1).astype("uint8")

    current = cv.dilate(last, kernel, iterations=1) & noimg

    while (current != last).any():
        last = current
        current = cv.dilate(last, kernel, iterations=1) & noimg

    return current


def region_growing(
    img: np.ndarray,
    seed: tuple,
    percent: float,
    max_it: int = 100,
    kernel: np.ndarray = None,
) -> np.ndarray:
    """Simple region growing algorithm based on the percentage of the mean value of
    the contour pixels.

    Args:
        img (np.ndarray): Input image.

        seed (tuple): Seed.

        percent (float): Percentage threshold for the mean value.

        max_it (int): Maximum number of iteration
        Defaults to 100.

        kernel (np.ndarray, optional): Growing kernel.
        Defaults to None (Uses cross kernel).

    Returns:
        np.ndarray: Mask of the segmented image.
    """
    if kernel is not None:  # Growing kernel (loading default)
        kernel = cv.getStructuringElement(cv.MORPH_CROSS, (3, 3))

    # Initializations
    # Current Shape = seed
    current_shape = np.zeros_like(img)
    current_shape[seed] = 1

    mean_psi = img[seed]  # Value of the image at seed
    # upper and lower bound thresholds
    th = (
        np.max([0, mean_psi * (1 - percent)]).astype("uint8"),
        np.min([255, mean_psi * (1 + percent)]).astype("uint8"),
    )

    # First step
    next_shape = (
        cv.dilate(current_shape, kernel, iterations=1) - current_shape
    )  # It is just the new pixels

    selected_pxl = (img * next_shape).astype("uint8")
    selected_pxl = (selected_pxl >= th[0]) & (
        selected_pxl <= th[1]
    )  # Select those meeting criterion

    # Next steps
    i = 1
    # Stops when max iteration reached or no pixels to add
    while (selected_pxl.any()) and (i < max_it):
        # Update current shape
        current_shape = current_shape + selected_pxl.astype("uint8")

        # Determine the borders of current shape for threshold computation
        updateShape = current_shape - cv.erode(
            current_shape.astype("uint8"), kernel, iterations=1
        )

        # Update thresholds
        mean_psi = np.mean(img[updateShape == 1])
        th = (
            np.max([0, mean_psi * (1 - percent)]).astype("uint8"),
            np.min([255, mean_psi * (1 + percent)]).astype("uint8"),
        )

        # Determine next new pixels
        next_shape = (
            cv.dilate(current_shape.astype("uint8"), kernel, iterations=1)
            - current_shape
        )

        selected_pxl = (img * next_shape).astype("uint8")
        selected_pxl = (selected_pxl >= th[0]) & (
            selected_pxl <= th[1]
        )  # Select those meeting criterion

        i += 1  # counter ++

    if i == max_it:  # Warning to test more iterations
        print("Warning: Maximum iterations reached.")

    return current_shape
