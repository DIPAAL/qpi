"""Utility functions for rendering heatmaps."""
import io
import multiprocessing
from typing import List, Tuple

import numpy as np
import rasterio as rio
from matplotlib import colors
from rasterio import MemoryFile
from rasterio.plot import show
import matplotlib.pyplot as plt
from PIL import Image
import imageio.v2 as imageio

from app.routers.v1.heatmap.schemas.multi_output_format import MultiOutputFormat

satellite = rio.open("qpi/run/references/danish_waters_3034.tiff")
dipaal_logo = Image.open("qpi/run/references/dipaal.png")
daisy_logo = Image.open("qpi/run/references/daisy.png")
aau_logo = Image.open("qpi/run/references/aau.png")

fig_size = (17, 10)
dpi = 100

fig_width = fig_size[0] * dpi
fig_height = fig_size[1] * dpi

# Resize the logos to max 30% if the width or 20% of the height, except DIPAAL which is 30% of the height
aau_logo.thumbnail((fig_width * 0.3, fig_height * 0.2), Image.LANCZOS)
aau_logo = np.asarray(aau_logo)
daisy_logo.thumbnail((fig_width * 0.3, fig_height * 0.2), Image.LANCZOS)
daisy_logo = np.asarray(daisy_logo)
dipaal_logo.thumbnail((fig_width * 0.3, fig_height * 0.3), Image.LANCZOS)
dipaal_logo = np.asarray(dipaal_logo)


def geo_tiff_to_imageio(geo_tiff_bytes: io.BytesIO, title, max_value):
    """Wrap around creating PNG and loading into ImageIO. Used to multiprocess the creation of PNGs."""
    return imageio.imread(geo_tiff_to_png(geo_tiff_bytes, title=title, max=max_value))


def geo_tiffs_to_video(rasters: List[Tuple[str, io.BytesIO]], fps, format: str, max_value: float = None):
    """
    Create a video from a list of GeoTIFFs.

    Keyword arguments:
        rasters: list of tuples of (title, GeoTIFF bytes)
        fps: frames per second
        format: output format
        max_value: max value for the heatmap
    """
    with multiprocessing.Pool() as pool:
        frames = pool.starmap(geo_tiff_to_imageio, [(raster, title, max_value) for title, raster in rasters])

    frames = np.array(frames)

    # Save the frames to a buffer
    buffer = io.BytesIO()

    if format == MultiOutputFormat.gif:
        duration = 1 / fps
        imageio.mimsave(buffer, frames, duration=duration, format='gif')
    else:
        imageio.mimsave(buffer, frames, fps=fps, format=format)

    buffer.seek(0)

    return buffer


def geo_tiff_to_png(geo_tiff_bytes: io.BytesIO, can_be_negative=False, title=None, max=None) -> io.BytesIO:
    """Convert a GeoTIFF to a PNG."""
    norm = colors.LogNorm(clip=True, vmin=1, vmax=max)
    if can_be_negative:
        norm = colors.SymLogNorm(1)

    with MemoryFile(geo_tiff_bytes) as memfile:
        with memfile.open() as raster:
            fig, ax = plt.subplots(figsize=fig_size)
            show(
                satellite,
                ax=ax,
                origin='upper', )

            # use a logarithmic colormap to show raster
            plot = show(
                raster,
                ax=ax, cmap='turbo',
                norm=norm,
                interpolation='none',
            )

            im = plot.get_images()[1]

            vmin, vmax = im.get_clim()

            if vmin == vmax:
                raise ValueError("Cannot render a heatmap where vmin == vmax.")

            fig.colorbar(im, ax=ax, orientation='horizontal', pad=0.06, shrink=0.5)

            ax.set_ylim(ax.get_ylim()[::-1])

            fig.figimage(aau_logo, 10, 10, zorder=3, alpha=1)

            im_height, im_width = dipaal_logo.shape[0:2]
            fig.figimage(dipaal_logo, 10, fig_height - im_height - 10, zorder=3, alpha=1, origin='upper')

            im_height, im_width = daisy_logo.shape[0:2]
            fig.figimage(daisy_logo, fig_width - im_width - 10, 10, zorder=3, alpha=1)

            if title:
                fig.suptitle(title, fontsize=16)

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=dpi)
            buffer.seek(0)

            plt.close(fig)
            return buffer
