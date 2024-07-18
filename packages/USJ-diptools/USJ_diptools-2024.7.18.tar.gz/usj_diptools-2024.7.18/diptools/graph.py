"""
-----------------------------------------------------------------------------------------
graph module
-----------------------------------------------------------------------------------------
Provides functionality to easily visualise images. 
"""

from collections import namedtuple
from typing import Tuple
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv


def show_image(
    img: np.ndarray,
    cmap: str = "gist_gray",
    converted: bool = True,
    normalize: bool = False,
    fig_size: tuple = (10, 20),
    fig_title: str = None,
    show_ticks: bool = False,
    x_tick: list = None,
    x_tick_labels: list = None,
    x_ticks_steps: int = 5,
    y_tick: list = None,
    y_tick_labels: list = None,
    y_ticks_steps: int = 5,
    save_figure: bool = False,
    save_name: str = "Figure.jpg",
    save_format: str = "jpg",
) -> None:
    """Show images.

    Args:
        img (np.ndarray): Image to view.

        cmap (str, optional): Colour map for the image to be displayed.
        Defaults to "gist_gray".

        converted (bool, optional): Whether an image has already been converted
        to greyscale, otherwise it will use the Open-CV API to convert it.
        Defaults to True.

        normalize (bool, optional): Whether or not to normalize an image.
        Defaults to False.

        fig_size (str, optional): Figure size in inches.
        Defaults to (10, 20).

        fig_title (str, optional): Figure title.
        Defaults to None.

        show_ticks (bool, optional): To display the x and y axis tick labels.
        Defaults to False.

        x_tick (list, optional): Values for the x-ticks when show_ticks = True.
        Defaults to None (handled by MatPlotLib).

        x_tick_labels (list, optional): Labels for the x-ticks when show_ticks = True.
        Defaults to None (handled by MatPlotLib).

        x_ticks_steps (int, optional): Steps to show x-ticks when show_ticks = True.
        Defaults to 5.

        y_tick (list, optional): Values for the y-ticks when show_ticks = True.
        Defaults to None (handled by MatPlotLib).

        y_tick_labels (list, optional): Labels for the y-ticks when show_ticks = True.
        Defaults to None (handled by MatPlotLib).

        y_ticks_steps (int, optional): Steps to show the y-ticks when show_ticks = True
        Defaults to 5.

        save_figure (bool, optional): To save the figure.
        Defaults to False.

        save_name (str, optional): Name of the output file.
        Defaults to "Figure.jpg".

        save_format (str, optional): Format of the output file.
        Defaults to "jpg".
    """

    fig = plt.figure(figsize=fig_size)
    ax = fig.gca()

    if not converted:
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    if normalize:
        plt.imshow(img, cmap)
    else:
        plt.imshow(
            img, cmap, vmin=0, vmax=255
        )  # This is to avoid automatic normalization

    if show_ticks:
        x_tick = np.linspace(0, img.shape[1] - 1, x_ticks_steps, dtype=int)
        ax.set_xticks(x_tick)
        ax.set_xticklabels(
            np.linspace(0, img.shape[1] - 1, x_ticks_steps, dtype=int)
        )
        
        if x_tick is not None:  # Set the x-axis ticks
            ax.set_xticks(x_tick)
            if x_tick_labels is not None:
                ax.set_xticklabels(x_tick_labels)

        y_tick = np.linspace(0, img.shape[0] - 1, y_ticks_steps, dtype=int)
        ax.set_yticks(y_tick)
        ax.set_yticklabels(
            np.linspace(0, img.shape[0] - 1, y_ticks_steps, dtype=int)
        )
        if y_tick is not None:  # Set the y-axis ticks
            ax.set_yticks(y_tick)
            if y_tick_labels is not None:
                ax.set_yticklabels(y_tick_labels)
    else:
        ax.axis("off")

    if fig_title is not None:
        ax.set_title(fig_title)

    plt.show()

    if save_figure:
        fig.savefig(save_name, dpi=300, format=save_format, bbox_inches="tight")


