"""Utility functions for rendering heatmaps."""
import io
import multiprocessing
from mpl_toolkits.axes_grid1 import make_axes_locatable
from typing import List, Tuple

import numpy as np
import rasterio as rio
from matplotlib import colors
from rasterio import MemoryFile
from rasterio.plot import show
import matplotlib.pyplot as plt
from PIL import Image
import imageio.v2 as imageio

from app.schemas.multi_output_format import MultiOutputFormat

satellite = rio.open("qpi/run/references/danish_waters_3034.tiff")


def geo_tiff_to_imageio(geo_tiff_bytes: io.BytesIO, title: str, max_value: float):
    """
    Wrap around creating PNG and loading into ImageIO. Used to multiprocess the creation of PNGs.

    Keyword arguments:
        geo_tiff_bytes: Binary representation of the GeoTIFF
        title: title which should be shown on the image
        max_value: max value for the heatmap, used for aligning the color scale.
    """
    return imageio.imread(geo_tiff_to_png(geo_tiff_bytes, title=title, max_value=max_value))


def geo_tiffs_to_video(
        rasters: List[Tuple[str, io.BytesIO]],
        fps: int,
        format: str,
        title_prefix: str,
        max_value: float = None
) -> io.BytesIO:
    """
    Create a video from a list of GeoTIFFs.

    Keyword arguments:
        rasters: list of tuples of (title, GeoTIFF bytes)
        fps: frames per second
        format: output format
        title_prefix: prefix for the title of each frame
        max_value: max value for the heatmap
    """
    with multiprocessing.Pool() as pool:
        frames = pool.starmap(
            geo_tiff_to_imageio,
            [(raster, f"{title_prefix} - {title}", max_value) for title, raster in rasters]
        )

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


def geo_tiff_to_png(
        geo_tiff_bytes: io.BytesIO,
        can_be_negative: bool = False,
        title: str = None,
        max_value: float = None
) -> io.BytesIO:
    """
    Convert a GeoTIFF to a PNG.

    Keyword arguments:
        geo_tiff_bytes: binary representation of the GeoTIFF
        can_be_negative: whether the geotiff can be negative, i.e. whether a colormap should support negative values.
        title: title which should be shown on the image
        max_value: max value for the heatmap, used for aligning the color scale.
    """
    norm = colors.LogNorm(clip=True, vmin=1, vmax=max_value)
    if can_be_negative:
        norm = colors.SymLogNorm(1)

    with MemoryFile(geo_tiff_bytes) as memfile:
        with memfile.open() as raster:
            fig, ax = plt.subplots(dpi=200, layout='tight')

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

            # invert y axis
            ax.set_ylim(ax.get_ylim()[::-1])

            if title:
                plt.title(title)

            # get size of im in pixels
            fig_height, fig_width = im.get_size()
            is_wider = fig_width > fig_height
            fig.set_size_inches(fig_width / 100 + (0 if is_wider else 1), fig_height / 100 + (1 if is_wider else 0))

            # the colorbar should only be as wide as the image on ax
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("bottom" if is_wider else "right", size="5%", pad=0.4)

            # add colorbar
            fig.colorbar(im, cax=cax, orientation='horizontal' if is_wider else 'vertical')

            fig.canvas.draw()

            image = Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb())

            plt.close(fig)

            # add logos by first adding max(10% of the height or 200px) to the bottom of the image
            height_to_add = int(max(image.height * 0.1, 100))

            # extend the image with the height to add and a white background
            image = image.crop((0, 0, image.width, image.height + height_to_add))
            image.paste(
                Image.new(
                    'RGB',
                    (image.width, height_to_add),
                    (255, 255, 255)
                ),
                (0, image.height - height_to_add)
            )

            dipaal_logo = Image.open("qpi/run/references/dipaal.png")
            daisy_logo = Image.open("qpi/run/references/daisy.png")
            aau_logo = Image.open("qpi/run/references/aau.png")
            aau_logo.thumbnail((image.width//3, height_to_add), Image.LANCZOS)
            daisy_logo.thumbnail((image.width//3, height_to_add), Image.LANCZOS)
            dipaal_logo.thumbnail((image.width//3, height_to_add), Image.LANCZOS)

            # Add logos to the image, with AAU logo on the left, daisy on the right, and dipaal in the center
            image.paste(
                aau_logo,
                (10, image.height - height_to_add//2 - aau_logo.height//2-10),
                aau_logo
            )
            image.paste(
                daisy_logo,
                (image.width - daisy_logo.width-10, image.height - height_to_add//2 - daisy_logo.height//2-10),
                daisy_logo
            )
            image.paste(
                dipaal_logo,
                (image.width//2 - dipaal_logo.width//2, image.height - height_to_add//2 - dipaal_logo.height//2 - 10),
                dipaal_logo
            )

            buffer = io.BytesIO()
            image.save(buffer, format='png')
            buffer.seek(0)

            return buffer
