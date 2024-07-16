"""
-----------------------------------------------------------------------------------------
pointprocessing module
-----------------------------------------------------------------------------------------
Provides point processing functionality. 
"""

import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv


def plot_transformation(
    x: np.ndarray,
    y: np.ndarray,
    fig_title: str = "Transformation",
    save_figure: bool = False,
    save_name: str = "Figure.jpg",
    save_format: str = "jpg",
) -> None:
    """Visualizes pixel transformation curves.

    Args:
        x (np.ndarray): Input intensity values.

        y (np.ndarray): Output intensity values.

        fig_title (str, optional): Figure title.
        Defaults to "Transformation".

        save_figure (bool, optional): To save figure.
        Defaults to False.

        save_name (str, optional): File name.
        Defaults to "Figure.jpg".

        save_format (str, optional): File extension.
        Defaults to "jpg".
    """

    fig = plt.figure(figsize=(5, 5))
    ax = fig.gca()

    ax.plot(x, y)
    ax.set_xticks([0, 128, 255])
    ax.set_yticks([0, 128, 255])
    ax.set_xlim((0, 256))
    ax.set_ylim((0, 256))

    ax.set_xlabel("input intensity", fontsize="x-large")
    ax.set_ylabel("output intensity", fontsize="x-large")
    ax.tick_params(axis="both", labelsize="x-large")  # Increase size of tick labels

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_title(fig_title, fontsize="xx-large")

    plt.show()

    if save_figure:
        fig.savefig(save_name, dpi=300, format=save_format, bbox_inches="tight")


def linear_norm(img: np.ndarray, v_min: int = 0, v_max: int = 255) -> np.ndarray:
    """Normalize an image.

    Args:
        img (np.ndarray): Imput image.

        v_min (int, optional): Minimum intensity value.
        Defaults to 0.

        v_max (int, optional): Maximum intensity value.
        Defaults to 255.

    Returns:
        np.ndarray: Normalized image.
    """

    return np.round(
        (img - img.min()) * ((v_max - v_min) / (img.max() - img.min())) + v_min
    )


def intensity_clamp(img: np.ndarray, v_min: int = 0, v_max: int = 255) -> np.ndarray:
    """Limits the output values of an image.

    Args:
        img (np.ndarray): Input image.

        v_min (int, optional): Minimum allowed intensity level.
        Defaults to 0.

        v_max (int, optional): Maximum allowed intensity level.
        Defaults to 255.

    Returns:
        np.ndarray: Output image.
    """
    img_c = img.copy()
    img_c[img_c < v_min] = v_min
    img_c[img_c > v_max] = v_max

    return img_c


def unsharp_masking(
    img: np.ndarray, weight: float, size: int = 3, radius: int = 1
) -> np.ndarray:
    """Unsharp masking using a gaussian kernel

    Args:
        img (np.ndarray): Input image.

        weight (int): Weight of the unsharp masking.

        size (int, optional): Size of the Gaussian kernel.
        Defaults to 3.

        radius (int, optional): Radius of the Gaussian kernel.
        Defaults to 1.

    Returns:
        np.ndarray: Unsharp maskied image.
    """

    return cv.addWeighted(
        img, 1, cv.GaussianBlur(img, (size, size), radius), -weight, 0
    )


def histogram_stretch_function(
    min_in: int,
    max_in: int,
    min_out: int,
    max_out: int,
    num: int = 2**8,
    range: tuple = (0, 2**8),
) -> np.ndarray:
    """Histogram stretch function.

    Args:
        a (int): Minimum input intensity.

        b (int): Maximum input intensity.

        c (int): Minimum output intensity.

        d (int): Maximum output intensity.

        num (int, optional): Number of intensity levels.
        Defaults to 2**8.

        range (tuple, optional): Range of intensity levels.
        Defaults to (0, 2**8).

    Returns:
        np.ndarray: Histogram stretch function.
    """
    input_intensity = np.linspace(range[0], range[1] - 1, num)
    output_intensity = np.concatenate(
        [
            min_in * np.ones_like(input_intensity[input_intensity < min_out]),
            np.linspace(
                min_in,
                max_in,
                np.sum((input_intensity >= min_out) & (input_intensity <= max_out)),
            ),
            max_in * np.ones_like(input_intensity[input_intensity > max_out]),
        ]
    )

    return output_intensity.astype("uint8")


def gamma_correction_function(
    gamma: float, k: int = 1, bit_depth: int = 8
) -> np.ndarray:
    """Returns the gamma correction function.

    Args:
        gamma (float): Gamma value.

        k (int, optional): Scale factor.
        Defaults to 1.

        bit (int, optional): Bit depth.
        Defaults to 8.

    Returns:
        np.ndarray: Gamma correction function.
    """
    return (
        k
        * np.power(
            np.linspace(0, 2**bit_depth - 1, 2**bit_depth) / (2**bit_depth - 1), gamma
        )
        * (2**bit_depth - 1)
    )


def log_function(i_max: int, bit: int = 8) -> np.ndarray:
    """Returns the log correction function.

    Args:
        i_max (int): Maximum image intensity.

        bit (int, optional): Bit depth.
        Defaults to 8.

    Returns:
        np.ndarray: Log correction function.
    """
    k = (2**bit - 1) / np.log(1 + i_max)
    return k * np.log(1 + np.linspace(0, 2**bit - 1, 2**bit))


def inv_log_function(i_max: int, bit: int = 8) -> np.ndarray:
    """Returns the inverse log correction funciton.

    Args:
        i_max (int): Maximum image intensity.

        bit (int, optional): Bit depth.
        Defaults to 8.

    Returns:
        np.ndarray: Inverse log correction function.
    """
    k = (2**bit - 1) / np.log(1 + i_max)
    return np.exp(np.linspace(0, 2**bit - 1, 2**bit) / k) - 1
