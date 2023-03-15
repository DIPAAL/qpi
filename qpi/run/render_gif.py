"""Module to create GIFs/MP4s from rasters in the database."""

import io
import os
from time import perf_counter

import imageio.v2 as imageio
import numpy as np
import rasterio as rio
from matplotlib import colors
from rasterio.plot import show
import matplotlib.pyplot as plt
from PIL import Image

from qpi.helper_functions import get_connection

plot_name = "Class B"

conn = get_connection()

query = """
WITH reference (rast) AS (
    SELECT ST_AddBand(
        ST_MakeEmptyRaster (795, 455, 3600000, 3030000, 1000, 1000, 0, 0, 3034),
        '32BUI'::text,
        1,
        0
    ) AS rast
)
 SELECT
    sq1.year,
    sq1.month,
    sq1.day,
    ST_AsGDALRaster(
        ST_MapAlgebra(sq1.rast, reference.rast, '[rast1.val]+[rast2.val]', extenttype:='UNION'),
        'cog'
    ) AS raster
FROM reference,
     (SELECT
          dd.year as year,
          dd.month_of_year as month,
          dd.day_of_month as day,
          ST_Union(rast) as rast
      FROM fact_cell_heatmap fch
               JOIN dim_raster dr on fch.raster_id = dr.raster_id
               JOIN dim_date dd on fch.date_id = dd.date_id
               JOIN dim_ship_type dst on fch.ship_type_id = dst.ship_type_id
      WHERE fch.spatial_resolution = 1000
        AND fch.heatmap_type_id = 1
        AND dst.mobile_type = 'Class B'
        AND fch.temporal_resolution_sec = 86400
      GROUP BY dd.year, dd.month_of_year, dd.day_of_month) sq1;
"""

# if temp_results folder is empty besides .gitignore
if len(os.listdir("qpi/run/temp_results")) == 1:
    print("temp_results is empty, creating files")
    start = perf_counter()
    cur = conn.cursor()
    cur.execute(query)

    # fetch the returned COG geotiff
    geotiff_bin = cur.fetchall()

    end = perf_counter()

    print(f"Query took {end - start} seconds")

    # save the geotiffs to files
    for year, month, day, geotiff in geotiff_bin:
        with open(f"qpi/run/temp_results/{year}_{str(month).zfill(2)}_{str(day).zfill(2)}.tiff", "wb") as f:
            f.write(geotiff)

files = [os.path.join("qpi/run/temp_results", f) for f in os.listdir("qpi/run/temp_results") if f.endswith(".tiff")]
files.sort()

sattelite = rio.open("qpi/run/references/danish_waters_3034.tiff")
dipaal_logo = Image.open("qpi/run/references/dipaal.png")
daisy_logo = Image.open("qpi/run/references/daisy.png")
aau_logo = Image.open("qpi/run/references/aau.png")

fig_size = (17, 10)
dpi = 100

fig_width = fig_size[0] * dpi
fig_height = fig_size[1] * dpi

# resize the logos to 30% of the figure's width, but keep aspect ratio
aau_logo.thumbnail((fig_width*0.3, fig_height*0.2), Image.LANCZOS)
aau_logo = np.asarray(aau_logo)
daisy_logo.thumbnail((fig_width*0.3, fig_height*0.2), Image.LANCZOS)
daisy_logo = np.asarray(daisy_logo)
dipaal_logo.thumbnail((fig_width*0.3, fig_height*0.3), Image.LANCZOS)
dipaal_logo = np.asarray(dipaal_logo)


def make_frame(f: str) -> io.BytesIO:
    """
    Create a PNG frame for a given file.

    Keyword arguments:
        f: the path to the raster file to create a frame for

    Returns:
        a BytesIO object containing the PNG frame
    """
    with rio.open(f) as raster:
        fig, ax = plt.subplots(figsize=fig_size)
        show(
            sattelite,
            ax=ax,
            origin='upper',)

        # use a logarithmic colormap to show raster
        retted = show(
            raster,
            ax=ax, cmap='turbo',
            norm=colors.LogNorm(clip=True),
            interpolation='none',
        )

        im = retted.get_images()[1]
        fig.colorbar(im, ax=ax, orientation='horizontal', pad=0.06, shrink=0.5)

        ax.set_ylim(ax.get_ylim()[::-1])

        file_name = f.split("/")[-1].split(".")[0]
        title = f"{plot_name} "+" ".join(file_name.split("_"))
        ax.set_title(title, fontsize=40)

        fig.figimage(aau_logo, 10, 10, zorder=3, alpha=1)

        im_height, im_width = dipaal_logo.shape[0:2]
        fig.figimage(dipaal_logo, 10, fig_height-im_height-10, zorder=3, alpha=1, origin='upper')

        im_height, im_width = daisy_logo.shape[0:2]
        fig.figimage(daisy_logo, fig_width-im_width-10, 10, zorder=3, alpha=1)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=dpi)
        buffer.seek(0)

        plt.close(fig)
        return buffer


frames = [imageio.imread(make_frame(f)) for f in files]
frames = np.array(frames)
imageio.mimsave(f'2021_daily_{plot_name}.mp4', frames, fps=4)