def show_histogram(
    img: np.ndarray,
    total_range: tuple = (0, 2**8),
    num_bins: int = 2**8,
    ret_hist: bool = False,
    calc_cdf: bool = False,
    x_lim: tuple = None,
    y_lim: tuple = None,
    cmap: str = "gist_gray",
    save_figure: bool = False,
    save_name: str = "Figure.png",
    save_format: str = "png",
) -> Tuple[np.ndarray, np.ndarray]:
    """Calculates and displays the histogram and CDF of an image.

    Args:
        img (np.ndarray): Input image.

        total_range (tuple, optional): Image dynamic range.
        Defaults to (0, 2**8).

        num_bins (int, optional): Number of bins for the histogram.
        Defaults to 2**8.

        ret_hist (bool, optional): Return the histogram.
        Defaults to False.

        calc_cdf (bool, optional): Calculates, visualizes and return the CDF.
        Defaults to False.

        x_lim (tuple, optional): Minimum and maximum value of the x-axis.
        Defaults to None (handled by MatPlotLib).

        y_lim (tuple, optional): Minimum and maximum value of the y-axis.
        Defaults to None (handled by MatPlotLib).

        cmap (str, optional): Colour map.
        Defaults to "gist_gray".

        save_figure (bool, optional): To save the figure.
        Defaults to False.

        save_name (str, optional): Name of the output file.
        Defaults to "Figure.jpg".

        save_format (str, optional): Format of the output file.
        Defaults to "jpg".

    Returns:
        Tuple[np.ndarray,np.ndarray]:
            histogram: Histogram of the image (only when ret_hist = True or calc_cdf = True)

            cdf: CDF of the image (only when calc_cdf = True)
    """

    histogram = cv.calcHist([img], [0], None, [num_bins], total_range)

    fig, ax = plt.subplots(2, 1, figsize=(10, 10))

    ax[0].bar(
        np.linspace(total_range[0], total_range[1] - 1, num_bins),
        histogram.flatten().astype("int"),
        width=1,
        color="k",
        label="Histogram",
    )

    if x_lim is not None:
        ax[0].set_xlim(x_lim)
        ax[0].set_xticks(
            [
                max(min(x_lim), 0),
                min((x_lim[1] - x_lim[0]) // 2, 128),
                min(max(x_lim), 255),
            ]
        )
    else:
        ax[0].set_xlim((total_range[0] - 1, total_range[1]))
        ax[0].set_xticks([0, 128, 255])

    if y_lim is not None:
        ax[0].set_ylim(y_lim)

    ax[0].set_title("Histogram", fontsize="x-large")
    ax[0].set_ylabel("Pixel Counts", fontsize="x-large")
    ax[0].tick_params(axis="both", labelsize="x-large")  # Increase size of tick labels

    if calc_cdf:
        cdf = np.cumsum(
            histogram.flatten().astype("int") / np.sum(histogram).astype("int")
        )

        ax2 = ax[0].twinx()  # clone the object

        ax2.plot(np.arange(0, 2**8), cdf, c="r", label="CDF")
        ax2.set_ylabel("Probability", fontsize="x-large")
        ax2.set_ylim((0, 1.01))

        lines, labels = ax[0].get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()

        ax2.legend(
            lines + lines2, labels + labels2, loc="upper left", fontsize="x-large"
        )
        ax2.tick_params(axis="y", labelsize="x-large")  # Increase size of tick labels

    # This is to show the Cmap
    ax[1].imshow(np.tile(np.arange(num_bins), (10, 1)), cmap=cmap)
    ax[1].set_xlim((-1, 256))
    box = ax[1].get_position()
    box.y0 = box.y0 + 0.19
    box.y1 = box.y1 + 0.19
    ax[1].set_position(box)
    ax[1].set_xticks([])
    ax[1].yaxis.set_visible(False)
    ax[1].set_xlabel("Intensity", fontsize="x-large")

    if save_figure:  # Saves the figure
        fig.savefig(save_name, dpi=300, format=save_format, bbox_inches="tight")

    plt.show()

    if calc_cdf and ret_hist:
        HistogramResult = namedtuple("HistogramResult", "histogram cdf")
        return HistogramResult(histogram.flatten(), cdf)
    elif ret_hist:
        HistogramResult = namedtuple("HistogramResult", "histogram")
        return HistogramResult(histogram.flatten())
